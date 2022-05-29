""""Subclass of the noughts and crosses game that implements the minimax algorithm"""

from game.app.game_base_class import NoughtsAndCrosses, NoughtsAndCrossesEssentialParameters
from game.app.player_base_class import Player
from terminal_board_scores import TerminalScore
import numpy as np
from typing import Tuple, List, Union
from random import shuffle
import math


class NoughtsAndCrossesMinimax(NoughtsAndCrosses):
    def __init__(self,
                 maximising_player: Player,
                 setup_parameters: NoughtsAndCrossesEssentialParameters,
                 draw_count: int = 0):
        super().__init__(setup_parameters, draw_count)
        self.maximising_player = maximising_player

    def minimax(self, playing_grid: np.array, search_depth: int, maximisers_move: bool, alpha: int = -math.inf,
                beta: int = math.inf) -> Union[int, Tuple[int, int]]:
        """
        Parameters:
        ----------
        playing_grid: The playing grid that is being searched. Note that we can't just used the instance attribute
        playing_grid as this gets altered throughout the searching by testing different game trees.

        search_depth: The depth at which we are searching relative to the current status of the playing_grid

        maximisers_move: T/F depending on whether we are call this function to maximise or minimise the value

        alpha: The value the maximiser can already guarantee at the given search depth or above - i.e. there is
        no point searching game trees where the minimiser is able to guarantee a lower value than this, so they are
        'pruned' meaning they're not fully searched. Default of -inf (first call) so can only be improved on

        beta: The value the minimiser can already guarantee at the given search depth or above - analogous ot alpha.
        Default of +inf (first call) so can only be improved on.

        Returns: Union[int, Tuple[int, int]].
        __________
        int when the first if statement passes. In this case the recursion has reached a board of terminal state as
        so just evaluates it

        Tuple[int, int] when the board has not reached maximum depth - it returns the move leading to the optimal score,
        assuming the maximiser always maximises and the minimiser always minimises the static evaluation function.
        """
        if self.is_terminal(playing_grid=playing_grid):  # Will be called once the recursion reaches a terminal state
            return self.evaluate_board_to_maximising_player(playing_grid=playing_grid, search_depth=search_depth)

        elif maximisers_move:
            max_score = -math.inf  # Initialise as -inf so that the score can only be improved upon
            best_move = None
            for move_option in self.get_available_cell_indices(playing_grid=playing_grid):
                playing_grid_copy = playing_grid.copy()
                self.mark_board(row_index=move_option[0], col_index=move_option[1], playing_grid=playing_grid_copy)
                potential_new_max = self.minimax(  # call minimax recursively until we hit end-state boards
                    playing_grid=playing_grid_copy, search_depth=search_depth + 1, maximisers_move=not maximisers_move,
                    alpha=alpha, beta=beta)
                # not maximisers_move is to indicate that when minimax is next called, it's a different player's go
                if potential_new_max > max_score:
                    max_score = potential_new_max
                    best_move = move_option
                alpha = max(alpha, potential_new_max)
                if beta <= alpha:
                    break  # No need to consider this game branch any further, as minimiser will avoid it
            return best_move

        else:  # minimisers move - they want to pick the game tree that minimises the score to the maximiser
            min_score = math.inf  # Initialise as +inf so that score can only be improved upon
            best_move = None
            for move_option in self.get_available_cell_indices(playing_grid=playing_grid):
                playing_grid_copy = playing_grid.copy()
                self.mark_board(row_index=move_option[0], col_index=move_option[1], playing_grid=playing_grid_copy)
                potential_new_min = self.minimax(
                    playing_grid=playing_grid_copy, search_depth=search_depth + 1, maximisers_move=not maximisers_move,
                    alpha=alpha, beta=beta)
                if potential_new_min < min_score:
                    min_score = potential_new_min
                    best_move = move_option
                beta = min(beta, potential_new_min)
                if beta <= alpha:
                    break  # No need to consider game branch any further, maximiser will just avoid it
            return best_move

    def evaluate_board_to_maximising_player(self, playing_grid: np.array, search_depth: int) -> int:
        """
        Static evaluation function for a playing_grid at the bottom of the minimax search tree, from the perspective
        of the maximising player.
        Parameters:
        __________
        search_depth: the depth in the search tree of the playing_grid scenario that we are evaluating. This is included
        as a parameter so that winning boards deep in the search tree can be penalised, and losing boards high up
        in the search tree can be favoured, to minimise search depth.
        """
        winning_player = self.get_winning_player()
        if winning_player is not None:
            if winning_player == self.maximising_player:
                return TerminalScore.MAX_WIN.value - search_depth
            else:
                return TerminalScore.MAX_LOSS.value + search_depth
        elif self.check_for_draw():
            return TerminalScore.DRAW.value  # Could also see the impact of penalising slow draws
        else:
            raise ValueError("Attempted to evaluate a playing_grid scenario that was not terminal.")

    @staticmethod
    def get_available_cell_indices(playing_grid: np.array) -> List[Tuple[int, int]]:
        """
        Method that looks at where the cells on the playing_grid are unmarked and returns a list (in a random order) of
        the index of each empty cell. This is the iterator for the minimax method.
        Parameters: playing_grid - this method is called on copies of the playing board, not just the playing board
        """
        available_cell_index_list = [tuple(index) for index in np.argwhere(playing_grid == 0)]
        shuffle(available_cell_index_list)
        return available_cell_index_list

    def is_terminal(self, playing_grid: np.array) -> bool:
        """
        Method that indicates whether or not a certain state of the playing_grid is terminal or not.
        Parameters: playing_grid - this method is called on copies of the playing board, not just the playing board
        """
        return (self.get_winning_player(playing_grid=playing_grid) is not None) or \
               (self.check_for_draw(playing_grid=playing_grid))
