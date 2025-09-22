"""Classic depth‑first minimax search for Tic Tac Toe.

Pure functional style (no global state / mutation) keeps the algorithm
easy to reason about and test. Because the game tree is tiny (≤ 9! states)
the simple implementation is sufficient for an "unbeatable" AI.

The browser front end contains an extended variant with alpha‑beta pruning
and instrumentation for visualization; here we keep a minimal reference
implementation appropriate for library consumption.
"""

from math import inf

from tic_tac_toe.logic.models import GameState, Mark, Move


def find_best_move(game_state: GameState) -> Move | None:
    """Return the optimal move for the current player or ``None``.

    Uses alpha-beta pruning to speed up search. Returns ``None`` only for
    terminal states. Tic Tac Toe already has a tiny search space but this
    keeps performance easily within strict test limits.
    """
    if game_state.game_over:
        return None
    maximizer: Mark = game_state.current_mark
    best_score = -inf
    best_move: Move | None = None
    for move in game_state.possible_moves:
        score = _alphabeta(
            move.after_state,
            maximizer=maximizer,
            is_maximizing=False,
            alpha=-inf,
            beta=inf,
        )
        if score > best_score:
            best_score = score
            best_move = move
    return best_move

def minimax(move: Move, maximizer: Mark, choose_highest_score: bool = False) -> int:  # backward compat
    """Legacy minimax wrapper retained for API compatibility.

    Delegates to alpha-beta implementation by evaluating the move's
    resulting state. ``choose_highest_score`` is ignored because alpha-beta
    infers layer parity from recursion depth.
    """
    return _alphabeta(move.after_state, maximizer, not choose_highest_score, -inf, inf)


def _alphabeta(
    state: GameState,
    maximizer: Mark,
    is_maximizing: bool,
    alpha: float,
    beta: float,
) -> int:
    if state.game_over:
        return state.evaluate_score(maximizer)
    if is_maximizing:
        value = -inf
        for move in state.possible_moves:
            value = max(
                value,
                _alphabeta(
                    move.after_state, maximizer, False, alpha, beta
                ),
            )
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return int(value)
    else:
        value = inf
        for move in state.possible_moves:
            value = min(
                value,
                _alphabeta(
                    move.after_state, maximizer, True, alpha, beta
                ),
            )
            beta = min(beta, value)
            if beta <= alpha:
                break
        return int(value)
