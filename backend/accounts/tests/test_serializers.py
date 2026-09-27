from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Profile
from accounts.serializers import (
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()

VALID_PAYLOAD = {
    "username": "player_one",
    "email": "player@example.com",
    "nickname": "MountainKnight",
    "password": "example-password",
    "password_confirm": "example-password",
}


class RegisterSerializerTests(TestCase):
    def test_creates_user_and_profile_together(self):
        serializer = RegisterSerializer(data=VALID_PAYLOAD)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertTrue(user.check_password("example-password"))
        self.assertEqual(user.profile.nickname, "MountainKnight")
        self.assertEqual(user.profile.avatar_key, Profile.KNIGHT_1)

    def test_mismatched_passwords_are_rejected(self):
        serializer = RegisterSerializer(
            data={**VALID_PAYLOAD, "password_confirm": "other-password"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_nothing_is_created_when_validation_fails(self):
        serializer = RegisterSerializer(
            data={**VALID_PAYLOAD, "password_confirm": "other-password"}
        )
        serializer.is_valid()

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)


class UserSerializerTests(TestCase):
    def test_never_exposes_password_data(self):
        user = User.objects.create_user(
            username="player_one",
            email="player@example.com",
            password="example-password",
        )
        Profile.objects.create(user=user, nickname="MountainKnight")

        data = UserSerializer(user).data

        self.assertEqual(set(data), {"id", "username", "email", "profile"})
        self.assertEqual(data["profile"], {
            "nickname": "MountainKnight",
            "avatar_key": Profile.KNIGHT_1,
        })


class ProfileUpdateSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="player_one",
            email="player@example.com",
            password="example-password",
        )
        self.profile = Profile.objects.create(user=self.user, nickname="MountainKnight")

    def test_keeping_own_nickname_is_allowed(self):
        serializer = ProfileUpdateSerializer(
            self.profile,
            data={"nickname": "MountainKnight", "avatar_key": Profile.KNIGHT_3},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_nickname_taken_by_another_profile_is_rejected(self):
        other = User.objects.create_user(
            username="player_two",
            email="other@example.com",
            password="example-password",
        )
        Profile.objects.create(user=other, nickname="RiverKnight")

        serializer = ProfileUpdateSerializer(
            self.profile, data={"nickname": "RiverKnight"}, partial=True
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("nickname", serializer.errors)
