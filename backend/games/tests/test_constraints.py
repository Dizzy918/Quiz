from django.db import IntegrityError, transaction
from django.test import TestCase

from games.models import GamePlayer, Round, RoundAnswer
from games.tests.factories import (
    create_choice_answer,
    create_choice_question,
    create_choice_round,
    create_game,
    create_numeric_question,
    create_numeric_round,
    create_player,
    create_user,
)


class GamePlayerConstraintTests(TestCase):
    def setUp(self):
        self.game = create_game()

    def test_a_user_joins_a_game_only_once(self):
        user = create_user("competitor")
        create_player(self.game, user=user, player_order=1)

        with self.assertRaises(IntegrityError), transaction.atomic():
            GamePlayer.objects.create(game=self.game, user=user, player_order=2)

    def test_player_order_is_unique_within_a_game(self):
        create_player(self.game, player_order=1)

        with self.assertRaises(IntegrityError), transaction.atomic():
            GamePlayer.objects.create(
                game=self.game, user=create_user("second"), player_order=1
            )

    def test_the_same_order_is_free_in_another_game(self):
        other = create_game(created_by=create_user("other-host"))
        create_player(self.game, player_order=1)

        create_player(other, user=create_user("second"), player_order=1)

        self.assertEqual(GamePlayer.objects.count(), 2)


class RoundConstraintTests(TestCase):
    def setUp(self):
        self.game = create_game()

    def test_round_number_is_unique_within_a_game(self):
        create_choice_round(self.game, number=1)

        with self.assertRaises(IntegrityError), transaction.atomic():
            create_numeric_round(self.game, number=1)

    def test_a_round_without_a_question_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Round.objects.create(
                game=self.game, number=1, question_type=Round.CHOICE
            )

    def test_a_round_with_two_questions_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Round.objects.create(
                game=self.game,
                number=1,
                question_type=Round.CHOICE,
                choice_question=create_choice_question(),
                numeric_question=create_numeric_question(),
            )

    def test_the_question_must_match_the_question_type(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Round.objects.create(
                game=self.game,
                number=1,
                question_type=Round.NUMERIC,
                choice_question=create_choice_question(),
            )


class RoundAnswerConstraintTests(TestCase):
    def setUp(self):
        self.game = create_game()
        self.player = create_player(self.game)
        self.round = create_choice_round(self.game)

    def test_a_player_answers_a_round_only_once(self):
        create_choice_answer(self.round, self.player)

        with self.assertRaises(IntegrityError), transaction.atomic():
            create_choice_answer(self.round, self.player)

    def test_an_empty_answer_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoundAnswer.objects.create(round=self.round, player=self.player)

    def test_an_answer_cannot_hold_both_values(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoundAnswer.objects.create(
                round=self.round,
                player=self.player,
                selected_option=self.round.choice_question.options.first(),
                numeric_value=5,
            )
