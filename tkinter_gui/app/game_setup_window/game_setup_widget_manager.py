from dataclasses import dataclass
import tkinter as tk

@dataclass(frozen=False)
class GameSetupWidgets:
    # Setup main_window
    setup_window: tk.Tk = None

    # Game parameters
    game_parameters_frame: tk.Frame = None
    game_rows_scale: tk.Scale = None
    game_rows_label: tk.Label = None
    game_cols_scale: tk.Scale = None
    game_cols_label: tk.Label = None
    win_length_scale: tk.Scale = None
    win_length_label: tk.Label = None

    # Player info
    player_info_frame: tk.Frame = None
    player_x_entry: tk.Entry = None
    player_o_entry: tk.Entry = None
    player_x_starts_radio: tk.Radiobutton = None
    player_o_starts_radio: tk.Radiobutton = None
    random_player_starts_radio: tk.Radiobutton = None

    # Universal
    confirmation_button: tk.Button = None
