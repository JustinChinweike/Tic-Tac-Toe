import tkinter as tk
from dataclasses import dataclass
from typing import Optional

from tic_tac_toe.game.engine import TicTacToe
from tic_tac_toe.game.players import MinimaxComputerPlayer, Player
from tic_tac_toe.game.renderers import Renderer
from tic_tac_toe.logic.exceptions import InvalidMove
from tic_tac_toe.logic.models import GameState, Mark

CELL_SIZE = 80
PADDING = 12
BOARD_SIZE = CELL_SIZE * 3 + PADDING * 2


class WindowRenderer(Renderer):
    def __init__(self, view: "GameView") -> None:
        self.view = view

    def render(self, game_state: GameState) -> None:  # pragma: no cover
        self.view.draw_board(game_state)


class WindowHumanPlayer(Player):
    def __init__(self, mark: Mark, view: "GameView") -> None:
        super().__init__(mark)
        self.view = view

    def get_move(self, game_state: GameState):  # pragma: no cover
        self.view.awaiting_mark = self.mark
        self.view.pending_state = game_state
        self.view.status_var.set(f"{self.mark}'s turn – click a square")
        self.view.root.wait_variable(self.view.move_ready)
        idx = self.view.clicked_index
        if idx is None:
            return None
        return game_state.make_move_to(idx)


@dataclass
class GameView:  # pragma: no cover
    root: tk.Tk

    def __post_init__(self) -> None:
        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE, height=BOARD_SIZE, bg="#ffffff")
        self.canvas.pack()
        self.status_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.status_var, font=("Arial", 12)).pack(pady=4)
        ctrl = tk.Frame(self.root)
        ctrl.pack(pady=4)
        tk.Button(ctrl, text="New Game", command=self.new_game).pack(side=tk.LEFT)
        self.canvas.bind("<Button-1>", self.on_click)
        self.awaiting_mark: Optional[Mark] = None
        self.pending_state: Optional[GameState] = None
        self.move_ready = tk.BooleanVar(value=False)
        self.clicked_index: Optional[int] = None
        self.engine: Optional[TicTacToe] = None
        self.status_var.set("Ready")

    def attach_engine(self, engine: TicTacToe) -> None:
        self.engine = engine

    def new_game(self) -> None:
        if self.engine:
            self.status_var.set("Starting new game")
            self.engine.play(Mark("X"))

    def on_click(self, event):
        if self.awaiting_mark is None or self.pending_state is None:
            return
        x = (event.x - PADDING) // CELL_SIZE
        y = (event.y - PADDING) // CELL_SIZE
        if not (0 <= x < 3 and 0 <= y < 3):
            return
        idx = y * 3 + x
        if self.pending_state.grid.cells[idx] != " ":
            self.status_var.set("Cell occupied")
            return
        try:
            self.clicked_index = idx
            self.awaiting_mark = None
            self.move_ready.set(True)
        except InvalidMove:
            self.status_var.set("Invalid move")

    def draw_board(self, game_state: GameState) -> None:
        self.canvas.delete("all")
        for i in range(4):
            offset = PADDING + i * CELL_SIZE
            self.canvas.create_line(PADDING, offset, PADDING + CELL_SIZE * 3, offset, width=2)
            self.canvas.create_line(offset, PADDING, offset, PADDING + CELL_SIZE * 3, width=2)
        for idx, ch in enumerate(game_state.grid.cells):
            if ch != " ":
                cx = PADDING + (idx % 3) * CELL_SIZE + CELL_SIZE / 2
                cy = PADDING + (idx // 3) * CELL_SIZE + CELL_SIZE / 2
                self.canvas.create_text(cx, cy, text=ch, font=("Arial", 36, "bold"))
        if game_state.winner:
            self.status_var.set(f"Winner: {game_state.winner}")
        elif game_state.tie:
            self.status_var.set("Tie game")
        else:
            self.status_var.set(f"Turn: {game_state.current_mark}")


def main():  # pragma: no cover
    root = tk.Tk()
    root.title("Tic Tac Toe")
    view = GameView(root)
    human = WindowHumanPlayer(Mark("X"), view)
    ai = MinimaxComputerPlayer(Mark("O"), delay_seconds=0.0)
    engine = TicTacToe(human, ai, WindowRenderer(view))
    view.attach_engine(engine)
    view.new_game()
    root.mainloop()
