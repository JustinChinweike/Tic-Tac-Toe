"""Player strategy abstractions.

Defines an extensible set of player types (human input handlers, random
AI, minimax AI). Each concrete player returns a ``Move`` given the
current ``GameState`` without mutating external state.
"""

import abc
import time

from tic_tac_toe.logic.exceptions import InvalidMove
from tic_tac_toe.logic.minimax import find_best_move
from tic_tac_toe.logic.models import GameState, Mark, Move


class Player(metaclass=abc.ABCMeta):
    """Abstract base class for all player strategies."""

    def __init__(self, mark: Mark) -> None:
        self.mark = mark

    def make_move(self, game_state: GameState) -> GameState:
        """Return the next ``GameState`` after this player's move.

        Raises ``InvalidMove`` if called out of turn or no legal move
        exists (terminal state).
        """
        if self.mark is game_state.current_mark:
            if move := self.get_move(game_state):
                return move.after_state
            raise InvalidMove("No more possible moves")
        else:
            raise InvalidMove("It's the other player's turn")

    @abc.abstractmethod
    def get_move(self, game_state: GameState) -> Move | None:
        """Return the desired move (or ``None`` if none available)."""


class ComputerPlayer(Player, metaclass=abc.ABCMeta):
    """Base class for AI strategies with optional think delay."""

    def __init__(self, mark: Mark, delay_seconds: float = 0.25) -> None:
        super().__init__(mark)
        self.delay_seconds = delay_seconds

    def get_move(self, game_state: GameState) -> Move | None:
        time.sleep(self.delay_seconds)
        return self.get_computer_move(game_state)

    @abc.abstractmethod
    def get_computer_move(self, game_state: GameState) -> Move | None:
        """Return the computer's chosen move."""


class RandomComputerPlayer(ComputerPlayer):
    """AI that selects a random legal move."""

    def get_computer_move(self, game_state: GameState) -> Move | None:
        return game_state.make_random_move()


class MinimaxComputerPlayer(ComputerPlayer):
    """Unbeatable AI using the classic minimax algorithm."""

    def get_computer_move(self, game_state: GameState) -> Move | None:
        if game_state.game_not_started:
            return game_state.make_random_move()
        else:
            return find_best_move(game_state)
