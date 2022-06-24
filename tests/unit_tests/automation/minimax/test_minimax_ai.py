"""Test for the methods of the NoughtsAndCrossesMinimax subclass of the NoughtAndCrosses class."""

# Standard library imports
import pytest
from typing import List

# Third party imports
import numpy as np

# Local application imports
from automation.minimax.minimax_ai import NoughtsAndCrossesMinimax
from automation.minimax.constants.terminal_board_scores import TerminalScore
from game.app.game_base_class import NoughtsAndCrossesEssentialParameters
from game.app.player_base_class import Player
from game.constants.game_constants import BoardMarking, StartingPlayer


# Fixtures used throughout module
@pytest.fixture(scope="module")
def human_player():
    return Player(name="Human", marking=BoardMarking.X)


@pytest.fixture(scope="module")
def minimax_player():
    return Player(name="Minimax", marking=BoardMarking.O)


@pytest.fixture(scope="function")
def three_three_game_parameters(human_player, minimax_player):
    """
    A starting player is included so that we aren't missing a non-default arg, however is reassigned in several tests.
    Note that if a board configuration is manually specified which implies a starting player different
    to that manually specified, then minimax will try to play for the human_player and thus the test will fail.
    """
    return NoughtsAndCrossesEssentialParameters(
        game_rows_m=3,
        game_cols_n=3,
        win_length_k=3,
        player_x=human_player,
        player_o=minimax_player,
        starting_player_value=StartingPlayer.PLAYER_O.value)


@pytest.fixture(scope="function")
def three_three_game_with_minimax_player(three_three_game_parameters):
    return NoughtsAndCrossesMinimax(
        setup_parameters=three_three_game_parameters,
    )


class TestMinimaxMoveReturnThreeThreeThree:
    """
    Class to test the effectiveness of the moves generated by the minimax function on an (m,n,k) = (3,3,3) game.
    Perhaps a downside of these tests is that they are also a measure of the quality of the algorithm, beyond just
    checking that it works, in that we test whether minimax returns the winning / blocking move.
    However, given that the tests below represent the absolute simplest case that minimax would assess (1 move away
    from a win, or 1 incorrect move away from a loss, in an (m,n,k) = (3,3,3) game, it should be considered that
    the algorithm is not working if it cannot correctly generate these moves.
    """

    def test_minimax_gets_winning_move_bottom_right_row(self, three_three_game_with_minimax_player):
        """Test that minimax can win in one move when presented opportunity (bottom row win)"""
        three_three_game_with_minimax_player.starting_player_value = StartingPlayer.PLAYER_O.value
        three_three_game_with_minimax_player.playing_grid = np.array([
            [BoardMarking.X.value, BoardMarking.EMPTY.value, BoardMarking.X.value],
            [BoardMarking.EMPTY.value, BoardMarking.EMPTY.value, BoardMarking.EMPTY.value],
            [BoardMarking.O.value, BoardMarking.O.value, BoardMarking.EMPTY.value]
        ])
        score, minimax_move = three_three_game_with_minimax_player.get_minimax_move_iterative_deepening()
        assert score == TerminalScore.MAX_WIN.value - 1  # -1 to reflect a search depth of 1 to find the win
        assert np.all(minimax_move == np.array([2, 2]))

    def test_minimax_gets_winning_move_north_east_diagonal(self, three_three_game_with_minimax_player):
        """Test that minimax can win in one move when presented opportunity (north east diagonal win)"""
        three_three_game_with_minimax_player.starting_player_value = StartingPlayer.PLAYER_O.value
        three_three_game_with_minimax_player.playing_grid = np.array([
            [BoardMarking.X.value, BoardMarking.EMPTY.value, BoardMarking.O.value],
            [BoardMarking.EMPTY.value, BoardMarking.EMPTY.value, BoardMarking.EMPTY.value],
            [BoardMarking.O.value, BoardMarking.X.value, BoardMarking.EMPTY.value]
        ])
        score, minimax_move = three_three_game_with_minimax_player.get_minimax_move_iterative_deepening()
        assert score == TerminalScore.MAX_WIN.value - 1  # -1 to reflect a search depth of 1 to find the win
        assert np.all(minimax_move == np.array([1, 1]))

    def test_minimax_makes_blocking_move_middle_left_vertical(self, three_three_game_with_minimax_player):
        """Test that minimax can win in one move when presented opportunity"""
        three_three_game_with_minimax_player.starting_player_value = StartingPlayer.PLAYER_X.value
        three_three_game_with_minimax_player.playing_grid = np.array([
            [BoardMarking.X.value, BoardMarking.EMPTY.value, BoardMarking.O.value],
            [BoardMarking.EMPTY.value, BoardMarking.EMPTY.value, BoardMarking.X.value],
            [BoardMarking.X.value, BoardMarking.O.value, BoardMarking.EMPTY.value]
        ])
        _, minimax_move = three_three_game_with_minimax_player.get_minimax_move_iterative_deepening()
        assert np.all(minimax_move == np.array([1, 0]))

    def test_minimax_makes_blocking_move_south_east_diagonal(self, three_three_game_with_minimax_player):
        """Test that minimax can win in one move when presented opportunity"""
        three_three_game_with_minimax_player.starting_player_value = StartingPlayer.PLAYER_O.value
        three_three_game_with_minimax_player.playing_grid = np.array([
            [BoardMarking.X.value, BoardMarking.EMPTY.value, BoardMarking.EMPTY.value],
            [BoardMarking.EMPTY.value, BoardMarking.X.value, BoardMarking.O.value],
            [BoardMarking.EMPTY.value, BoardMarking.O.value, BoardMarking.EMPTY.value]
        ])
        _, minimax_move = three_three_game_with_minimax_player.get_minimax_move_iterative_deepening()
        assert np.all(minimax_move == np.array([2, 2]))


class TestMinimaxAncillaryMethodsThreeThree:
    """Class containing tests for the ancillary methods of the minimax class"""

    # Tests for the _get_available_cell_indices
    def test_get_available_cell_indices_ordering(self, three_three_game_with_minimax_player):
        """Test that _get_available_cell_indices gets the correct order of cells to search in."""
        three_three_game_with_minimax_player.playing_grid = np.array([
            [BoardMarking.X.value, BoardMarking.X.value, BoardMarking.O.value],
            [BoardMarking.EMPTY.value, BoardMarking.X.value, BoardMarking.O.value],
            [BoardMarking.EMPTY.value, BoardMarking.O.value, BoardMarking.EMPTY.value]
        ])
        three_three_game_with_minimax_player.previous_mark_index = np.array([0, 0])
        actual_ordered_list: List[np.ndarray] = \
            three_three_game_with_minimax_player._get_available_cell_indices(
                playing_grid=three_three_game_with_minimax_player.playing_grid, search_depth=0
            )
        expected_ordered_list = [np.array([1, 0]), np.array([2, 0]), np.array([2, 2])]
        for cell_number, expected_array in enumerate(expected_ordered_list):
            assert np.all(actual_ordered_list[cell_number] == expected_array)

    def test_get_available_cell_indices_random(self, three_three_game_with_minimax_player):
        """Test that the correct cells are identified as available"""
        three_three_game_with_minimax_player.playing_grid = np.array([
            [BoardMarking.X.value, BoardMarking.X.value, BoardMarking.O.value],
            [BoardMarking.EMPTY.value, BoardMarking.X.value, BoardMarking.O.value],
            [BoardMarking.EMPTY.value, BoardMarking.O.value, BoardMarking.EMPTY.value]
        ])
        actual_random_ordered_list: List[np.ndarray] = \
            three_three_game_with_minimax_player._get_available_cell_indices(
                playing_grid=three_three_game_with_minimax_player.playing_grid, search_depth=0
            )
        expected_random_ordered_list = [np.array([2, 0]), np.array([2, 2]), np.array([1, 0])]  # Order does not matter
        for expected_cell in expected_random_ordered_list:  # assert cell in list does not work as cell is a numpy array
            validity = False
            for actual_cell in actual_random_ordered_list:
                validity += np.all(expected_cell == actual_cell)
            assert validity

    def test_available_cell_prioritiser(self):
        """Test that the available_cell_prioritiser is working."""
        actual_absolute = NoughtsAndCrossesMinimax._available_cell_prioritiser(
            last_played_index=np.array([0, 1]), available_index=np.array([1, 0]))
        expected_absolute = np.sqrt(2)
        assert actual_absolute == pytest.approx(expected_absolute) == actual_absolute
