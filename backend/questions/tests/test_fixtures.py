from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


class QuestionBankFixtureTests(TestCase):
    fixtures = ["questions/question_bank.json"]

    def test_fixture_loads_the_expected_amount_of_data(self):
        self.assertEqual(Category.objects.count(), 6)
        self.assertEqual(ChoiceQuestion.objects.count(), 12)
        self.assertEqual(AnswerOption.objects.count(), 48)
        self.assertEqual(NumericQuestion.objects.count(), 12)

    def test_every_choice_question_is_well_formed(self):
        for question in ChoiceQuestion.objects.all():
            with self.subTest(question=question.text):
                options = list(question.options.all())
                self.assertEqual(len(options), 4)
                self.assertEqual(sum(1 for o in options if o.is_correct), 1)
                self.assertTrue(all(o.text.strip() for o in options))

    def test_every_numeric_question_has_an_answer(self):
        for question in NumericQuestion.objects.all():
            with self.subTest(question=question.text):
                self.assertIsInstance(question.correct_answer, int)

    def test_every_question_belongs_to_a_category(self):
        categories = set(Category.objects.values_list("id", flat=True))

        for question in [*ChoiceQuestion.objects.all(), *NumericQuestion.objects.all()]:
            with self.subTest(question=question.text):
                self.assertIn(question.category_id, categories)
