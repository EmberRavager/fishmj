"""牌相关类定义"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.constants import SUIT_COLORS, TILE_CHARS, BOLD, WHITE, RESET, SUITS


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

    def __lt__(self, other: Tile) -> bool:
        if self.suit != other.suit:
            return list(SUITS).index(self.suit) < list(SUITS).index(other.suit)
        return self.rank < other.rank

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tile):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))


@dataclass
class Meld:
    meld_type: str
    tiles: List[Tile]
    from_player: Optional[int] = None


@dataclass
class PlayerState:
    name: str
    hand: List[Tile] = field(default_factory=list)
    discards: List[Tile] = field(default_factory=list)
    melds: List[Meld] = field(default_factory=list)
    is_ready: bool = False
    is_tsumo: bool = False
    is_ron: bool = False
    last_draw: Optional[Tile] = None
