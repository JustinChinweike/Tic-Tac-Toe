"""Domain models for the Tic Tac Toe game.

These immutable, dataclass based models represent the complete state of a
Tic Tac Toe game. They are intentionally *logic only* – no I/O concerns –
so they can be reused across multiple front ends.

Design goals:
* Immutability of value objects (``frozen=True`` dataclasses) for easier
    reasoning and safe sharing across threads or visualizers.
* Lazy derived values via ``functools.cached_property`` to avoid recomputing
    counts / winner detection while keeping code straightforward.
* Small public surface: ``GameState`` + ``Move`` + ``Grid`` + ``Mark``.

Evaluation & Search:
The ``evaluate_score`` method encodes terminal state utility values for the
classic minimax algorithm: X win = 1, O win = -1 (from the queried mark's
perspective), tie = 0. Non‑terminal evaluation raises
``UnknownGameScore`` to guard misuse.
"""

import enum
import random
import re
from dataclasses import dataclass
from functools import cached_property

from tic_tac_toe.logic.exceptions import InvalidMove, UnknownGameScore
from tic_tac_toe.logic.validators import validate_game_state, validate_grid

WINNING_PATTERNS = (
    "???......",
    "...???...",
    "......???",
    "?..?..?..",
    ".?..?..?.",
    "..?..?..?",
    "?...?...?",
    "..?.?.?..",
)


class Mark(str, enum.Enum):
    """Enumeration of player marks.

    Stored as single character strings for compact board representation.
    The ``other`` property returns the opposing mark, enabling concise
    turn alternation logic without conditionals spread throughout code.
    """

    CROSS = "X"
    NAUGHT = "O"

    @property
    def other(self) -> "Mark":
        """Return the opposing mark (X <-> O)."""
        return Mark.CROSS if self is Mark.NAUGHT else Mark.NAUGHT


@dataclass(frozen=True)
class Grid:
    """Immutable 3×3 board representation.

    The board is stored as a 9‑character string in row‑major order using
    characters ``X``, ``O`` and space for empties. String storage keeps the
    object hashable and cheap to copy.
    """

    cells: str = " " * 9

    def __post_init__(self) -> None:  # validation keep constructor minimal
        validate_grid(self)

    @cached_property
    def x_count(self) -> int:
        """Number of X marks on the board."""
        return self.cells.count("X")

    @cached_property
    def o_count(self) -> int:
        """Number of O marks on the board."""
        return self.cells.count("O")

    @cached_property
    def empty_count(self) -> int:
        """Number of empty cells remaining."""
        return self.cells.count(" ")


@dataclass(frozen=True)
class Move:
    """Represents a single atomic move from one state to the next.

    Storing both the originating and resulting ``GameState`` makes the
    object convenient for search algorithms and replay / visualization.
    """

    mark: Mark
    cell_index: int
    before_state: "GameState"
    after_state: "GameState"


@dataclass(frozen=True)
class GameState:
    """Complete immutable snapshot of a game at a point in time.

    Provides convenience cached properties for common derived facts such
    as whose turn it is, whether the game is over, and winner details.
    """

    grid: Grid
    starting_mark: Mark = Mark("X")

    def __post_init__(self) -> None:  # structural validation
        validate_game_state(self)

    @cached_property
    def current_mark(self) -> Mark:
        """Mark whose turn it is in this state."""
        if self.grid.x_count == self.grid.o_count:
            return self.starting_mark
        else:
            return self.starting_mark.other

    @cached_property
    def game_not_started(self) -> bool:
        """True if the board is empty (initial state)."""
        return self.grid.empty_count == 9

    @cached_property
    def game_over(self) -> bool:
        """True if a winner exists or the game is a tie."""
        return self.winner is not None or self.tie

    @cached_property
    def tie(self) -> bool:
        """True if the board is full and there is no winner."""
        return self.winner is None and self.grid.empty_count == 0

    @cached_property
    def winner(self) -> Mark | None:
        """Return the winning mark if a winning pattern is present."""
        for pattern in WINNING_PATTERNS:
            for mark in Mark:
                if re.match(pattern.replace("?", mark), self.grid.cells):
                    return mark
        return None

    @cached_property
    def winning_cells(self) -> list[int]:
        """Indices (0‑8) of the winning line if present else empty list."""
        for pattern in WINNING_PATTERNS:
            for mark in Mark:
                if re.match(pattern.replace("?", mark), self.grid.cells):
                    return [
                        match.start() for match in re.finditer(r"\?", pattern)
                    ]
        return []

    @cached_property
    def possible_moves(self) -> list[Move]:
        """All legal moves from this state (empty if terminal)."""
        moves = []
        if not self.game_over:
            for match in re.finditer(r"\s", self.grid.cells):
                moves.append(self.make_move_to(match.start()))
        return moves

    def make_random_move(self) -> Move | None:
        """Return a random legal move or ``None`` if terminal."""
        try:
            return random.choice(self.possible_moves)
        except IndexError:
            return None

    def make_move_to(self, index: int) -> Move:
        """Create the move placing the current mark in ``index``.

        Raises ``InvalidMove`` if the target cell is not empty.
        """
        if self.grid.cells[index] != " ":
            raise InvalidMove("Cell is not empty")
        return Move(
            mark=self.current_mark,
            cell_index=index,
            before_state=self,
            after_state=GameState(
                Grid(
                    self.grid.cells[:index]
                    + self.current_mark
                    + self.grid.cells[index + 1 :]
                ),
                self.starting_mark,
            ),
        )

    def evaluate_score(self, mark: Mark) -> int:
        """Return terminal utility score from ``mark``'s perspective.

        1 win, -1 loss, 0 tie. Raises ``UnknownGameScore`` if not terminal.
        """
        if self.game_over:
            if self.tie:
                return 0
            if self.winner is mark:
                return 1
            else:
                return -1
        raise UnknownGameScore("Game is not over yet")
