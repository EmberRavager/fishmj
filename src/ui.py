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
    hand_tiles = "  ".join([f"[{t.colored()}]" for t in hand])
    hand_indices = "  ".join([f"{i+1:^3}" for i in range(len(hand))])

    print()
    print(f" 你的手牌: {hand_tiles}")
    print(f"        {hand_indices}")
    print()


def menu_line(content: str, width: int = 54, pad: bool = True) -> str:
    padded = content.ljust(width) if pad else content
    return f"{colored('║', 'CYAN')}{padded}{colored('║', 'CYAN')}"


def show_main_menu() -> None:
    clear_screen()
    print()


def prompt_discard(game: MahjongGame) -> bool:
    while True:
        if game.turn_phase != "await_discard":
            print(colored("\n  ⚠ 需要先摸牌", "YELLOW"))
            input(colored("\n按回车继续...", "DIM"))
            return False
        print_hand_with_help(game.players[0].hand)
        raw = input(colored("  请输入要打出的牌序号 >> ", "GREEN")).strip()
        if raw.isdigit():
            index = int(raw) - 1
            if 0 <= index < len(game.players[0].hand):
                discarded = game.discard_tile(0, index)
                game.last_action = f"你打出 {discarded.colored()}"
                game.set_turn(1)
                winners = game.resolve_ron_on_discard(0, discarded)
                if winners:
                    names = "、".join([game.players[i].name for i in winners])
                    game.last_action = f"{names} 胡牌！"
                return game.game_over
        print(colored("索引超出范围。", "RED"))
        input(colored("\n按回车继续...", "DIM"))
    print(colored("╔" + "═" * 54 + "╗", "CYAN"))
    title = "  🀄  FishMJ 麻将  🀄  ".center(54)
    print(menu_line(colored(title, "YELLOW"), pad=False))
    print(colored("╠" + "═" * 54 + "╣", "CYAN"))
    print(menu_line(""))
    section = "  🎮 游戏模式 ".center(54)
    print(menu_line(colored(section, "WHITE"), pad=False))
    print(menu_line(""))
    option_1 = "    1. 单机模式   - 1人 + 3电脑".ljust(54)
    option_1 = option_1.replace("1.", colored("1.", "CYAN"), 1)
    option_1 = option_1.replace("单机模式", colored("单机模式", "GREEN"), 1)
    print(menu_line(option_1, pad=False))
    option_2 = "    2. 对战模式   - 暂未开放".ljust(54)
    option_2 = option_2.replace("2.", colored("2.", "CYAN"), 1)
    option_2 = option_2.replace("对战模式", colored("对战模式", "YELLOW"), 1)
    print(menu_line(option_2, pad=False))
    option_3 = "    3. 联机模式   - 暂未开放".ljust(54)
    option_3 = option_3.replace("3.", colored("3.", "CYAN"), 1)
    option_3 = option_3.replace("联机模式", colored("联机模式", "BLUE"), 1)
    print(menu_line(option_3, pad=False))
    print(menu_line(""))
    option_q = "    q. 退出游戏".ljust(54)
    option_q = option_q.replace("q.", colored("q.", "RED"), 1)
    print(menu_line(option_q, pad=False))
    print(menu_line(""))
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

    while True:
        if game.game_over:
            print(colored("\n游戏结束！", "YELLOW"))
            if game.winners:
                if len(game.winners) == 1:
                    winner = game.players[game.winners[0]]
                    print(colored(f"\n  🎉 {winner.name} 胡牌！", "GREEN"))
                else:
                    names = "、".join([game.players[i].name for i in game.winners])
                    print(colored(f"\n  🎉 多人胡牌：{names}", "GREEN"))
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

        claim_options = []
        if game.last_discard_tile:
            if game.can_ron(0, game.last_discard_tile):
                claim_options.append("hu=胡")
            if game.can_pon(0, game.last_discard_tile):
                claim_options.append("pon=碰")
            if game.can_kan(0, game.last_discard_tile):
                claim_options.append("kan=杠")
            can_chow = game.last_discard_player == 3
            if can_chow and game.can_chow(0, game.last_discard_tile):
                claim_options.append("chi=吃")

        if claim_options:
            last_tile = game.last_discard_tile
            if last_tile is None:
                continue
            tips = "  可操作: " + "  ".join(claim_options)
            print(colored(tips, "YELLOW"))
            raw = input(colored("  选择操作(回车跳过) >> ", "GREEN")).strip().lower()
            if raw in {"q", "quit", "exit"}:
                print(colored("\n已退出游戏，再见！", "GREEN"))
                return 0
            if raw == "hu":
                winners = game.resolve_ron_on_discard(game.last_discard_player or 0, last_tile)
                if 0 not in winners:
                    winners = [0] + winners
                    game.winners = winners
                    game.winner = winners[0]
                    game.game_over = True
                for i in winners:
                    game.players[i].is_ron = True
                game.last_action = "你胡牌！"
                clear_screen()
                print_header("🐟 FishMJ 麻将 🀄")
                print(game.board_summary())
                if len(game.winners) > 1:
                    names = "、".join([game.players[i].name for i in game.winners])
                    print(colored(f"\n  🎉 多人胡牌：{names}", "GREEN"))
                else:
                    print(colored("\n  🎉 你胡牌！", "GREEN"))
                input(colored("\n按回车退出...", "DIM"))
                return 0
            if raw == "chi":
                if game.last_discard_player != 3:
                    print(colored("\n  ❌ 没有可吃的牌", "RED"))
                    input(colored("\n按回车继续...", "DIM"))
                    continue
                sequences = game.can_chow(0, last_tile)
                if not sequences:
                    print(colored("\n  ❌ 没有可吃的牌", "RED"))
                    input(colored("\n按回车继续...", "DIM"))
                    continue
                if len(sequences) > 1:
                    print(colored("\n  可吃组合:", "CYAN"))
                    for i, seq in enumerate(sequences, start=1):
                        tiles = [Tile(last_tile.suit, r) for r in seq]
                        tiles_str = " ".join([t.colored() for t in tiles])
                        print(f"   {i}. {tiles_str}")
                    choice = input(colored("\n  选择组合序号 >> ", "GREEN")).strip()
                    if not choice.isdigit() or not (1 <= int(choice) <= len(sequences)):
                        print(colored("\n  ❌ 选择无效", "RED"))
                        input(colored("\n按回车继续...", "DIM"))
                        continue
                    sequence = sequences[int(choice) - 1]
                else:
                    sequence = sequences[0]
                if game.claim_chow(0, last_tile, sequence, from_player=3):
                    game.last_action = "你吃牌"
                    if prompt_discard(game):
                        return 0
                    continue
                print(colored("\n  ❌ 吃牌失败", "RED"))
                input(colored("\n按回车继续...", "DIM"))
                continue
            if raw == "pon":
                if game.can_pon(0, last_tile):
                    if game.claim_pon(0, last_tile, from_player=3):
                        game.last_action = "你碰牌"
                        if prompt_discard(game):
                            return 0
                        continue
                    print(colored("\n  ❌ 碰牌失败", "RED"))
                else:
                    print(colored("\n  ❌ 没有可碰的牌", "RED"))
                input(colored("\n按回车继续...", "DIM"))
                continue
            if raw == "kan":
                if game.can_kan(0, last_tile):
                    winners = game.resolve_ron_on_discard(3, last_tile, exclude=[0])
                    if winners:
                        names = "、".join([game.players[i].name for i in winners])
                        print(colored(f"\n  ❌ 被抢杠胡：{names}", "RED"))
                        input(colored("\n按回车退出...", "DIM"))
                        return 0
                    if game.claim_kan(0, last_tile, from_player=3):
                        if game.turn_phase != "await_draw":
                            game.turn_phase = "await_draw"
                        tile = game.draw_for_current()
                        if tile is None:
                            print(colored("牌墙已空，流局。", "YELLOW"))
                            return 0
                        print(colored(f"\n  你补摸到 {tile.colored()}", "CYAN"))
                        if prompt_discard(game):
                            return 0
                        continue
                    print(colored("\n  ❌ 杠牌失败", "RED"))
                else:
                    kans = game.available_concealed_kans(0)
                    if not kans:
                        print(colored("\n  ❌ 没有可杠的牌", "RED"))
                        input(colored("\n按回车继续...", "DIM"))
                        continue
                    if len(kans) > 1:
                        print(colored("\n  可暗杠牌:", "CYAN"))
                        for i, k in enumerate(kans, start=1):
                            print(f"   {i}. {k.colored()}")
                        choice = input(colored("\n  选择暗杠序号 >> ", "GREEN")).strip()
                        if not choice.isdigit() or not (1 <= int(choice) <= len(kans)):
                            print(colored("\n  ❌ 选择无效", "RED"))
                            input(colored("\n按回车继续...", "DIM"))
                            continue
                        selected = kans[int(choice) - 1]
                    else:
                        selected = kans[0]
                    winners = game.resolve_ron_on_discard(0, selected, exclude=[0])
                    if winners:
                        names = "、".join([game.players[i].name for i in winners])
                        print(colored(f"\n  ❌ 被抢杠胡：{names}", "RED"))
                        input(colored("\n按回车退出...", "DIM"))
                        return 0
                    if game.claim_kan(0, selected, from_player=None):
                        if game.turn_phase != "await_draw":
                            game.turn_phase = "await_draw"
                        tile = game.draw_for_current()
                        if tile is None:
                            print(colored("牌墙已空，流局。", "YELLOW"))
                            return 0
                        print(colored(f"\n  你补摸到 {tile.colored()}", "CYAN"))
                        if prompt_discard(game):
                            return 0
                        continue
                    print(colored("\n  ❌ 杠牌失败", "RED"))
                input(colored("\n按回车继续...", "DIM"))
                continue
            if raw:
                print(colored("\n  ❌ 无法识别操作", "RED"))
                input(colored("\n按回车继续...", "DIM"))
                continue

        if game.turn_phase == "await_draw":
            game.clear_last_discard()
            tile = game.draw_for_current()
            if tile is None:
                print(colored("牌墙已空，流局。", "YELLOW"))
                return 0
            game.last_action = f"你摸到 {tile.colored()}"

        if game.can_tsumo(0):
            choice = input(colored("  🎉 可以自摸，输入 hu 胡牌，回车继续 >> ", "GREEN")).strip().lower()
            if choice == "hu":
                game.winner = 0
                game.winners = [0]
                game.players[0].is_tsumo = True
                game.last_action = "你自摸！"
                clear_screen()
                print_header("🐟 FishMJ 麻将 🀄")
                print(game.board_summary())
                print(colored(f"\n  🎉 你自摸！", "GREEN"))
                input(colored("\n按回车退出...", "DIM"))
                return 0

        while True:
            print_hand_with_help(game.players[0].hand)
            raw = input(colored("  请输入要打出的牌序号 >> ", "GREEN")).strip().lower()
            if raw in {"q", "quit", "exit"}:
                print(colored("\n已退出游戏，再见！", "GREEN"))
                return 0
            if raw.isdigit():
                index = int(raw) - 1
                if not (0 <= index < len(game.players[0].hand)):
                    print(colored("索引超出范围。", "RED"))
                    input(colored("\n按回车继续...", "DIM"))
                    continue
                discarded = game.discard_tile(0, index)
                game.last_action = f"你打出 {discarded.colored()}"
                winners = game.resolve_ron_on_discard(0, discarded)
                if winners:
                    names = "、".join([game.players[i].name for i in winners])
                    print(colored(f"\n  🎉 多人胡牌：{names}", "GREEN"))
                    input(colored("\n按回车退出...", "DIM"))
                    return 0
                game.set_turn(1)
                for _ in range(3):
                    if game.wall and not game.winner:
                        game.last_action = game.bot_action()
                        if game.winner is not None:
                            break
                break
            print(colored("索引超出范围。", "RED"))
            input(colored("\n按回车继续...", "DIM"))
