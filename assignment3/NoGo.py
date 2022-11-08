#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

import sys
from gtp_connection import GtpConnection
from board_util import GoBoardUtil
from board import GoBoard
import argparse
from typing import Tuple

class Go0:
    def __init__(self, move_select:str):
        """
        NoGo player that selects moves randomly from the set of legal moves.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "Go0"
        self.version = 1.0

    def get_move(self, board, color):
        return GoBoardUtil.generate_random_move(board, color, 
                                                use_eye_filter=False)
def parse_args() -> Tuple[int,str,str]:
    """
    Parse the arguments
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--simnum",
        type=int,
        default=10,
        help="number of simulations per legal move",
    )
    parser.add_argument(
        "--moveselect",
        type=str,
        default="roundrobin",
        help="type of move selection: roundrobin or ucb",
    )
    parser.add_argument(
        "--simrule",
        type=str,
        default="random",
        help="type of simulation policy: random or rulebased",
    )

    """
    Code used from Go3 program
    """
    args = parser.parse_args()
    sim = args.sim
    move_select = args.moveselect
    sim_rule = args.simrule

    if move_select != "simple" and move_select != "ucb":
        print("moveselect must be simple or ucb")
        sys.exit(0)
    if sim_rule != "random" and sim_rule != "rulebased":
        print("simrule must be random or rulebased")
        sys.exit(0)

    return sim, move_select, sim_rule


def run(sim:int, move_select:str, sim_rule:str):
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Go0(), board)
    con.start_connection()

if __name__ == "__main__":
    sim, move_select, sim_rule = parse_args()
    run(sim,move_select,sim_rule)
