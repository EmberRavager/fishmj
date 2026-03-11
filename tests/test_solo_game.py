import unittest

from src.fishmj import SoloMahjongGame


class SoloGameTest(unittest.TestCase):
    def test_start_round_deals_cards(self):
        game = SoloMahjongGame("Tester", seed=42)
        game.start_round()
        self.assertEqual(len(game.players), 4)
        self.assertTrue(all(len(p.hand) == 13 for p in game.players))
        self.assertEqual(len(game.wall), 108 - 52)

    def test_draw_and_discard(self):
        game = SoloMahjongGame("Tester", seed=1)
        game.start_round()
        tile = game.draw_for_current()
        self.assertIsNotNone(tile)
        self.assertEqual(len(game.players[0].hand), 14)
        dropped = game.discard(0, 0)
        self.assertEqual(len(game.players[0].hand), 13)
        self.assertIn(dropped, game.players[0].discards)


if __name__ == "__main__":
    unittest.main()
