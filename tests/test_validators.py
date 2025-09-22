import pytest
from tic_tac_toe.logic.models import Grid, GameState
from tic_tac_toe.logic.validators import validate_grid, validate_game_state
from tic_tac_toe.logic.exceptions import InvalidGameState

def test_validate_grid_allows_valid():
    validate_grid(Grid("XOXOXO   "))

def test_validate_grid_rejects_invalid_chars():
    with pytest.raises(ValueError):
        validate_grid(Grid("INVALID!!"))

def test_validate_game_state_wrong_counts():
    with pytest.raises(InvalidGameState):
        validate_game_state(GameState(Grid("XXXXOO   ")))

def test_validate_game_state_winner_consistency():
    with pytest.raises(InvalidGameState):
        validate_game_state(GameState(Grid("XXXOOO   ")))
