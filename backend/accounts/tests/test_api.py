from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Profile

User = get_user_model()

REGISTER_URL = reverse("accounts:register")
LOGIN_URL = reverse("accounts:login")
LOGOUT_URL = reverse("accounts:logout")
ME_URL = reverse("accounts:me")
CSRF_URL = reverse("accounts:csrf")

PASSWORD = "example-password"


def register_payload(**overrides):
    payload = {
        "username": "player_one",
        "email": "player@example.com",
        "nickname": "MountainKnight",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }
    payload.update(overrides)
    return payload


def create_player(username="existing", email="existing@example.com", nickname="ExistingKnight"):
    user = User.objects.create_user(username=username, email=email, password=PASSWORD)
    Profile.objects.create(user=user, nickname=nickname)
    return user


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_successful_registration(self):
        response = self.client.post(REGISTER_URL, register_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="player_one")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(user.profile.nickname, "MountainKnight")
        self.assertEqual(user.profile.avatar_key, Profile.KNIGHT_1)

        self.assertEqual(
            response.json(),
            {
                "id": user.id,
                "username": "player_one",
                "email": "player@example.com",
                "profile": {"nickname": "MountainKnight", "avatar_key": Profile.KNIGHT_1},
            },
        )

    def test_invalid_registration(self):
        create_player()
        cases = [
            ("username taken", register_payload(username="existing"), "username"),
            ("email taken", register_payload(email="existing@example.com"), "email"),
            ("nickname taken", register_payload(nickname="ExistingKnight"), "nickname"),
            (
                "passwords differ",
                register_payload(password_confirm="other-password"),
                "password_confirm",
            ),
        ]

        for label, payload, expected_field in cases:
            with self.subTest(case=label):
                response = self.client.post(REGISTER_URL, payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(expected_field, response.json()["errors"])
                self.assertEqual(User.objects.count(), 1)


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_player(
            username="player_one", email="player@example.com", nickname="MountainKnight"
        )

    def test_successful_login_starts_a_session(self):
        response = self.client.post(
            LOGIN_URL, {"username": "player_one", "password": PASSWORD}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "player_one")

        me = self.client.get(ME_URL)
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.json()["id"], self.user.id)

    def test_wrong_password_is_rejected(self):
        response = self.client.post(
            LOGIN_URL, {"username": "player_one", "password": "wrong-password"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.json())

        me = self.client.get(ME_URL)
        self.assertIn(
            me.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )


class MePermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_player(
            username="player_one", email="player@example.com", nickname="MountainKnight"
        )
        self.other = create_player(
            username="player_two", email="other@example.com", nickname="RiverKnight"
        )

    def test_anonymous_access_is_denied(self):
        response = self.client.get(ME_URL)

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_authenticated_user_sees_only_own_data(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.user.id)
        self.assertEqual(response.json()["profile"]["nickname"], "MountainKnight")


class ProfileUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_player(
            username="player_one", email="player@example.com", nickname="MountainKnight"
        )
        self.client.force_authenticate(self.user)

    def test_nickname_and_avatar_are_updated(self):
        response = self.client.patch(
            ME_URL, {"nickname": "NewKnight", "avatar_key": Profile.KNIGHT_3}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["profile"],
            {"nickname": "NewKnight", "avatar_key": Profile.KNIGHT_3},
        )

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.nickname, "NewKnight")
        self.assertEqual(self.user.profile.avatar_key, Profile.KNIGHT_3)

    def test_protected_fields_are_ignored(self):
        response = self.client.patch(
            ME_URL,
            {"nickname": "NewKnight", "is_staff": True, "username": "hacker"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertEqual(self.user.username, "player_one")


class LogoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_player(
            username="player_one", email="player@example.com", nickname="MountainKnight"
        )

    def test_logout_ends_the_session(self):
        self.client.post(
            LOGIN_URL, {"username": "player_one", "password": PASSWORD}, format="json"
        )

        response = self.client.post(LOGOUT_URL)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        me = self.client.get(ME_URL)
        self.assertIn(
            me.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

    def test_anonymous_logout_is_denied(self):
        response = self.client.post(LOGOUT_URL)

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )


class CsrfTests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = create_player(
            username="player_one", email="player@example.com", nickname="MountainKnight"
        )

    def csrf_token(self):
        response = self.client.get(CSRF_URL)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        return self.client.cookies["csrftoken"].value

    def test_unsafe_request_without_token_is_forbidden(self):
        self.client.force_login(self.user)

        response = self.client.patch(ME_URL, {"nickname": "NewKnight"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.nickname, "MountainKnight")

    def test_same_request_succeeds_with_token(self):
        self.client.force_login(self.user)
        token = self.csrf_token()

        response = self.client.patch(
            ME_URL,
            {"nickname": "NewKnight"},
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.nickname, "NewKnight")
