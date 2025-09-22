from __future__ import annotations

from tic_tac_toe.game.players import Player
from tic_tac_toe.logic.models import GameState, Move


class ConsolePlayer(Player):
    def get_move(self, game_state: GameState) -> Move | None:  # pragma: no cover - interactive
        while True:
            raw = input(f"Player {self.mark.value} move (1-9): ").strip()
            if raw.lower() in {"q", "quit", "exit"}:
                raise SystemExit(0)
            if not raw.isdigit():
                print("Enter a number 1-9")
                continue
            cell = int(raw)
            if cell < 1 or cell > 9:
                print("Enter a number 1-9")
                continue
            index = cell - 1
            if game_state.grid.cells[index] != " ":
                print("Cell occupied. Pick another.")
                continue
            # Produce a valid Move by delegating to GameState factory
            return game_state.make_move_to(index)
