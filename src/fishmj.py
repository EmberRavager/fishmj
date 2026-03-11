#!/usr/bin/env python3
"""FishMJ CLI prototype.

Current focus: solo/offline mode with 3 bots.
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass
from typing import List, Optional


SUITS = ("万", "条", "筒")
RANKS = tuple(range(1, 10))

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

BG_CYAN = "\033[46m"

SUIT_COLORS = {
    "万": RED,
    "条": GREEN,
    "筒": BLUE,
}

TILE_CHARS = {
    "万": "🀇🀈🀉🀊🀋🀌🀍🀎🀏",
    "条": "🀐🀑🀒🀓🀔🀕🀖🀗🀘",
    "筒": "🀙🀚🀛🀜🀝🀞🀟🀠🀡",
}


def colored(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def tile_to_str(tile: "Tile", show_back: bool = False) -> str:
    if show_back:
        return f"{BG_CYAN}{WHITE}　{RESET}"
    suit_color = SUIT_COLORS.get(tile.suit, WHITE)
    symbols = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九"}
    return f"{BOLD}{suit_color}{symbols[tile.rank]}{tile.suit}{RESET}"


def tile_to_char(tile: "Tile") -> str:
    return TILE_CHARS.get(tile.suit, "?")[tile.rank - 1]


@dataclass(frozen=True)
class Tile:
    suit: str
    rank: int

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

    def colored(self) -> str:
        suit_color = SUIT_COLORS.get(self.suit, WHITE)
        return f"{BOLD}{suit_color}{self.char()}{RESET}"

    def char(self) -> str:
        chars = TILE_CHARS.get(self.suit, "🀫")
        return chars[self.rank - 1]


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
            PlayerState("南家", [], []),
            PlayerState("西家", [], []),
            PlayerState("北家", [], []),
        ]
        self.wall = self._build_wall()
        self.turn = 0
        self.started = False
        self.last_action = ""

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
        msg = f"{colored(bot.name, YELLOW)} 摸牌后打出 {discarded.colored()}"
        self.turn = (self.turn + 1) % 4
        return msg

    def human_hand(self) -> str:
        hand = self.players[0].hand
        tiles = [f"{colored(str(i+1), CYAN)}:{tile.colored()}" for i, tile in enumerate(hand)]
        return " ".join(tiles)

    def display_hand_compact(self) -> str:
        hand = self.players[0].hand
        return "".join([tile.colored() for tile in hand])

    def board_summary(self) -> str:
        lines = []
        lines.append(colored("┌" + "─" * 46 + "┐", CYAN))
        lines.append(colored("│" + "  🎴 FishMJ 麻将对局  🎴 ".center(46) + "│", YELLOW))
        lines.append(colored("├" + "─" * 46 + "┤", CYAN))
        
        winds = ["东", "南", "西", "北"]
        
        for i, p in enumerate(self.players):
            is_current = i == self.turn
            marker = colored("►", GREEN) if is_current else " "
            hand_count = len(p.hand)
            discard_count = len(p.discards)
            
            wind_color = {0: RED, 1: GREEN, 2: BLUE, 3: MAGENTA}.get(i, WHITE)
            wind_str = colored(f"{winds[i]}", wind_color)
            
            player_name = colored(p.name, YELLOW) if i != 0 else colored(p.name, GREEN)
            
            if is_current:
                line = f"{marker} {wind_str} {player_name} 手:{hand_count} 弃:{discard_count} ◄"
            else:
                line = f"  {wind_str} {player_name} 手:{hand_count} 弃:{discard_count}"
            lines.append(colored("│", CYAN) + f" {line:<44}" + colored("│", CYAN))
            
            if p.discards:
                discards_str = " ".join([t.colored() for t in p.discards[-6:]])
                lines.append(colored("│", CYAN) + f"   └ {discards_str:<38}" + colored("│", CYAN))
        
        wall_remaining = len(self.wall)
        wall_bar = "▓" * (wall_remaining // 14) + "░" * (10 - wall_remaining // 14)
        
        lines.append(colored("├" + "─" * 46 + "┤", CYAN))
        wall_info = f" 🎴 牌墙: {wall_remaining}/136  [{wall_bar}]"
        lines.append(colored("│", CYAN) + f" {wall_info:<44}" + colored("│", CYAN))
        lines.append(colored("└" + "─" * 46 + "┘", CYAN))
        
        if self.last_action:
            lines.append(colored(f"  💬 {self.last_action}", YELLOW))
        
        return "\n".join(lines)


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def print_header(title: str) -> None:
    print()
    print(colored("╔" + "═" * 50 + "╗", CYAN))
    print(colored(f"║{title:^50}║", CYAN))
    print(colored("╚" + "═" * 50 + "╝", CYAN))


def print_hand_with_help(game: SoloMahjongGame) -> None:
    hand = game.players[0].hand
    hand_tiles = " ".join([t.colored() for t in hand])
    hand_indices = " ".join([f"{i+1:>2}" for i in range(len(hand))])
    
    print()
    print(f" 你的手牌: {hand_tiles}")
    print(f"        {hand_indices}")
    print()
    print(" 命令: draw=摸牌  d N=打第N张  auto=自动  quit=退出")
    print(" 提示: d 1 打出第1张牌  d 14 打出第14张牌")


def show_main_menu() -> None:
    clear_screen()
    print()
    print(colored("╔" + "═" * 54 + "╗", CYAN))
    print(colored("║" + "  🀄  FishMJ 麻将  🀄  ".center(54) + "║", YELLOW))
    print(colored("╠" + "═" * 54 + "╣", CYAN))
    print(colored("║" + " ".center(54) + "║", CYAN))
    print(colored("║" + "  🎮 游戏模式 ".center(54) + "║", WHITE))
    print(colored("║" + " ".center(54) + "║", CYAN))
    print(colored("║" + f"    {colored('1.', CYAN)} {colored('单机模式', GREEN)}   - 1人 + 3电脑".ljust(54) + "║", CYAN))
    print(colored("║" + f"    {colored('2.', CYAN)} {colored('对战模式', YELLOW)}   - 暂未开放".ljust(54) + "║", CYAN))
    print(colored("║" + f"    {colored('3.', CYAN)} {colored('联机模式', BLUE)}   - 暂未开放".ljust(54) + "║", CYAN))
    print(colored("║" + " ".center(54) + "║", CYAN))
    print(colored("║" + f"    {colored('q.', RED)} 退出游戏".ljust(54) + "║", CYAN))
    print(colored("║" + " ".center(54) + "║", CYAN))
    print(colored("╚" + "═" * 54 + "╝", CYAN))
    print()


def main_menu() -> Optional[str]:
    while True:
        show_main_menu()
        choice = input(colored("  请选择 >> ", GREEN)).strip().lower()
        
        if choice in ("1", "单机", "单机模式"):
            return "solo"
        elif choice in ("2", "对战", "对战模式"):
            print(colored("\n  ⚙ 暂未开放，敬请期待！", YELLOW))
            input(colored("\n  按回车返回...", DIM))
            continue
        elif choice in ("3", "联机", "联机模式"):
            print(colored("\n  ⚙ 暂未开放，敬请期待！", YELLOW))
            input(colored("\n  按回车返回...", DIM))
            continue
        elif choice in ("q", "quit", "exit", "退出"):
            clear_screen()
            print(colored("\n  👋 再见！感谢游玩 FishMJ！\n", GREEN))
            return None
        else:
            print(colored("\n  ❌ 无效选择，请重新输入", RED))
            input(colored("\n  按回车继续...", DIM))


def run_solo_mode(nickname: str, seed: Optional[int] = None) -> int:
    clear_screen()
    game = SoloMahjongGame(nickname=nickname, seed=seed)
    game.start_round()
    
    print_header("🐟 FishMJ 麻将 🀄")
    print()
    print(colored(f"  欢迎 {colored(nickname, GREEN)} 加入游戏！", WHITE))
    print(f"  座位: {colored('东', RED)} (庄家)")
    print()
    print(f"{colored('┌─ 欢迎 ─────────────────────────────┐', CYAN)}")
    print(f"│ 输入命令操作，输入 help 查看更多帮助   │")
    print(f"└──────────────────────────────────────┘")

    while True:
        if not game.wall:
            print(colored("\n牌墙已空，流局。", YELLOW))
            print(colored("游戏结束！", GREEN))
            return 0

        if game.turn != 0:
            game.last_action = game.bot_step()
            clear_screen()
            print_header("🐟 FishMJ 麻将 🀄")
            print(game.board_summary())
            continue

        clear_screen()
        print_header("🐟 FishMJ 麻将 🀄")
        print(game.board_summary())
        print_hand_with_help(game)
        
        raw = input(f"\n{colored('► ', GREEN)}").strip()

        if raw in {"help", "h"}:
            print()
            print(" 命令帮助:")
            print("   draw    - 摸一张牌")
            print("   d N     - 打出第N张牌")
            print("   auto    - 自动摸打")
            print("   hand    - 查看手牌")
            print("   board   - 查看牌桌")
            print("   quit    - 退出游戏")
            input(colored("\n按回车继续...", DIM))
            continue
        if raw in {"quit", "q", "exit"}:
            print(colored("\n已退出游戏，再见！", GREEN))
            return 0
        if raw == "hand":
            print(f"\n{colored('你的手牌:', CYAN)} {game.display_hand_compact()}")
            input(colored("\n按回车继续...", DIM))
            continue
        if raw == "board":
            print(game.board_summary())
            input(colored("\n按回车继续...", DIM))
            continue
        if raw == "draw":
            tile = game.draw_for_current()
            if tile is None:
                print(colored("牌墙已空，流局。", YELLOW))
                return 0
            game.last_action = f"你摸到了 {tile.colored()}"
            print(f"\n{colored('你摸到了:', CYAN)} {tile.colored()}")
            print(f"{colored('当前手牌:', CYAN)} {game.display_hand_compact()}")
            input(colored("\n按回车继续...", DIM))
            continue
        if raw == "auto":
            tile = game.draw_for_current()
            if tile is None:
                print(colored("牌墙已空，流局。", YELLOW))
                return 0
            discarded = game.discard(0, len(game.players[0].hand) - 1)
            game.last_action = f"你摸到 {tile.colored()}，自动打出 {discarded.colored()}"
            game.turn = 1
            for _ in range(3):
                if game.wall:
                    game.last_action = game.bot_step()
            continue

        parts = raw.split()
        if len(parts) == 2 and parts[0] in {"d", "discard"} and parts[1].isdigit():
            index = int(parts[1]) - 1
            if not (0 <= index < len(game.players[0].hand)):
                print(colored("索引超出范围。", RED))
                input(colored("\n按回车继续...", DIM))
                continue
            discarded = game.discard(0, index)
            game.last_action = f"你打出 {discarded.colored()}"
            game.turn = 1
            for _ in range(3):
                if game.wall:
                    game.last_action = game.bot_step()
            continue

        print(colored("无法识别命令，输入 help 查看说明。", RED))
        input(colored("\n按回车继续...", DIM))


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
        mode = main_menu()
        if mode is None:
            return 0
        nick = getattr(args, "nick", "你")
        seed = getattr(args, "seed", None)
        return run_solo_mode(nickname=nick, seed=seed)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
