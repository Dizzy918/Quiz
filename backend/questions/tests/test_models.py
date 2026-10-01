from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


def add_options(question, correct_count=1, total=4):
    for index in range(total):
        AnswerOption.objects.create(
            question=question,
            text=f"Отговор {index + 1}",
            is_correct=index < correct_count,
        )


class CategoryTests(TestCase):
    def test_name_is_unique(self):
        Category.objects.create(name="География")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name="География")

    def test_category_with_questions_cannot_be_deleted(self):
        category = Category.objects.create(name="История")
        NumericQuestion.objects.create(
            category=category, text="През коя година?", correct_answer=1945
        )

        with self.assertRaises(ProtectedError):
            category.delete()

        self.assertEqual(Category.objects.count(), 1)


class ChoiceQuestionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="География")

    def create_question(self):
        return ChoiceQuestion.objects.create(
            category=self.category, text="Коя е столицата на Австралия?"
        )

    def test_valid_choice_question(self):
        question = self.create_question()
        add_options(question)

        question.full_clean()

        self.assertEqual(question.options.count(), 4)
        self.assertEqual(question.options.filter(is_correct=True).count(), 1)
        self.assertEqual(list(self.category.choicequestions.all()), [question])

    def test_invalid_option_sets_are_rejected(self):
        cases = [
            ("three options", {"total": 3, "correct_count": 1}),
            ("five options", {"total": 5, "correct_count": 1}),
            ("no correct option", {"total": 4, "correct_count": 0}),
            ("two correct options", {"total": 4, "correct_count": 2}),
        ]

        for label, kwargs in cases:
            with self.subTest(case=label):
                question = self.create_question()
                add_options(question, **kwargs)

                with self.assertRaises(ValidationError):
                    question.full_clean()

                question.delete()

    def test_deleting_question_deletes_its_options(self):
        question = self.create_question()
        add_options(question)

        question.delete()

        self.assertEqual(AnswerOption.objects.count(), 0)


class NumericQuestionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Наука")

    def test_valid_numeric_question(self):
        question = NumericQuestion.objects.create(
            category=self.category,
            text="Колко хромозоми има една човешка телесна клетка?",
            correct_answer=46,
        )

        question.full_clean()

        self.assertEqual(question.correct_answer, 46)
        self.assertEqual(list(self.category.numericquestions.all()), [question])

    def test_correct_answer_is_required(self):
        question = NumericQuestion(category=self.category, text="Колко?")

        with self.assertRaises(ValidationError) as context:
            question.full_clean()

        self.assertIn("correct_answer", context.exception.message_dict)
