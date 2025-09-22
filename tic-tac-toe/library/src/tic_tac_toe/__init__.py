"""Tic Tac Toe reusable game engine package.

This package exposes a small, well‑typed public API for building multiple
front ends (console, desktop GUI, browser via PyScript) atop a shared
pure Python core. The internal structure is intentionally simple:

Layers:
	logic: Domain models, validation rules, search (minimax)
	game:  Orchestration layer (engine loop, player & renderer abstractions)

Only stable, documented symbols are exported via ``__all__`` below.
"""

from .game.engine import TicTacToe
from .game.players import (
	ComputerPlayer,
	MinimaxComputerPlayer,
	Player,
	RandomComputerPlayer,
)
from .logic.minimax import find_best_move
from .logic.models import GameState, Grid, Move, Mark

__all__ = [
	"GameState",
	"Grid",
	"Move",
	"Mark",
	"find_best_move",
	"TicTacToe",
	"Player",
	"ComputerPlayer",
	"RandomComputerPlayer",
	"MinimaxComputerPlayer",
]

__version__ = "1.0.0"

