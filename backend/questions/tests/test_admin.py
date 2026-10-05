from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from questions.models import Category, ChoiceQuestion

ADD_URL = reverse("admin:questions_choicequestion_add")


def post_data(category, options):
    """Admin add-form payload for a choice question and its inline options."""
    data = {
        "category": category.pk,
        "text": "Коя е столицата на Австралия?",
        "options-TOTAL_FORMS": str(len(options)),
        "options-INITIAL_FORMS": "0",
        "options-MIN_NUM_FORMS": "4",
        "options-MAX_NUM_FORMS": "4",
    }
    for index, (text, is_correct) in enumerate(options):
        data[f"options-{index}-text"] = text
        data[f"options-{index}-id"] = ""
        data[f"options-{index}-question"] = ""
        if is_correct:
            data[f"options-{index}-is_correct"] = "on"
    return data


class ChoiceQuestionAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client.force_login(
            User.objects.create_superuser(
                username="editor", email="editor@example.com", password="example-password"
            )
        )
        self.category = Category.objects.create(name="География")

    def test_four_options_with_one_correct_are_saved(self):
        options = [("Сидни", False), ("Мелбърн", False), ("Канбера", True), ("Пърт", False)]

        response = self.client.post(ADD_URL, post_data(self.category, options))

        self.assertEqual(response.status_code, 302)
        question = ChoiceQuestion.objects.get()
        self.assertEqual(question.options.count(), 4)
        self.assertEqual(question.options.filter(is_correct=True).count(), 1)

    def test_admin_refuses_a_broken_set_of_options(self):
        cases = [
            (
                "two correct",
                [("Сидни", True), ("Мелбърн", False), ("Канбера", True), ("Пърт", False)],
            ),
            (
                "no correct",
                [("Сидни", False), ("Мелбърн", False), ("Канбера", False), ("Пърт", False)],
            ),
            ("three options", [("Сидни", False), ("Мелбърн", False), ("Канбера", True)]),
        ]

        for label, options in cases:
            with self.subTest(case=label):
                response = self.client.post(ADD_URL, post_data(self.category, options))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(ChoiceQuestion.objects.count(), 0)
