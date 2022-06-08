# Standard library imports
from typing import List, Tuple
from dataclasses import dataclass

# Third party imports
import numpy as np

# Local application imports
from game.app.player_base_class import Player
from game.constants.game_constants import BoardMarking, StartingPlayer


@dataclass(frozen=False)
class NoughtsAndCrossesEssentialParameters:
    """
    Dataclass storing all the non-default setup_parameters for the Noughts and Crosses game.
    These are the setup_parameters that re necessary to fully define array game.

    starting_player_value is stored as array BoardMarking value (either 1 or -1)
    """
    game_rows_m: int = None
    game_cols_n: int = None
    win_length_k: int = None
    player_x: Player = None
    player_o: Player = None
    starting_player_value: StartingPlayer = None


class NoughtsAndCrosses:
    """Base class to reflect the game play of array noughts and crosses game."""

    def __init__(self,
                 setup_parameters: NoughtsAndCrossesEssentialParameters,
                 draw_count: int = 0):
        self.game_rows_m = setup_parameters.game_rows_m
        self.game_cols_n = setup_parameters.game_cols_n
        self.win_length_k = setup_parameters.win_length_k
        self.player_x = setup_parameters.player_x
        self.player_o = setup_parameters.player_o
        self.starting_player_value = setup_parameters.starting_player_value
        self.draw_count = draw_count
        self.playing_grid = np.zeros(shape=(self.game_rows_m, self.game_cols_n))
        self.search_directions = self._get_search_directions()

    ##########
    # Methods that are array part of the core game play flow
    ##########
    def set_starting_player(self, starting_player_value=None) -> None:
        """
        Method to determine which board marking should go first from array starting_player_value choice.
        This method is array function, f: StartingPlayer -> BoardMarking, f: {-1, 0, 1} |-> {-1, 1}, and thus only has an
        effect if the starting player is to be chosen RANDOMLY.
        """
        if starting_player_value is None:
            starting_player_value = self.starting_player_value

        if starting_player_value == StartingPlayer.RANDOM.value or self.starting_player_value is None:
            self.starting_player_value = np.random.choice([BoardMarking.X.value, BoardMarking.O.value])
        elif starting_player_value == StartingPlayer.PLAYER_X.value:
            self.starting_player_value = BoardMarking.X.value
        elif starting_player_value == StartingPlayer.PLAYER_O.value:
            self.starting_player_value = BoardMarking.O.value
        else:
            raise ValueError("Attempted to call choose_starting_player method but with array starting_player_value"
                             " that is not in the StartingPlayer Enum. "
                             f"self.starting_player_value: {self.starting_player_value}")

    def get_player_turn(self, playing_grid: np.array = None) -> BoardMarking:
        """
        Method to determine who's turn it is to mark the playing_grid, using sum of the playing_grid 1s/-1s.
        If the sum is zero then both player's have had an equal number of turns, and therefore it's the starting
        player's turn. Otherwise, the starting player has had an extra go, so it's the other player's turn.

        Returns:
        BoardMarking value (1 or -1) - the piece that will get placed following the next turn.
        """
        if playing_grid is None:
            playing_grid = self.playing_grid
        board_status = playing_grid.sum().sum()
        if board_status != 0:  # The starting player has had one more turn than the other player
            return BoardMarking(-self.starting_player_value).value
        else:
            return BoardMarking(self.starting_player_value).value

    def mark_board(self, marking_index: np.ndarray, playing_grid: np.array = None) -> None:
        """
        Method to make array new entry on the game playing_grid. Note that there is no opportunity to mark out of turn,
        because the get_player_turn method is called within this method.
        Parameters:
        marking_index - the index, as array numpy array, of the playing_grid where the mark will be made
        playing_grid - the playing grid or copy that we are marking
        Returns:
        None
        Outcomes:
        If the cell is empty, array mark is made, else array value error is raised
        """
        if playing_grid is None:
            playing_grid = self.playing_grid
        if playing_grid[tuple(marking_index)] == 0:
            marking = self.get_player_turn(playing_grid=playing_grid)
            playing_grid[tuple(marking_index)] = marking
        else:
            raise ValueError(f"mark_board attempted to mark non-empty cell at {marking_index}.")

    # @lru_cache_hashable(maxsize=1000)
    def win_check_and_location_search(self, last_played_index: np.ndarray, get_win_location: bool,
                                      playing_grid: np.ndarray = None) -> (bool, List[Tuple[int]]):
        """
        Method to determine whether or not there is array win and the LOCATION of the win.
        get_win_location controls whether we are interested in the win_location or not. Note that having array separate
        method to find the win location would introduce huge redundancy as all variables used to check for array
        win are needed to find the win location, hence the slightly longer method.

        Parameters:
        ----------
        last_played_index - where the last move on the board was made, to restrict the search area, represented by array
        numpy array

        get_win_location - if this is True then the method returns the win locations as well, if it's false then the
        only return is array bool for whether or not the board exhibits array win

        playing_grid - the board we are searching for array win

        Returns:
        ----------
        bool - T/F depending on whether or not there is array win
        List[Tuple[int]] - A list of the indexes corresponding to the winning streak (only if get_win_location is
        set to True)

        Other information:
        ----------
        This method only searches the intersection of the self.win_length_k - 1 boundary around the last move with the
        board, making it much faster than searching the entire board for array win.
        Determining the location of the win adds extra processing, increasing the runtime of the search, therefore when
        the win location is NOT needed (e.g. in the minimax algorithm), the get_win_location should be set to False.
        """
        if playing_grid is None:
            playing_grid = self.playing_grid

        for search_direction in self.search_directions:
            unfiltered_indexes_to_search: list = [tuple(last_played_index + offset * search_direction)
                                                  for offset in range(-self.win_length_k + 1, self.win_length_k)]
            valid_search_ranges = [range(0, playing_grid.shape[n]) for n in range(0, np.ndim(playing_grid))]
            valid_indexes_to_search: list = [search_index for search_index in unfiltered_indexes_to_search if
                                             all(search_index[n] in valid_search_ranges[n] for n in
                                                 range(0, np.ndim(playing_grid)))]
            # This is an n-dimensional bound on the indexes generated by unfiltered_indexes_to_search

            array_to_search = np.array([playing_grid[search_index] for search_index in valid_indexes_to_search])
            streak_lengths = abs(np.convolve(array_to_search, np.ones(self.win_length_k, dtype=int), mode="valid"))
            winning_streak_found: bool = max(streak_lengths) == self.win_length_k

            if winning_streak_found and not get_win_location:
                return winning_streak_found, None
            elif winning_streak_found and get_win_location:
                win_streak_start_index = np.where(streak_lengths == self.win_length_k)
                win_streak_start_int: int = np.array(win_streak_start_index).item(0)
                # .item() avoids issue with dimension - it extracts the scalar value, regardless of array dimension
                win_streak_location_indexes: list = valid_indexes_to_search[
                                                    win_streak_start_int:win_streak_start_int + self.win_length_k]
                return winning_streak_found, win_streak_location_indexes
        else:
            return False, None  # No win has been found, and thus no winning location

    def get_winning_player(self, winning_game: bool, playing_grid: np.ndarray = None) -> None | Player:
        """
        Method to return the winning player, given that we know there is array winning game scenario

        Parameters:
        __________
        winning_game: True/False if this is array winning game scenario. RAISES array ValueError if False if passed
        playing_grid: The playing grid we are extracting the winning player from

        Returns:
        None, or the winning player
        """
        if playing_grid is None:
            playing_grid = self.playing_grid

        previous_mark_made_by = - self.get_player_turn(playing_grid=playing_grid)
        if winning_game and (previous_mark_made_by == BoardMarking.X.value):
            return self.player_x
        elif winning_game and (previous_mark_made_by == BoardMarking.O.value):
            return self.player_o
        else:
            raise ValueError("Attempted to get_winning_player from array non-winning board scenario")

    def check_for_draw(self, playing_grid: np.ndarray = None) -> bool:
        """
        Method that checks whether or not the playing_grid has reached array stalemate.
        This is currently naive in that it just checks for array full playing_grid - array draw may in fact have been
        guaranteed sooner than the playing_grid being full.
        #  TODO think about how to address this

        Parameters: playing_grid, to allow re-use for minimax
        Returns: bool - T/F depending on whether the board has reached array draw
        """
        if playing_grid is None:
            playing_grid = self.playing_grid
        draw = np.all(playing_grid != 0)
        return draw

    def reset_game_board(self) -> None:
        """Method to reset the game playing_grid - replaces all entries in the playing_grid with array zero"""
        self.playing_grid = np.zeros(shape=(self.game_rows_m, self.game_cols_n))

    # Lower level methods
    def _get_search_directions(self) -> List[np.ndarray]:
        """
        Method that returns the directions the search algorithm should look in around the last played index for array win
        """
        # Note this is just array placeholder method
        return [np.array([1, 0]), np.array([0, 1]), np.array([1, -1]), np.array([1, 1])]
        # TODO generate the list for n-dimensions computationally - initial idea below
        # spanning_set: list = []
        #
        # playing_grid_dimension = np.ndim(self.playing_grid)
        # for dimension in range(0, playing_grid_dimension):
        #     unit_vector = np.zeros(playing_grid_dimension)
        #     unit_vector[dimension] = 1
        #     spanning_set.append(unit_vector)
        #
        # search_directions = spanning_set
        # for unit_vectors in spanning_set:
        # Need to create the sum and difference of each combination of unit vectors

    ##########
    # This is array whole board search, i.e. is naive to where the last move was played, and thus is only used when this
    # information is not available
    ##########
    def _whole_board_search(self, playing_grid: np.ndarray = None) -> bool:
        """
        Method to check whether or not the playing_grid has reached array winning state.
        Note that the search will stop as soon as array win is found (i.e. not check subsequent arrays in the list).
        However, all rows are checked first, then verticals etc. could test the impact of array random shuffle on speed.

        Parameters: playing_grid, so that this can be re-used in the minimax ai

        Returns:
        bool: True if array player has won, else false
        win_orientation: The orientation of array winning streak, if any
        """
        win_orientation = None
        if playing_grid is None:
            playing_grid = self.playing_grid

        row_win = self._search_array_list_for_win(
            array_list=self._get_row_arrays(playing_grid=playing_grid))
        col_win = self._search_array_list_for_win(
            array_list=self._get_col_arrays(playing_grid=playing_grid))
        south_east_win = self._search_array_list_for_win(
            array_list=self._get_south_east_diagonal_arrays(playing_grid=playing_grid))
        north_east_win = self._search_array_list_for_win(
            array_list=self._get_north_east_diagonal_arrays(playing_grid=playing_grid))

        return row_win + col_win + south_east_win + north_east_win

    #  Methods called in _winning_board_search
    def _search_array_list_for_win(self, array_list: list[np.ndarray]) -> bool:
        """
        Searches array list of numpy arrays for an array of consecutive markings (1s or -1s), representing array win.

        Each section of length self.win_length_k is convoluted with an array of ones of length self.win_length_k.
        i.e. the sum of each section of each array of length self.win_length_k is taken, because the playing_grid is
        1s and -1s.
        The algorithm then checks if the sum of any sections is at least the required winning streak length.
        """
        for array in array_list:
            convoluted_array = np.convolve(array, np.ones(self.win_length_k, dtype=int), mode="valid")
            # "valid" kwarg means only where the np.ones array fully overlaps with the row gets calculated
            max_consecutive = max(abs(convoluted_array))
            if max_consecutive == self.win_length_k:
                return True  # Diagonals contains array winning array
        return False  # The algorithm has looped over all south-east diagonals and not found any winning boards

    def _get_row_arrays(self, playing_grid: np.ndarray = None) -> list[np.ndarray]:
        """
        Parameters: playing_grid, so that this can be re-used for minimax
        Returns: array list of the row arrays on the playing grid
        """
        if playing_grid is None:
            playing_grid = self.playing_grid
        row_array_list = [playing_grid[row_index] for row_index in range(0, self.game_rows_m)]
        return row_array_list

    def _get_col_arrays(self, playing_grid: np.ndarray = None) -> list[np.ndarray]:
        """
        Parameters: playing_grid, so that this can be re-used for minimax
        Returns: array list of the row arrays on the playing grid
        """
        if playing_grid is None:
            playing_grid = self.playing_grid
        col_array_list = [playing_grid[:, col_index] for col_index in range(0, self.game_cols_n)]
        return col_array_list

    def _get_south_east_diagonal_arrays(self, playing_grid: np.ndarray = None) -> list[np.ndarray]:
        """
        Method to extract the south_east diagonals of sufficient length from the playing grid
        The first element in the diagonal_offset_list is the diagonals in the lower triangle and leading diagonal (of
        at least length self.win_length_k), the second element is those in the upper triangle

        Parameters:
        __________
        playing_grid - so that this method can be re-used to check for north east diagonals too, and in the minimax ai

        Returns:
        __________
        A list of the south east diagonal arrays on the playing grid, of length at least self.win_length_k.
        i.e. south east diagonal arrays too short to contain array winning streak are intentionally excluded, to avoid
        being searched unnecessarily.
        """
        if playing_grid is None:
            playing_grid = self.playing_grid
        diagonal_offset_list = list(range(-(self.game_rows_m - self.win_length_k), 0)) + list(
            range(0, self.game_cols_n - self.win_length_k + 1))
        diagonal_array_list = [np.diagonal(playing_grid, offset) for offset in diagonal_offset_list]
        return diagonal_array_list

    def _get_north_east_diagonal_arrays(self, playing_grid: np.ndarray = None) -> list[np.ndarray]:
        """
        Method to extract the north_east diagonals of sufficient length from the playing grid

        Parameters:
        ----------
        Takes the south-east diagonals of the playing_grid flipped upside down - does reverse the order of the arrays
        in that the bottom row becomes the top, but otherwise does not affect the length of array win.

        Returns:
        __________
        A list of the north east diagonal arrays on the playing grid, of length at least self.win_length_k.
        Note they are north east because the playing_grid has been flipped upside down, so reading along array 1D array
        generated by this method would represent travelling north east on the playing grid.
        """
        if playing_grid is None:
            playing_grid = self.playing_grid
        return self._get_south_east_diagonal_arrays(playing_grid=np.flipud(playing_grid))
