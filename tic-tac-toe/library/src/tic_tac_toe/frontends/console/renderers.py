from __future__ import annotations

from tic_tac_toe.game.renderers import Renderer
from tic_tac_toe.logic.models import GameState


class ConsoleRenderer(Renderer):
    def render(self, game_state: GameState) -> None:  # pragma: no cover - IO
        grid = game_state.grid
        # grid.cells is a flat string of characters ("X", "O" or space)
        symbols = [c for c in grid.cells]
        print()
        for r in range(3):
            row = symbols[r * 3 : (r + 1) * 3]
            print(" | ".join(row))
            if r < 2:
                print("---------")
        print()
        if game_state.game_over:
            if game_state.winner:
                print(f"Winner: {game_state.winner.value}")
            else:
                print("Draw")
