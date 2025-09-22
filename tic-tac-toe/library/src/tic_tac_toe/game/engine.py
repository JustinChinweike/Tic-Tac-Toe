"""Game orchestration loop tying players and rendering together.

The ``TicTacToe`` engine is intentionally minimal: it advances the game
state by invoking the current player's move strategy and delegates visual
updates to a ``Renderer`` abstraction. This separation keeps the core
logic free of I/O concerns enabling reuse across console, GUI or web.
"""

from dataclasses import dataclass
from typing import Callable, TypeAlias

from tic_tac_toe.game.players import Player
from tic_tac_toe.game.renderers import Renderer
from tic_tac_toe.logic.exceptions import InvalidMove
from tic_tac_toe.logic.models import GameState, Grid, Mark
from tic_tac_toe.logic.validators import validate_players

ErrorHandler: TypeAlias = Callable[[Exception], None]


@dataclass(frozen=True)
class TicTacToe:
    """High level engine driving the game loop.

    Attributes:
        player1 / player2: Concrete ``Player`` implementations.
        renderer: Strategy responsible for presenting state to the user.
        error_handler: Optional callback for surfacing invalid move errors
            instead of letting them raise out of the loop.
    """

    player1: Player
    player2: Player
    renderer: Renderer
    error_handler: ErrorHandler | None = None

    def __post_init__(self):  # validate player distinct marks
        validate_players(self.player1, self.player2)

    def play(self, starting_mark: Mark = Mark.CROSS) -> None:
        """Run a complete game until terminal state reached."""
        game_state = GameState(Grid(), starting_mark)
        while True:
            self.renderer.render(game_state)
            if game_state.game_over:
                break
            player = self.get_current_player(game_state)
            try:
                game_state = player.make_move(game_state)
            except InvalidMove as ex:
                if self.error_handler:
                    self.error_handler(ex)

    def get_current_player(self, game_state: GameState) -> Player:
        """Return the player whose mark matches the state's current mark."""
        if game_state.current_mark is self.player1.mark:
            return self.player1
        else:
            return self.player2


def play(renderer: Renderer, player1: Player, player2: Player, starting_mark: Mark = Mark.CROSS) -> None:
    TicTacToe(player1, player2, renderer).play(starting_mark)
