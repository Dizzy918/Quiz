from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from games.models import Game, GamePlayer, Round, RoundAnswer
from games.tests.factories import (
    create_choice_answer,
    create_choice_round,
    create_game,
    create_numeric_round,
    create_player,
    create_user,
)


class GameTests(TestCase):
    def test_new_game_starts_as_waiting(self):
        game = create_game()

        self.assertEqual(game.status, Game.WAITING)
        self.assertIsNotNone(game.created_at)
        self.assertIsNone(game.started_at)
        self.assertIsNone(game.finished_at)

    def test_creator_cannot_be_deleted_while_the_game_exists(self):
        host = create_user("host")
        create_game(created_by=host)

        with self.assertRaises(ProtectedError):
            host.delete()

    def test_deleting_a_game_removes_players_rounds_and_answers(self):
        game = create_game()
        player = create_player(game)
        round_ = create_choice_round(game)
        create_choice_answer(round_, player)

        game.delete()

        self.assertEqual(GamePlayer.objects.count(), 0)
        self.assertEqual(Round.objects.count(), 0)
        self.assertEqual(RoundAnswer.objects.count(), 0)


class GamePlayerTests(TestCase):
    def test_players_are_ordered_and_reachable_from_the_game(self):
        game = create_game()
        second = create_player(game, player_order=2)
        first = create_player(game, player_order=1)

        self.assertEqual(list(game.players.all()), [first, second])
        self.assertEqual(first.score, 0)
        self.assertTrue(first.is_active)

    def test_a_player_in_a_game_protects_the_user(self):
        game = create_game()
        user = create_user("competitor")
        create_player(game, user=user)

        with self.assertRaises(ProtectedError):
            user.delete()


class RoundTests(TestCase):
    def setUp(self):
        self.game = create_game()

    def test_choice_round_exposes_its_question(self):
        round_ = create_choice_round(self.game)

        round_.full_clean()

        self.assertEqual(round_.status, Round.PENDING)
        self.assertEqual(round_.question, round_.choice_question)
        self.assertIsNone(round_.numeric_question)

    def test_numeric_round_exposes_its_question(self):
        round_ = create_numeric_round(self.game)

        round_.full_clean()

        self.assertEqual(round_.question, round_.numeric_question)
        self.assertIsNone(round_.choice_question)

    def test_rounds_are_ordered_by_number(self):
        second = create_numeric_round(self.game, number=2)
        first = create_choice_round(self.game, number=1)

        self.assertEqual(list(self.game.rounds.all()), [first, second])

    def test_question_type_must_match_the_question(self):
        round_ = Round(
            game=self.game,
            number=1,
            question_type=Round.CHOICE,
            numeric_question=create_numeric_round(self.game, number=9).numeric_question,
        )

        with self.assertRaises(ValidationError) as context:
            round_.full_clean()

        self.assertIn("choice_question", context.exception.message_dict)

    def test_a_used_question_cannot_be_deleted(self):
        round_ = create_choice_round(self.game)

        with self.assertRaises(ProtectedError):
            round_.choice_question.delete()


class RoundAnswerTests(TestCase):
    def setUp(self):
        self.game = create_game()
        self.player = create_player(self.game)

    def test_choice_answer_defaults(self):
        round_ = create_choice_round(self.game)

        answer = create_choice_answer(round_, self.player)
        answer.full_clean()

        self.assertIsNone(answer.is_correct)
        self.assertEqual(answer.points_awarded, 0)
        self.assertIsNone(answer.numeric_value)
        self.assertEqual(list(round_.answers.all()), [answer])
        self.assertEqual(list(self.player.answers.all()), [answer])

    def test_numeric_answer_is_stored_as_a_value(self):
        round_ = create_numeric_round(self.game)

        answer = RoundAnswer.objects.create(
            round=round_, player=self.player, numeric_value=5
        )
        answer.full_clean()

        self.assertEqual(answer.numeric_value, 5)
        self.assertIsNone(answer.selected_option)

    def test_answer_kind_must_match_the_round(self):
        round_ = create_numeric_round(self.game)
        answer = RoundAnswer(round=round_, player=self.player, numeric_value=None)
        answer.selected_option = create_choice_round(
            self.game, number=2
        ).choice_question.options.first()

        with self.assertRaises(ValidationError) as context:
            answer.full_clean()

        self.assertIn("numeric_value", context.exception.message_dict)

    def test_player_must_belong_to_the_same_game(self):
        other_game = create_game(created_by=create_user("other-host"))
        outsider = create_player(other_game, user=create_user("outsider"))
        round_ = create_choice_round(self.game)

        answer = RoundAnswer(
            round=round_,
            player=outsider,
            selected_option=round_.choice_question.options.first(),
        )

        with self.assertRaises(ValidationError) as context:
            answer.full_clean()

        self.assertIn("player", context.exception.message_dict)

    def test_one_player_answers_across_several_rounds(self):
        first = create_choice_round(self.game, number=1)
        second = create_numeric_round(self.game, number=2)

        create_choice_answer(first, self.player)
        RoundAnswer.objects.create(round=second, player=self.player, numeric_value=5)

        self.assertEqual(self.player.answers.count(), 2)
