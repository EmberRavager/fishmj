#!/usr/bin/env python3
"""FishMJ CLI prototype.

Current focus: solo/offline mode with 3 bots.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Optional


SUITS = ("万", "条", "筒")
RANKS = tuple(range(1, 10))


@dataclass(frozen=True)
class Tile:
    suit: str
    rank: int

    def __str__(self) -> str:
        symbols = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九"}
        return f"{symbols[self.rank]}{self.suit}"


@dataclass
class PlayerState:
    name: str
    hand: List[Tile]
    discards: List[Tile]


class SoloMahjongGame:
    """Very small offline loop for one human player + three bots."""

    def __init__(self, nickname: str, seed: Optional[int] = None) -> None:
        self.rng = random.Random(seed)
        self.players = [
            PlayerState(nickname, [], []),
            PlayerState("Bot-南", [], []),
            PlayerState("Bot-西", [], []),
            PlayerState("Bot-北", [], []),
        ]
        self.wall = self._build_wall()
        self.turn = 0
        self.started = False

    def _build_wall(self) -> List[Tile]:
        wall = [Tile(suit, rank) for suit in SUITS for rank in RANKS for _ in range(4)]
        self.rng.shuffle(wall)
        return wall

    def start_round(self) -> None:
        if self.started:
            return
        self.started = True
        for _ in range(13):
            for p in self.players:
                p.hand.append(self.wall.pop())
        self.players[0].hand.sort(key=lambda t: (SUITS.index(t.suit), t.rank))

    def draw_for_current(self) -> Optional[Tile]:
        if not self.wall:
            return None
        tile = self.wall.pop()
        self.players[self.turn].hand.append(tile)
        if self.turn == 0:
            self.players[0].hand.sort(key=lambda t: (SUITS.index(t.suit), t.rank))
        return tile

    def discard(self, player_index: int, hand_index: int) -> Tile:
        player = self.players[player_index]
        tile = player.hand.pop(hand_index)
        player.discards.append(tile)
        return tile

    def bot_step(self) -> str:
        tile = self.draw_for_current()
        if tile is None:
            return "牌墙已空，流局。"
        bot = self.players[self.turn]
        discard_index = self.rng.randrange(len(bot.hand))
        discarded = self.discard(self.turn, discard_index)
        msg = f"{bot.name} 摸牌后打出 {discarded}"
        self.turn = (self.turn + 1) % 4
        return msg

    def human_hand(self) -> str:
        cards = [f"{i + 1}[{tile}]" for i, tile in enumerate(self.players[0].hand)]
        return " ".join(cards)

    def board_summary(self) -> str:
        lines = ["Players:"]
        winds = ["东", "南", "西", "北"]
        for i, p in enumerate(self.players):
            marker = "*" if i == self.turn else " "
            lines.append(f"{marker}[{winds[i]}] {p.name} 手牌:{len(p.hand)} 弃牌:{len(p.discards)}")
        lines.append(f"剩余牌墙: {len(self.wall)}")
        return "\n".join(lines)


HELP_TEXT = """可用命令：
help                查看帮助
hand                查看手牌
draw                摸牌（仅轮到你时可用）
d <index>           打出第 index 张牌（1-based）
board               查看牌桌信息
auto                自动执行 1 轮（你摸+打后，3 个 bot 各打一手）
quit                退出
"""


def run_solo_mode(nickname: str, seed: Optional[int] = None) -> int:
    game = SoloMahjongGame(nickname=nickname, seed=seed)
    game.start_round()
    print(f"FishMJ 单机模式启动，欢迎你：{nickname}")
    print(HELP_TEXT)

    while True:
        if not game.wall:
            print("牌墙已空，流局。")
            return 0

        if game.turn != 0:
            print(game.bot_step())
            continue

        print("\nYour turn")
        print(game.board_summary())
        print("Your hand:")
        print(game.human_hand())
        raw = input("> ").strip()

        if raw in {"help", "h"}:
            print(HELP_TEXT)
            continue
        if raw in {"quit", "q", "exit"}:
            print("已退出单机模式。")
            return 0
        if raw == "hand":
            print(game.human_hand())
            continue
        if raw == "board":
            print(game.board_summary())
            continue
        if raw == "draw":
            tile = game.draw_for_current()
            if tile is None:
                print("牌墙已空，流局。")
                return 0
            print(f"你摸到了 {tile}")
            print(game.human_hand())
            continue
        if raw == "auto":
            tile = game.draw_for_current()
            if tile is None:
                print("牌墙已空，流局。")
                return 0
            print(f"你摸到了 {tile}")
            discarded = game.discard(0, len(game.players[0].hand) - 1)
            print(f"你自动打出 {discarded}")
            game.turn = 1
            for _ in range(3):
                if game.wall:
                    print(game.bot_step())
            continue

        parts = raw.split()
        if len(parts) == 2 and parts[0] in {"d", "discard"} and parts[1].isdigit():
            index = int(parts[1]) - 1
            if not (0 <= index < len(game.players[0].hand)):
                print("索引超出范围。")
                continue
            discarded = game.discard(0, index)
            print(f"你打出 {discarded}")
            game.turn = 1
            for _ in range(3):
                if game.wall:
                    print(game.bot_step())
            continue

        print("无法识别命令，输入 help 查看说明。")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FishMJ CLI")
    sub = parser.add_subparsers(dest="command")

    solo = sub.add_parser("solo", help="启动单机模式（1 人 + 3 bot）")
    solo.add_argument("--nick", default="你", help="玩家昵称")
    solo.add_argument("--seed", type=int, default=None, help="随机种子，便于复现")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command in (None, "solo"):
        nick = getattr(args, "nick", "你")
        seed = getattr(args, "seed", None)
        return run_solo_mode(nickname=nick, seed=seed)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
