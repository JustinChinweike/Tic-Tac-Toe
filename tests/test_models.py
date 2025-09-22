import pytest
from tic_tac_toe.logic.models import GameState, Grid, Mark
from tic_tac_toe.logic.exceptions import InvalidMove, UnknownGameScore

def test_initial_state():
    gs = GameState(Grid())
    assert gs.current_mark == Mark("X")
    assert not gs.game_over
    assert gs.possible_moves and len(gs.possible_moves) == 9

def test_make_move_and_turn_switch():
    gs = GameState(Grid())
    move0 = gs.make_move_to(0)
    assert move0.after_state.grid.cells[0] == "X"
    assert move0.after_state.current_mark == Mark("O")

def test_winner_detection_rows():
    # Use a valid game progression state where X has won top row
    # with proper mark count difference (X one ahead of O)
    gs = GameState(Grid("XXXOO    "))
    assert gs.winner == Mark("X")
    assert gs.game_over
    assert set(gs.winning_cells) == {0,1,2}

def test_tie_state():
    gs = GameState(Grid("XOXOOXXXO"))
    assert gs.tie
    assert gs.game_over
    assert gs.winner is None

def test_invalid_move_raises():
    gs = GameState(Grid())
    gs2 = gs.make_move_to(0).after_state
    with pytest.raises(InvalidMove):
        gs2.make_move_to(0)

def test_evaluate_score_terminal():
    winning = GameState(Grid("XXXOO    "))
    assert winning.game_over
    assert winning.evaluate_score(Mark("X")) == 1
    assert winning.evaluate_score(Mark("O")) == -1

def test_evaluate_score_not_over_raises():
    gs = GameState(Grid())
    with pytest.raises(UnknownGameScore):
        gs.evaluate_score(Mark("X"))
