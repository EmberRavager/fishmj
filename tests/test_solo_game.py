import unittest

from src.game import MahjongGame


class SoloGameTest(unittest.TestCase):
    def test_start_round_deals_cards(self):
        game = MahjongGame("Tester", seed=42)
        game.start_round()
        self.assertEqual(len(game.players), 4)
        self.assertTrue(all(len(p.hand) == 13 for p in game.players))
        self.assertEqual(len(game.wall), 52)

    def test_draw_and_discard(self):
        game = MahjongGame("Tester", seed=1)
        game.start_round()
        tile = game.draw_for_current()
        self.assertIsNotNone(tile)
        self.assertEqual(len(game.players[0].hand), 14)
        dropped = game.discard_tile(0, 0)
        self.assertEqual(len(game.players[0].hand), 13)
        self.assertIn(dropped, game.players[0].discards)


if __name__ == "__main__":
    unittest.main()
