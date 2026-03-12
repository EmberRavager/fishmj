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
        self.turn_phase = "await_draw"
        self.started = False
        self.last_action = ""
        self.game_over = False
        self.winner: Optional[int] = None
        self.winners: List[int] = []
        self.last_discard_tile: Optional[Tile] = None
        self.last_discard_player: Optional[int] = None

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
        self.turn_phase = "await_draw"

    def draw_tile(self, player_index: int) -> Optional[Tile]:
        if not self.wall:
            return None
        tile = self.wall.pop()
        self.players[player_index].hand.append(tile)
        self.players[player_index].last_draw = tile
        return tile

    def draw_for_current(self) -> Optional[Tile]:
        tile = self.draw_tile(self.turn)
        if tile is not None:
            self.turn_phase = "await_discard"
        return tile

    def discard_tile(self, player_index: int, hand_index: int) -> Tile:
        player = self.players[player_index]
        tile = player.hand.pop(hand_index)
        player.discards.append(tile)
        self.last_discard_tile = tile
        self.last_discard_player = player_index
        player.last_draw = None
        return tile

    def set_turn(self, player_index: int) -> None:
        self.turn = player_index
        self.turn_phase = "await_draw"

    def clear_last_discard(self) -> None:
        self.last_discard_tile = None
        self.last_discard_player = None

    def resolve_ron_on_discard(
        self, discarder_index: int, tile: Tile, exclude: Optional[List[int]] = None
    ) -> List[int]:
        excluded = set(exclude or [])
        winners = []
        for i, _ in enumerate(self.players):
            if i == discarder_index or i in excluded:
                continue
            if self.can_ron(i, tile):
                winners.append(i)

        if winners:
            self.winners = winners
            self.winner = winners[0]
            self.game_over = True
            for i in winners:
                self.players[i].is_ron = True
        return winners

    def can_chow(self, player_index: int, tile: Tile) -> List[Tuple[int, int, int]]:
        player = self.players[player_index]
        hand_counts: dict = {}
        for t in player.hand:
            key = (t.suit, t.rank)
            hand_counts[key] = hand_counts.get(key, 0) + 1

        if tile.suit not in SUITS:
            return []

        possible_chows: List[Tuple[int, int, int]] = []
        sequences = [
            (tile.rank - 2, tile.rank - 1, tile.rank),
            (tile.rank - 1, tile.rank, tile.rank + 1),
            (tile.rank, tile.rank + 1, tile.rank + 2),
        ]

        for seq in sequences:
            if min(seq) < 1 or max(seq) > 9:
                continue
            needed = [rank for rank in seq if rank != tile.rank]
            if all(hand_counts.get((tile.suit, rank), 0) >= 1 for rank in needed):
                possible_chows.append(seq)

        return possible_chows

    def can_pon(self, player_index: int, tile: Tile) -> bool:
        player = self.players[player_index]
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
        return self.check_tsumo(self._combined_tiles(self.players[player_index], extra_tile=tile))

    def can_tsumo(self, player_index: int) -> bool:
        player = self.players[player_index]
        return self.check_tsumo(self._combined_tiles(player))

    def _combined_tiles(self, player: PlayerState, extra_tile: Optional[Tile] = None) -> List[Tile]:
        tiles = list(player.hand)
        for meld in player.melds:
            tiles.extend(meld.tiles)
        if extra_tile:
            tiles.append(extra_tile)
        return tiles

    def _remove_tiles_from_hand(self, player: PlayerState, tiles: List[Tile]) -> bool:
        hand = player.hand
        for tile in tiles:
            for i, hand_tile in enumerate(hand):
                if hand_tile == tile:
                    hand.pop(i)
                    break
            else:
                return False
        return True

    def claim_pon(self, player_index: int, tile: Tile, from_player: int) -> bool:
        player = self.players[player_index]
        needed = [Tile(tile.suit, tile.rank), Tile(tile.suit, tile.rank)]
        if not self._remove_tiles_from_hand(player, needed):
            return False
        meld_tiles = needed + [tile]
        player.melds.append(Meld("碰", meld_tiles, from_player=from_player))
        player.hand.sort(key=lambda t: (SUITS.index(t.suit), t.rank))
        self.clear_last_discard()
        self.turn = player_index
        self.turn_phase = "await_discard"
        return True

    def claim_chow(self, player_index: int, tile: Tile, sequence: Tuple[int, int, int], from_player: int) -> bool:
        player = self.players[player_index]
        if tile.rank not in sequence:
            return False
        needed_ranks = []
        used_tile = False
        for rank in sequence:
            if rank == tile.rank and not used_tile:
                used_tile = True
                continue
            needed_ranks.append(rank)
        needed_tiles = [Tile(tile.suit, rank) for rank in needed_ranks]
        if not self._remove_tiles_from_hand(player, needed_tiles):
            return False
        meld_tiles = needed_tiles + [tile]
        meld_tiles.sort(key=lambda t: t.rank)
        player.melds.append(Meld("吃", meld_tiles, from_player=from_player))
        player.hand.sort(key=lambda t: (SUITS.index(t.suit), t.rank))
        self.clear_last_discard()
        self.turn = player_index
        self.turn_phase = "await_discard"
        return True

    def available_concealed_kans(self, player_index: int) -> List[Tile]:
        player = self.players[player_index]
        counts: dict = {}
        for tile in player.hand:
            key = (tile.suit, tile.rank)
            counts[key] = counts.get(key, 0) + 1
        kans = []
        for (suit, rank), count in counts.items():
            if count >= 4:
                kans.append(Tile(suit, rank))
        return kans

    def claim_kan(self, player_index: int, tile: Tile, from_player: Optional[int]) -> bool:
        player = self.players[player_index]
        needed = [Tile(tile.suit, tile.rank)] * (3 if from_player is not None else 4)
        if not self._remove_tiles_from_hand(player, needed):
            return False
        meld_tiles = needed + ([tile] if from_player is not None else [])
        player.melds.append(Meld("杠", meld_tiles, from_player=from_player))
        player.hand.sort(key=lambda t: (SUITS.index(t.suit), t.rank))
        self.clear_last_discard()
        self.turn = player_index
        self.turn_phase = "await_draw"
        return True

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
        bot = self.players[self.turn]
        if self.last_discard_tile:
            if self.last_discard_player is not None:
                winners = self.resolve_ron_on_discard(
                    self.last_discard_player,
                    self.last_discard_tile,
                )
                if winners:
                    names = "、".join([self.players[i].name for i in winners])
                    return f"{names} 胡牌！"

            if self.can_ron(self.turn, self.last_discard_tile):
                self.winner = self.turn
                self.winners = [self.turn]
                self.players[self.turn].is_ron = True
                return f"{bot.name} 胡牌！"

            if self.can_kan(self.turn, self.last_discard_tile):
                from_player = self.last_discard_player if self.last_discard_player is not None else (self.turn - 1) % 4
                winners = self.resolve_ron_on_discard(from_player, self.last_discard_tile)
                if winners:
                    names = "、".join([self.players[i].name for i in winners])
                    return f"{names} 抢杠胡！"
                if self.claim_kan(self.turn, self.last_discard_tile, from_player=from_player):
                    tile = self.draw_for_current()
                    if tile is None:
                        self.game_over = True
                        return "牌墙已空，流局。"
                    discard_idx = self._choose_discard(bot)
                    discarded = self.discard_tile(self.turn, discard_idx)
                    msg = f"{bot.name} 杠后打出 {discarded.colored()}"
                    self.set_turn((self.turn + 1) % 4)
                    return msg

            if self.can_pon(self.turn, self.last_discard_tile):
                from_player = self.last_discard_player if self.last_discard_player is not None else (self.turn - 1) % 4
                if self.claim_pon(self.turn, self.last_discard_tile, from_player=from_player):
                    discard_idx = self._choose_discard(bot)
                    discarded = self.discard_tile(self.turn, discard_idx)
                    msg = f"{bot.name} 碰后打出 {discarded.colored()}"
                    self.set_turn((self.turn + 1) % 4)
                    return msg

            if self.last_discard_player is not None:
                can_chow = (self.turn == (self.last_discard_player + 1) % 4)
                if can_chow:
                    sequences = self.can_chow(self.turn, self.last_discard_tile)
                    if sequences:
                        from_player = self.last_discard_player
                        if self.claim_chow(self.turn, self.last_discard_tile, sequences[0], from_player=from_player):
                            discard_idx = self._choose_discard(bot)
                            discarded = self.discard_tile(self.turn, discard_idx)
                            msg = f"{bot.name} 吃后打出 {discarded.colored()}"
                            self.set_turn((self.turn + 1) % 4)
                            return msg

        self.clear_last_discard()
        if self.turn_phase == "await_draw":
            tile = self.draw_for_current()
            if tile is None:
                self.game_over = True
                return "牌墙已空，流局。"

            if self.can_tsumo(self.turn):
                self.winner = self.turn
                self.winners = [self.turn]
                self.players[self.turn].is_tsumo = True
                return f"{bot.name} 自摸！"

        discard_idx = self._choose_discard(bot)
        discarded = self.discard_tile(self.turn, discard_idx)
        winners = self.resolve_ron_on_discard(self.turn, discarded)
        if winners:
            names = "、".join([self.players[i].name for i in winners])
            return f"{names} 胡牌！"

        msg = f"{bot.name} 打出 {discarded.colored()}"
        self.set_turn((self.turn + 1) % 4)
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

        def pad_line(content: str, width: int = 70) -> str:
            return colored("│", "CYAN") + content.ljust(width) + colored("│", "CYAN")

        def player_info(index: int) -> str:
            player = self.players[index]
            wind_color = WIND_COLORS.get(index, "WHITE")
            wind_str = colored("东南西北"[index], wind_color)
            name = colored(player.name, "GREEN" if index == 0 else "YELLOW")
            hand_count = len(player.hand)
            discard_count = len(player.discards)
            meld_count = len(player.melds)
            status = ""
            if player.is_tsumo:
                status = " T!"
            elif player.is_ron:
                status = " R!"
            marker = colored("►", "GREEN") if index == self.turn else " "
            return f"{marker}{wind_str} {name} {hand_count}/{meld_count}/{discard_count}{status}"

        lines = []
        lines.append(colored("┌" + "─" * 70 + "┐", "CYAN"))
        title = "  FishMJ  ".center(70)
        lines.append(pad_line(colored(title, "YELLOW")))
        lines.append(colored("├" + "─" * 70 + "┤", "CYAN"))

        north = player_info(1)
        north_discards = " ".join([t.colored() for t in self.players[1].discards[-6:]])
        lines.append(pad_line(north.center(70)))
        if north_discards:
            lines.append(pad_line(f"{north_discards}".center(70)))
        else:
            lines.append(pad_line(""))

        west = player_info(2)
        east = player_info(3)
        center_tile = self.last_discard_tile.colored() if self.last_discard_tile else "--"
        center = f"{center_tile}"
        middle = f"{west:<28}{center:^14}{east:>28}"
        lines.append(pad_line(middle))

        west_discards = " ".join([t.colored() for t in self.players[2].discards[-4:]])
        east_discards = " ".join([t.colored() for t in self.players[3].discards[-4:]])
        middle_discards = f"{(west_discards):<28}{'':^14}{(east_discards):>28}"
        lines.append(pad_line(middle_discards))

        wall_remaining = len(self.wall)
        wall_bar = "▓" * (wall_remaining // 14) + "░" * (10 - wall_remaining // 14)
        wall_info = f"{wall_remaining}/136  [{wall_bar}]"
        lines.append(pad_line(wall_info.center(70)))

        south = player_info(0)
        south_discards = " ".join([t.colored() for t in self.players[0].discards[-6:]])
        lines.append(pad_line(south.center(70)))
        if south_discards:
            lines.append(pad_line(f"{south_discards}".center(70)))
        else:
            lines.append(pad_line(""))

        lines.append(colored("└" + "─" * 70 + "┘", "CYAN"))

        if self.last_action:
            lines.append(colored(f"  💬 {self.last_action}", "YELLOW"))

        return "\n".join(lines)
