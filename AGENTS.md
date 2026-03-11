# AGENTS.md - Agentic Coding Guidelines for FishMJ

## Project Overview

FishMJ is a Python-based Mahjong CLI game with a focus on solo/offline mode. The codebase is small and straightforward, containing a main CLI entry point and unit tests.

## Build, Lint, and Test Commands

### Running Tests

Run all tests:
```bash
python3 -m unittest discover -s tests
```

Run a single test:
```bash
python3 -m unittest tests.test_solo_game.SoloGameTest.test_start_round_deals_cards
python3 -m unittest tests.test_solo_game.SoloGameTest.test_draw_and_discard
```

Run a specific test file:
```bash
python3 -m unittest tests.test_solo_game
```

### Running the CLI

Run the solo mode:
```bash
python3 -m src.fishmj solo --nick "YourName"
python3 -m src.fishmj solo --nick "YourName" --seed 42
```

### Type Checking and Linting

Currently no external type checker or linter is configured. If you add one:

- **mypy**: `python3 -m mypy src/`
- **pyright**: `python3 -m pyright src/`
- **ruff**: `ruff check src/`

## Code Style Guidelines

### General Principles

- Keep code simple and readable
- Prefer explicit over implicit

### Imports

- Use absolute imports (e.g., `from src.fishmj import SoloMahjongGame`)
- Group imports: standard library first, then third-party, then local
- Use `from __future__ import annotations` for forward references

```python
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Optional
```

### Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters

### Type Hints

- Use type hints for all function signatures
- Use `Optional[X]` instead of `X | None` for Python 3.9 compatibility
- Use `List`, `Dict`, `Tuple` from typing

```python
def function(param: str) -> Optional[int]:
    ...
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `SoloMahjongGame`, `PlayerState`)
- **Functions/methods**: snake_case (e.g., `start_round`, `draw_for_current`)
- **Variables**: snake_case (e.g., `player_index`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `SUITS`, `RANKS`)
- **Private methods**: prefix with underscore (e.g., `_build_wall`)

### Dataclasses

- Use `@dataclass(frozen=True)` for immutable data (like `Tile`)
- Use regular `@dataclass` for mutable state (like `PlayerState`)

```python
@dataclass(frozen=True)
class Tile:
    suit: str
    rank: int

@dataclass
class PlayerState:
    name: str
    hand: List[Tile]
    discards: List[Tile]
```

### Error Handling

- Use explicit error messages
- Validate input early
- Use `raise SystemExit(code)` for CLI exit

```python
if not (0 <= index < len(hand)):
    print("索引超出范围。")
    continue
```

### CLI Structure

- Use `argparse` for argument parsing
- Create a `build_parser()` function
- Return integers from `main()` for exit codes (0 = success)

### Testing

- Use Python's built-in `unittest` framework
- Place tests in `tests/` directory
- Name test files as `test_<module>.py`
- Name test classes with `Test` suffix
- Name test methods with `test_` prefix

```python
class SoloGameTest(unittest.TestCase):
    def test_start_round_deals_cards(self):
        game = SoloMahjongGame("Tester", seed=42)
        game.start_round()
        self.assertEqual(len(game.players), 4)
```

### File Organization

```
fishmj/
├── src/
│   └── fishmj.py          # Main application code
├── tests/
│   └── test_solo_game.py  # Unit tests
├── README.md
├── PRODUCT.md
└── AGENTS.md
```

### Best Practices

1. **Keep functions small** - Each function should do one thing
2. **Avoid magic numbers** - Use named constants
3. **Use seeds for reproducibility** - Allow deterministic testing
4. **Sort hands** - Keep player hands sorted for readability
5. **Use Chinese for user-facing output** - CLI uses Chinese text
