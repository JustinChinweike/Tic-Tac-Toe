"""Renderer abstraction used by the game engine.

Concrete implementations (console, GUI, browser) translate a ``GameState``
into a user facing view. Keeping this separate from the engine allows
pure game logic to remain UI agnostic.
"""

import abc

from tic_tac_toe.logic.models import GameState


class Renderer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def render(self, game_state: GameState) -> None:
        """Present the given game state to the user."""
