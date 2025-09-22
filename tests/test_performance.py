import time
from tic_tac_toe.logic.models import GameState, Grid
from tic_tac_toe.logic.minimax import find_best_move

def test_full_minimax_performance():
    start = time.time()
    gs = GameState(Grid())
    move = find_best_move(gs)
    assert move is not None
    elapsed = time.time() - start
    assert elapsed < 2.0, f"Minimax too slow: {elapsed:.2f}s"
