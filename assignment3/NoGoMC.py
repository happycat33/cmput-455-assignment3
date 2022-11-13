from typing import Union, Any

from numpy import signedinteger, intc

from PatternSelection import get_best_move_based_on_pattern, \
    get_moves_probability_based_on_pattern
from board import GoBoard
from board_base import GO_COLOR, GO_POINT, BLACK, WHITE
from board_util import GoBoardUtil
from simulation_engine import GoSimulationEngine
from ucb import runUcb


class NoGo3(GoSimulationEngine):
    def __init__(self, sim: int, move_select: str, sim_rule: str) -> None:
        """
        NoGo player that selects moves by simulation.
        """
        GoSimulationEngine.__init__(self, "NoGo3", 1.0,
                                    sim, move_select, sim_rule,
                                    check_selfatari=False)

    def simulate(self, board: GoBoard, move: GO_POINT,
                 toplay: GO_COLOR) -> GO_COLOR:
        """
        Run a simulated game for a given move.
        """
        cboard: GoBoard = board.copy()
        cboard.play_move(move, toplay)
        return self.playGame(cboard)

    def get_moves_probability(self, board: GoBoard, color: GO_COLOR):
        """
        Calculate the legal moves with the probability
        """
        cboard = board.copy()

        if self.args.random_simulation:
            # Random policy
            legal_moves = GoBoardUtil.generate_legal_moves(cboard, color)
            same_prob = 1 / len(legal_moves) if len(legal_moves) > 0 else 0
            return [(move, same_prob) for move in legal_moves]

        # Pattern policy
        return get_moves_probability_based_on_pattern(cboard, color)

    def get_moves(self, board: GoBoard, color: GO_COLOR):
        """
        Run one-ply MC simulations to get a move to play.
        """
        cboard = board.copy()
        legal_moves = GoBoardUtil.generate_legal_moves(cboard, color)

        if self.args.use_ucb:
            # UCB
            C = 0.4  # sqrt(2) is safe, this is more aggressive
            moves = runUcb(self, cboard, C, legal_moves, color)
            return moves
        else:
            # Round Robin
            moveWins = []
            for move in legal_moves:
                wins = self.simulateMove(cboard, move, color)
                moveWins.append(wins)
            total = sum(moveWins)
            return [(legal_moves[i], 0 if total == 0 else moveWins[i] / total)
                    for i in
                    range(len(legal_moves))]

    def playGame(self, board: GoBoard) -> GO_COLOR:
        """
        Run a simulation game.
        """
        winner = self.get_winner(board)
        while winner is None:
            color = board.current_player
            if self.args.random_simulation:
                # random policy
                move = GoBoardUtil.generate_random_move(board, color, False)
            else:
                # Pattern-based probabilistic
                move = get_best_move_based_on_pattern(board, color)

            board.play_move(move, color)

            # check if the game is over
            winner = self.get_winner(board)

        return winner

    def get_winner(self, board: GoBoard):
        # get current winner
        legal_moves = GoBoardUtil.generate_legal_moves(board,
                                                       board.current_player)
        if len(legal_moves) > 0:
            return None
        else:
            if board.current_player == BLACK:
                return WHITE
            else:
                return BLACK
