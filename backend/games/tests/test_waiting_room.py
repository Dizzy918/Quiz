from django.test import TestCase

from games.models import Game, GamePlayer, WaitingPlayer
from games.tests.factories import create_user


class WaitingRoomFormationTests(TestCase):
    def test_forming_game_with_five_waiting_creates_game_and_leaves_two(self):
        for index in range(1, 6):
            user = create_user(f"waiting_user_{index}")
            WaitingPlayer.objects.create(user=user)

        game = WaitingPlayer.try_form_game()

        self.assertIsNotNone(game)
        self.assertEqual(game.status, Game.WAITING)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(WaitingPlayer.objects.count(), 2)

        players = list(GamePlayer.objects.filter(game=game))
        self.assertEqual(len(players), 3)
        self.assertEqual(len({player.color for player in players}), 3)
        self.assertEqual([player.score for player in players], [0, 0, 0])

        selected_user_ids = {player.user_id for player in players}
        remaining_user_ids = set(
            WaitingPlayer.objects.values_list("user_id", flat=True)
        )
        self.assertTrue(selected_user_ids.isdisjoint(remaining_user_ids))

    def test_forming_game_with_two_waiting_makes_no_changes(self):
        for index in range(1, 3):
            user = create_user(f"waiting_user_{index}")
            WaitingPlayer.objects.create(user=user)

        game = WaitingPlayer.try_form_game()

        self.assertIsNone(game)
        self.assertEqual(Game.objects.count(), 0)
        self.assertEqual(GamePlayer.objects.count(), 0)
        self.assertEqual(WaitingPlayer.objects.count(), 2)