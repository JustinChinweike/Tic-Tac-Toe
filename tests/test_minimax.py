from tic_tac_toe.logic.models import GameState, Grid
from tic_tac_toe.logic.minimax import find_best_move

def test_minimax_finds_winning_move():
    gs = GameState(Grid("XX OO    "))
    move = find_best_move(gs)
    assert move is not None
    assert move.cell_index == 2

def test_minimax_blocks_opponent():
    gs = GameState(Grid("OO  X X  "))
    move = find_best_move(gs)
    assert move is not None
    assert move.cell_index == 2

def test_minimax_never_returns_none_if_moves():
    gs = GameState(Grid())
    move = find_best_move(gs)
    assert move is not None
