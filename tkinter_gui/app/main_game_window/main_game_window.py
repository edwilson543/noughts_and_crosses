from game.app.player_base_class import Player
from game.constants.game_constants import GameValue
from tkinter_gui.constants.dimensions import FrameDimensions
from tkinter_gui.constants.style_and_colours import Colour
from tkinter_gui.app.main_game_window.active_game_frames import ActiveGameFrames
from tkinter_gui.app.main_game_window.historic_games_frame import HistoricInfoFrame
from tkinter_gui.app.main_game_window.widget_management import MainWindowWidgetManager
import tkinter as tk


class NoughtsAndCrossesWindow(ActiveGameFrames, HistoricInfoFrame):
    def __init__(self,
                 game_rows_m: int,
                 game_cols_n: int,
                 win_length_k: int,
                 pos_player: Player,
                 neg_player: Player,
                 starting_player: GameValue = GameValue.X,
                 draw_count: int = 0,
                 active_unconfirmed_cell: (int, int) = None,
                 widget_manager=MainWindowWidgetManager()):
        super().__init__(game_rows_m, game_cols_n, win_length_k, pos_player, neg_player, starting_player,
                         draw_count, active_unconfirmed_cell, widget_manager)

    def launch_playing_window(self):
        """Method for launching the main noughts and crosses game play window and controlling the game flow"""
        # Define and configure the window
        game_window = tk.Tk()
        game_window.title("Noughts and Crosses")
        game_window.configure(background=Colour.window.value)
        game_window.rowconfigure(index=0, weight=1)
        game_window.columnconfigure(index=0, weight=1)
        self.create_all_game_components(master_window=game_window)
        game_window.mainloop()

    def create_all_game_components(self, master_window: tk.Tk):
        """Method to create all the frames used in the main game window and fill the with their components"""
        # Background frame that contains all components of the game
        background_frame = tk.Frame(master=master_window, background=Colour.background.value, borderwidth=3,
                                    relief=tk.RIDGE)
        background_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        background_frame.rowconfigure(index=[0, 1], minsize=FrameDimensions.game_info_frame.height, weight=1)
        background_frame.columnconfigure(index=0, minsize=FrameDimensions.game_frame.width, weight=1)
        background_frame.columnconfigure(index=1, minsize=FrameDimensions.game_info_frame.width, weight=0)

        # Frame that contains the playing grid (entire left)
        self.widget_manager.playing_grid_frame = tk.Frame(
            master=background_frame, background=Colour.game_background.value,
            borderwidth=5, relief=tk.SUNKEN)
        self.widget_manager.playing_grid_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
        super().populate_empty_playing_grid()

        # Frame for the buttons that control the gameplay (top-right)
        self.widget_manager.game_info_frame = tk.Frame(
            master=background_frame, background=Colour.game_buttons_background.value,
            borderwidth=5, relief=tk.SUNKEN)
        self.widget_manager.game_info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        # active_game_frames_carrier.populate_game_info_grid()
        super().populate_game_info_grid()

        # Frame for the labels that says the status across multiple games (bottom-right)
        self.widget_manager.historic_info_frame = tk.Frame(
            master=background_frame, background=Colour.game_status_background.value,
            borderwidth=5, relief=tk.SUNKEN)
        self.widget_manager.historic_info_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        super().populate_historic_info_grid()
