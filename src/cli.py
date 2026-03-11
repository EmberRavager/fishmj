"""CLI 入口"""

import argparse
from typing import Optional

from src.ui import run_solo_mode, main_menu


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
