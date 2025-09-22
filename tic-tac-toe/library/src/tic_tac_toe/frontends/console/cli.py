from tic_tac_toe.game.engine import play

from .args import parse_args
from .renderers import ConsoleRenderer


def main() -> None:  # pragma: no cover - thin wrapper
    args = parse_args()
    play(ConsoleRenderer(), args.player1, args.player2, args.starting_mark)
