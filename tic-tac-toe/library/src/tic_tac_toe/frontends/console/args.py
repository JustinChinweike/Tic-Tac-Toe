import argparse
from typing import NamedTuple

from tic_tac_toe.game.players import (
    MinimaxComputerPlayer,
    Player,
    RandomComputerPlayer,
)
from tic_tac_toe.logic.models import Mark

from .players import ConsolePlayer

PLAYER_CLASSES = {
    "human": ConsolePlayer,
    "random": RandomComputerPlayer,
    "minimax": MinimaxComputerPlayer,
}


class Args(NamedTuple):
    player1: Player
    player2: Player
    starting_mark: Mark


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument("-X", dest="player_x", choices=PLAYER_CLASSES.keys(), default="human")
    parser.add_argument("-O", dest="player_o", choices=PLAYER_CLASSES.keys(), default="minimax")
    parser.add_argument("--starting", dest="starting_mark", choices=[m.value for m in Mark], default=Mark.CROSS.value, help="Which mark starts (X or O)")
    args = parser.parse_args()

    player_x = PLAYER_CLASSES[args.player_x](Mark.CROSS)
    player_o = PLAYER_CLASSES[args.player_o](Mark.NAUGHT)

    starting_mark = Mark(args.starting_mark)

    # Args player1 is always X, player2 always O; engine uses starting_mark
    return Args(player_x, player_o, starting_mark)
