"""UI 显示模块"""

from typing import Optional

from src.constants import CYAN, YELLOW, GREEN, RED, WHITE, DIM
from src.game import MahjongGame
from src.tiles import Tile


def colored(text: str, color: str) -> str:
    color_codes = {
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
        "DIM": "\033[2m",
        "RED": "\033[91m",
        "GREEN": "\033[92m",
        "YELLOW": "\033[93m",
        "BLUE": "\033[94m",
        "MAGENTA": "\033[95m",
        "CYAN": "\033[96m",
        "WHITE": "\033[97m",
    }
    return f"{color_codes.get(color, '')}{text}{color_codes['RESET']}"


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def print_header(title: str) -> None:
    print()
    print(colored("╔" + "═" * 50 + "╗", "CYAN"))
    print(colored(f"║{title:^50}║", "CYAN"))
    print(colored("╚" + "═" * 50 + "╝", "CYAN"))


def print_hand_with_help(hand: list) -> None:
    hand_tiles = " ".join([t.colored() for t in hand])
    hand_indices = " ".join([f"{i+1:>2}" for i in range(len(hand))])

    print()
    print(f" 你的手牌: {hand_tiles}")
    print(f"        {hand_indices}")
    print()
    print(" 命令: draw=摸牌  d N=打第N张  pon=碰  quit=退出")
    print(" 提示: d 1 打出第1张牌  d 14 打出第14张牌")


def show_main_menu() -> None:
    clear_screen()
    print()
    print(colored("╔" + "═" * 54 + "╗", "CYAN"))
    print(colored("║" + "  🀄  FishMJ 麻将  🀄  ".center(54) + "║", "YELLOW"))
    print(colored("╠" + "═" * 54 + "╣", "CYAN"))
    print(colored("║" + " ".center(54) + "║", "CYAN"))
    print(colored("║" + "  🎮 游戏模式 ".center(54) + "║", "WHITE"))
    print(colored("║" + " ".center(54) + "║", "CYAN"))
    print(colored("║" + f"    {colored('1.', 'CYAN')} {colored('单机模式', 'GREEN')}   - 1人 + 3电脑".ljust(54) + "║", "CYAN"))
    print(colored("║" + f"    {colored('2.', 'CYAN')} {colored('对战模式', 'YELLOW')}   - 暂未开放".ljust(54) + "║", "CYAN"))
    print(colored("║" + f"    {colored('3.', 'CYAN')} {colored('联机模式', 'BLUE')}   - 暂未开放".ljust(54) + "║", "CYAN"))
    print(colored("║" + " ".center(54) + "║", "CYAN"))
    print(colored("║" + f"    {colored('q.', 'RED')} 退出游戏".ljust(54) + "║", "CYAN"))
    print(colored("║" + " ".center(54) + "║", "CYAN"))
    print(colored("╚" + "═" * 54 + "╝", "CYAN"))
    print()


def main_menu() -> Optional[str]:
    while True:
        show_main_menu()
        choice = input(colored("  请选择 >> ", "GREEN")).strip().lower()

        if choice in ("1", "单机", "单机模式"):
            return "solo"
        elif choice in ("2", "对战", "对战模式"):
            print(colored("\n  ⚙ 暂未开放，敬请期待！", "YELLOW"))
            input(colored("\n  按回车返回...", "DIM"))
            continue
        elif choice in ("3", "联机", "联机模式"):
            print(colored("\n  ⚙ 暂未开放，敬请期待！", "YELLOW"))
            input(colored("\n  按回车返回...", "DIM"))
            continue
        elif choice in ("q", "quit", "exit", "退出"):
            clear_screen()
            print(colored("\n  👋 再见！感谢游玩 FishMJ！\n", "GREEN"))
            return None
        else:
            print(colored("\n  ❌ 无效选择，请重新输入", "RED"))
            input(colored("\n  按回车继续...", "DIM"))


def run_solo_mode(nickname: str, seed: Optional[int] = None) -> int:
    clear_screen()
    game = MahjongGame(nickname=nickname, seed=seed)
    game.start_round()

    print_header("🐟 FishMJ 麻将 🀄")
    print()
    print(colored(f"  欢迎 {colored(nickname, 'GREEN')} 加入游戏！", "WHITE"))
    print(f"  座位: {colored('东', 'RED')} (庄家)")
    print()
    print(f"{colored('┌─ 欢迎 ─────────────────────────────┐', 'CYAN')}")
    print(f"│ 输入命令操作，输入 help 查看更多帮助   │")
    print(f"└──────────────────────────────────────┘")

    while True:
        if game.game_over:
            print(colored("\n游戏结束！", "YELLOW"))
            if game.winner is not None:
                winner = game.players[game.winner]
                print(colored(f"\n  🎉 {winner.name} 胡牌！", "GREEN"))
            else:
                print(colored("\n  流局", "YELLOW"))
            input(colored("\n按回车退出...", "DIM"))
            return 0

        if game.wall:
            remaining = len(game.wall)
            if remaining <= 4:
                print(colored(f"\n  ⚠ 牌墙剩余 {remaining} 张！", "RED"))

        if game.turn != 0:
            game.last_action = game.bot_action()
            clear_screen()
            print_header("🐟 FishMJ 麻将 🀄")
            print(game.board_summary())

            if game.winner is not None:
                print(colored(f"\n  🎉 {game.players[game.winner].name} 胡牌！", "GREEN"))
                input(colored("\n按回车退出...", "DIM"))
                return 0

            continue

        clear_screen()
        print_header("🐟 FishMJ 麻将 🀄")
        print(game.board_summary())
        print_hand_with_help(game.players[0].hand)

        raw = input(f"\n{colored('► ', 'GREEN')}").strip()

        if raw in {"help", "h"}:
            print()
            print(" 命令帮助:")
            print("   draw    - 摸一张牌")
            print("   d N     - 打出第N张牌")
            print("   pon     - 碰")
            print("   kan     - 杠")
            print("   hu      - 胡")
            print("   auto    - 自动摸打")
            print("   hand    - 查看手牌")
            print("   board   - 查看牌桌")
            print("   quit    - 退出游戏")
            input(colored("\n按回车继续...", "DIM"))
            continue
        if raw in {"quit", "q", "exit"}:
            print(colored("\n已退出游戏，再见！", "GREEN"))
            return 0
        if raw == "hand":
            print(f"\n{colored('你的手牌:', 'CYAN')} " + " ".join([t.colored() for t in game.players[0].hand]))
            input(colored("\n按回车继续...", "DIM"))
            continue
        if raw == "board":
            print(game.board_summary())
            input(colored("\n按回车继续...", "DIM"))
            continue
        if raw == "draw":
            tile = game.draw_for_current()
            if tile is None:
                print(colored("牌墙已空，流局。", "YELLOW"))
                return 0
            game.last_action = f"你摸到了 {tile.colored()}"
            print(f"\n{colored('你摸到了:', 'CYAN')} {tile.colored()}")
            print(f"{colored('当前手牌:', 'CYAN')} " + " ".join([t.colored() for t in game.players[0].hand]))

            if game.can_tsumo(0):
                print(colored("\n  🎉 可以胡牌！输入 hu 胡牌", "GREEN"))

            input(colored("\n按回车继续...", "DIM"))
            continue
        if raw == "hu":
            if game.can_tsumo(0):
                game.winner = 0
                game.players[0].is_tsumo = True
                game.last_action = "你自摸！"
                clear_screen()
                print_header("🐟 FishMJ 麻将 🀄")
                print(game.board_summary())
                print(colored(f"\n  🎉 你自摸！", "GREEN"))
                input(colored("\n按回车退出...", "DIM"))
                return 0
            else:
                print(colored("\n  ❌ 无法胡牌", "RED"))
                input(colored("\n按回车继续...", "DIM"))
            continue
        if raw == "pon":
            if game.last_discard_tile and game.can_pon(0, game.last_discard_tile):
                print(colored("\n  ❌ 暂不支持碰", "YELLOW"))
            else:
                print(colored("\n  ❌ 没有可碰的牌", "RED"))
            input(colored("\n按回车继续...", "DIM"))
            continue
        if raw == "kan":
            if game.can_kan(0):
                print(colored("\n  ❌ 暂不支持杠", "YELLOW"))
            else:
                print(colored("\n  ❌ 没有可杠的牌", "RED"))
            input(colored("\n按回车继续...", "DIM"))
            continue
        if raw == "auto":
            tile = game.draw_for_current()
            if tile is None:
                print(colored("牌墙已空，流局。", "YELLOW"))
                return 0
            discarded = game.discard_tile(0, len(game.players[0].hand) - 1)
            game.last_action = f"你摸到 {tile.colored()}，自动打出 {discarded.colored()}"
            game.turn = 1
            for _ in range(3):
                if game.wall and not game.winner:
                    game.last_action = game.bot_action()
                    if game.winner is not None:
                        break
            continue

        parts = raw.split()
        if len(parts) == 2 and parts[0] in {"d", "discard"} and parts[1].isdigit():
            index = int(parts[1]) - 1
            if not (0 <= index < len(game.players[0].hand)):
                print(colored("索引超出范围。", "RED"))
                input(colored("\n按回车继续...", "DIM"))
                continue
            discarded = game.discard_tile(0, index)
            game.last_action = f"你打出 {discarded.colored()}"
            game.turn = 1
            for _ in range(3):
                if game.wall and not game.winner:
                    game.last_action = game.bot_action()
                    if game.winner is not None:
                        break
            continue

        print(colored("无法识别命令，输入 help 查看说明。", "RED"))
        input(colored("\n按回车继续...", "DIM"))
