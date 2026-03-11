"""游戏核心逻辑"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from src.constants import SUITS, RANKS, TOTAL_TILES, WIND_COLORS
from src.tiles import Tile, PlayerState, Meld


class MahjongGame:
    """麻将游戏核心逻辑"""

    def __init__(self, nickname: str, seed: Optional[int] = None) -> None:
        self.rng = random.Random(seed)
        self.players: List[PlayerState] = [
            PlayerState(nickname),
            PlayerState("南家"),
            PlayerState("西家"),
            PlayerState("北家"),
        ]
        self.wall: List[Tile] = []
        self.dora_indicators: List[Tile] = []
        self.turn = 0
        self.started = False
        self.last_action = ""
        self.game_over = False
        self.winner: Optional[int] = None
        self.last_discard_tile: Optional[Tile] = None

    def _build_wall(self) -> List[Tile]:
        wall = [Tile(suit, rank) for suit in SUITS for rank in RANKS for _ in range(4)]
        self.rng.shuffle(wall)
        return wall

    def start_round(self) -> None:
        if self.started:
            return
        self.started = True
        self.wall = self._build_wall()

        for _ in range(13):
            for p in self.players:
                p.hand.append(self.wall.pop())

        for p in self.players:
            p.hand.sort(key=lambda t: (SUITS.index(t.suit), t.rank))

        for _ in range(4):
            self.dora_indicators.append(self.wall.pop())

    def draw_tile(self, player_index: int) -> Optional[Tile]:
        if not self.wall:
            return None
        tile = self.wall.pop()
        self.players[player_index].hand.append(tile)
        self.players[player_index].last_draw = tile
        return tile

    def draw_for_current(self) -> Optional[Tile]:
        return self.draw_tile(self.turn)

    def discard_tile(self, player_index: int, hand_index: int) -> Tile:
        player = self.players[player_index]
        tile = player.hand.pop(hand_index)
        player.discards.append(tile)
        self.last_discard_tile = tile
        player.last_draw = None
        return tile

    def can_chow(self, player_index: int, tile: Tile) -> List[Tuple[int, int, int]]:
        player = self.players[player_index]
        if player_index == 0:
            return []

        hand_counts: dict = {}
        for t in player.hand:
            key = (t.suit, t.rank)
            hand_counts[key] = hand_counts.get(key, 0) + 1

        possible_chows: List[Tuple[int, int, int]] = []

        if tile.suit in SUITS:
            for offset in [-2, -1, 1, 2]:
                if 1 <= tile.rank + offset <= 9:
                    needed = [(tile.suit, tile.rank + offset)]
                    if offset in [-2, 2]:
                        needed.append((tile.suit, tile.rank + offset * 2))
                    else:
                        needed.append((tile.suit, tile.rank - offset))

                    can_form = True
                    for suit_rank in needed:
                        count = hand_counts.get(suit_rank, 0)
                        if count < 1:
                            can_form = False
                            break

                    if can_form:
                        possible_chows.append((tile.rank + offset, tile.rank, tile.rank - offset))

        return possible_chows

    def can_pon(self, player_index: int, tile: Tile) -> bool:
        player = self.players[player_index]
        if player_index == 0:
            return False

        count = sum(1 for t in player.hand if t.suit == tile.suit and t.rank == tile.rank)
        return count >= 2

    def can_kan(self, player_index: int, tile: Optional[Tile] = None) -> bool:
        player = self.players[player_index]
        if tile is None:
            if player.last_draw:
                tile = player.last_draw
            else:
                return False

        count = sum(1 for t in player.hand if t.suit == tile.suit and t.rank == tile.rank)
        return count >= 3

    def can_ron(self, player_index: int, tile: Tile) -> bool:
        if player_index == 0:
            return False
        return self.check_tsumo(self.players[player_index].hand + [tile])

    def can_tsumo(self, player_index: int) -> bool:
        player = self.players[player_index]
        return self.check_tsumo(player.hand)

    def check_tsumo(self, hand: List[Tile]) -> bool:
        if len(hand) != 14:
            return False

        sorted_hand = sorted(hand, key=lambda t: (SUITS.index(t.suit), t.rank))

        if self._is_thirteen_orphans(sorted_hand):
            return True

        for i in range(len(sorted_hand)):
            test_hand = sorted_hand[:i] + sorted_hand[i+1:]
            if self._can_form_sets(test_hand):
                return True

        return False

    def _is_thirteen_orphans(self, hand: List[Tile]) -> bool:
        orphans = []
        for suit in SUITS:
            for rank in [1, 9]:
                orphans.append(Tile(suit, rank))

        orphan_count = sum(1 for t in hand if t in orphans)
        return orphan_count >= 12

    def _can_form_sets(self, tiles: List[Tile]) -> bool:
        if not tiles:
            return True

        if len(tiles) % 3 != 0:
            return False

        first = tiles[0]
        count = sum(1 for t in tiles if t == first)

        if count >= 3:
            new_tiles = [t for t in tiles if t != first][:3] + [t for t in tiles if t != first][3:]
            if self._can_form_sets(new_tiles):
                return True

        if first.suit in SUITS:
            seq = [Tile(first.suit, first.rank + i) for i in range(3) if first.rank + i <= 9]
            if len(seq) == 3:
                has_seq = all(t in tiles for t in seq)
                if has_seq:
                    new_tiles = [t for t in tiles if t not in seq]
                    if self._can_form_sets(new_tiles):
                        return True

        return False

    def bot_action(self) -> str:
        tile = self.draw_for_current()
        if tile is None:
            self.game_over = True
            return "牌墙已空，流局。"

        bot = self.players[self.turn]
        hand = bot.hand

        if self.last_discard_tile:
            if self.can_ron(self.turn, self.last_discard_tile):
                self.winner = self.turn
                self.players[self.turn].is_ron = True
                return f"{bot.name} 胡牌！"

            if self.can_pon(self.turn, self.last_discard_tile):
                return f"{bot.name} 碰！"

        if self.can_tsumo(self.turn):
            self.winner = self.turn
            self.players[self.turn].is_tsumo = True
            return f"{bot.name} 自摸！"

        discard_idx = self._choose_discard(bot)
        discarded = self.discard_tile(self.turn, discard_idx)

        msg = f"{bot.name} 打出 {discarded.colored()}"
        self.turn = (self.turn + 1) % 4
        return msg

    def _choose_discard(self, player: PlayerState) -> int:
        hand = player.hand

        for i, tile in enumerate(hand):
            count = sum(1 for t in hand if t == tile)
            if count == 1:
                for j, other in enumerate(hand):
                    if other != tile and other.suit == tile.suit and abs(other.rank - tile.rank) <= 2:
                        return i

        return len(hand) - 1

    def board_summary(self) -> str:
        from src.ui import colored

        lines = []
        lines.append(colored("┌" + "─" * 46 + "┐", "CYAN"))
        lines.append(colored("│" + "  🎴 FishMJ 麻将对局  🎴 ".center(46) + "│", "YELLOW"))
        lines.append(colored("├" + "─" * 46 + "┤", "CYAN"))

        for i, p in enumerate(self.players):
            is_current = i == self.turn
            marker = colored("►", "GREEN") if is_current else " "

            wind_color = WIND_COLORS.get(i, "WHITE")
            wind_str = colored("东南西北"[i], wind_color)

            player_name = colored(p.name, "YELLOW") if i != 0 else colored(p.name, "GREEN")

            hand_count = len(p.hand)
            discard_count = len(p.discards)
            meld_count = len(p.melds)

            status = ""
            if p.is_tsumo:
                status = " 自摸!"
            elif p.is_ron:
                status = " 胡!"

            if is_current:
                line = f"{marker} {wind_str} {player_name} 手:{hand_count} 副:{meld_count} 弃:{discard_count} ◄{status}"
            else:
                line = f"  {wind_str} {player_name} 手:{hand_count} 副:{meld_count} 弃:{discard_count}{status}"
            lines.append(colored("│", "CYAN") + f" {line:<44}" + colored("│", "CYAN"))

            if p.melds:
                melds_str = " ".join([f"[{m.meld_type}]" for m in p.melds])
                lines.append(colored("│", "CYAN") + f"   └ {melds_str:<38}" + colored("│", "CYAN"))

            if p.discards:
                discards_str = " ".join([t.colored() for t in p.discards[-6:]])
                lines.append(colored("│", "CYAN") + f"   └ {discards_str:<38}" + colored("│", "CYAN"))

        wall_remaining = len(self.wall)
        wall_bar = "▓" * (wall_remaining // 14) + "░" * (10 - wall_remaining // 14)

        lines.append(colored("├" + "─" * 46 + "┤", "CYAN"))
        wall_info = f" 🎴 牌墙: {wall_remaining}/136  [{wall_bar}]"
        lines.append(colored("│", "CYAN") + f" {wall_info:<44}" + colored("│", "CYAN"))
        lines.append(colored("└" + "─" * 46 + "┘", "CYAN"))

        if self.last_action:
            lines.append(colored(f"  💬 {self.last_action}", "YELLOW"))

        return "\n".join(lines)
