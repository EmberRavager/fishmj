"""游戏常量定义"""

from typing import Dict, Tuple

SUITS: Tuple[str, ...] = ("万", "条", "筒")
RANKS: Tuple[int, ...] = tuple(range(1, 10))
WINDS: Tuple[str, ...] = ("东", "南", "西", "北")

TILE_COUNT_PER_SUIT = 4
TOTAL_TILES = len(SUITS) * len(RANKS) * TILE_COUNT_PER_SUIT

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

SUIT_COLORS: Dict[str, str] = {
    "万": RED,
    "条": GREEN,
    "筒": BLUE,
}

TILE_CHARS: Dict[str, str] = {
    "万": "🀇🀈🀉🀊🀋🀌🀍🀎🀏",
    "条": "🀐🀑🀒🀓🀔🀕🀖🀗🀘",
    "筒": "🀙🀚🀛🀜🀝🀞🀟🀠🀡",
}

WIND_COLORS: Dict[int, str] = {
    0: RED,
    1: GREEN,
    2: BLUE,
    3: MAGENTA,
}
