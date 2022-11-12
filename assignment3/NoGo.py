#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

import sys
from board_base import DEFAULT_SIZE, GO_POINT, GO_COLOR, PASS, opponent
from gtp_connection import GtpConnection
from board_util import GoBoardUtil
from board import GoBoard
import argparse
from typing import Tuple
from pattern_util import PatternUtil
from simulation_engine import GoSimulationEngine, Go3Args
from ucb import runUcb
from simulation_util import writeMoves, select_best_move

class Go0(GoSimulationEngine):
    def __init__(self,numSimulations:int, move_select:str, sim_rule:str, 
                 self_atari: bool, limit: int = 100) -> None:
        """
        NoGo player that selects moves randomly from the set of legal moves.

        Parameters
        ----------
        name : strOverview
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        GoSimulationEngine.__init__(self, "Go0", 1.0,
                                    sim, move_select, sim_rule, self_atari, limit)

    def simulate(self, board: GoBoard, move:GO_POINT, toplay:GO_COLOR) -> GO_COLOR:
        """
        Run a simulated game for a given move.
        """
        cboard: GoBoard = board.copy()
        cboard.play_move(move, toplay)
        opp: GO_COLOR = opponent(toplay)
        return self.playGame(cboard, opp)

    def get_move(self, board:GoBoard, color):
        """
        Run one-ply MC simulations to get a move to play.
        """
        cboard = board.copy()
        emptyPoints = board.get_empty_points()
        moves = []
        for p in emptyPoints:
            if board.is_legal(p, color):
                moves.append(p)
        if self.args.use_ucb:
            C = 0.4  # sqrt(2) is safe, this is more aggressive
            best = runUcb(self, cboard, C, moves, color)
            return best
        else:
            moveWins = []
            for move in moves:
                wins = self.simulateMove(cboard, move, color)
                moveWins.append(wins)
            writeMoves(cboard, moves, moveWins, self.args.sim)
            return select_best_move(board, moves, moveWins)

    
    def genmove(self, state):
        assert not state.endOfGame()
        moves = state.legalMoves()
        numMoves = len(moves)
        score = [0] * numMoves
        for i in range(numMoves):
            move = moves[i]
            score[i] = self.simulate(state, move)
        #print(score)
        bestIndex = score.index(max(score))
        best = moves[bestIndex]
        #print("Best move:", best, "score", score[best])
        assert best in state.legalMoves()
        return best

    def playGame(self, board: GoBoard, color: GO_COLOR) -> GO_COLOR:
        """
        Run a simulation game.
        """
        nuPasses = 0
        for _ in range(self.args.limit):
            color = board.current_player
            if self.args.random_simulation:
                move = GoBoardUtil.generate_random_move(board, color, True)
            else:
                move = PatternUtil.generate_move_with_filter(
                    board, self.args.use_pattern, self.args.check_selfatari
                )
            board.play_move(move, color)
            if move == PASS:
                nuPasses += 1
            else:
                nuPasses = 0
            if nuPasses >= 2:
                break
        return winner(board, self.komi)

def parse_args() -> Tuple[int,str,str]:
    """
    Parse the arguments
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--sim",
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
        help="type of simulation policy: random or patternbased",
    )
    parser.add_argument(
	"--movefilter",
	action="store_true",
	default=False,
	help="whether use move filter or not",
    )

    """
    Code used from Go3 program
    """
    args = parser.parse_args()
    sim = args.sim
    move_select = args.moveselect
    sim_rule = args.simrule
    check_selfatari = args.movefilter

    if move_select != "roundrobin" and move_select != "ucb":
        print("moveselect must be round robin or ucb")
        sys.exit(0)
    if sim_rule != "random" and sim_rule != "pattern":
        print("simrule must be random or patternbased")
        sys.exit(0)

    return sim, move_select, sim_rule, check_selfatari


def run(sim:int, move_select:str, sim_rule:str, self_atari:bool):
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    engine : Go0 = Go0(sim,move_select,sim_rule, self_atari)
    con = GtpConnection(Go0(), board)
    con.start_connection()

if __name__ == "__main__":
    sim, move_select, sim_rule, self_atari = parse_args()
    run(sim,move_select,sim_rule, self_atari)
