import hypothesis.strategies as st
from hypothesis import given
from tic_tac_toe.logic.models import GameState, Grid

@st.composite
def random_partial_board(draw):
    cells = [" "] * 9
    turn = "X"
    for _ in range(draw(st.integers(min_value=0, max_value=9))):
        empties = [i for i,c in enumerate(cells) if c == " "]
        if not empties:
            break
        idx = draw(st.sampled_from(empties))
        cells[idx] = turn
        board_str = ''.join(cells)
        gs = GameState(Grid(board_str))
        if gs.game_over:
            break
        turn = "O" if turn == "X" else "X"
    return ''.join(cells)

@given(random_partial_board())
def test_counts_difference_within_one(board):
    gs = GameState(Grid(board))
    assert abs(gs.grid.x_count - gs.grid.o_count) <= 1

@given(random_partial_board())
def test_possible_moves_valid(board):
    gs = GameState(Grid(board))
    for move in gs.possible_moves:
        assert gs.grid.cells[move.cell_index] == ' '
