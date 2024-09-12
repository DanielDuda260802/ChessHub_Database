import io
import os
import tkinter as tk
from tkinter import messagebox
import chess # type: ignore
import chess.pgn # type: ignore

from helper import database_utils
from helper import config

db = database_utils.ChessDatabase() 

def open_save_analysis_window(root, pgn_string):
    save_window = tk.Toplevel()
    save_window.title("Save Analysis")
    save_window.geometry("700x280")
    save_window.configure(bg="#F8E7BB")

    def validate_numeric_input(input_value):
        if input_value == "":
            return True
        if input_value.isdigit() and len(input_value) <= 4:
            return True
        return False

    def validate_date_input(input_value, max_value):
        if input_value.isdigit():
            return 1 <= int(input_value) <= max_value
        elif input_value == "":
            return True
        return False
    
    def validate_month_input(input_value):
        if input_value == "":
            return True
        if input_value.isdigit() and 1 <= int(input_value) <= 12 and len(input_value) <= 2:
            return True
        return False
    
    def validate_day_input(input_value):
        if input_value == "":
            return True
        if input_value.isdigit() and 1 <= int(input_value) <= 31 and len(input_value) <= 2:
            return True
        return False

    vcmd_numeric_elo = (save_window.register(validate_numeric_input), '%P')
    vcmd_numeric_year = (save_window.register(validate_numeric_input), '%P')
    vcmd_numeric_month = (save_window.register(validate_month_input), '%P')
    vcmd_numeric_day = (save_window.register(validate_day_input), '%P')

    labels = {
        "white": "White",
        "black": "Black",
        "tournament": "Tournament",
        "elo_white": "Elo white:",
        "elo_black": "Elo black:",
        "round": "Round:",
        "result": "Results:",
        "year": "Year:",
        "month": "Month:",
        "day": "Day:"
    }

    entry_vars = {}

    tk.Label(save_window, text=labels['white'], font=("Inter", 14), bg="#F8E7BB").grid(row=0, column=0, padx=20, pady=5, sticky="e")
    white_entry = tk.Entry(save_window, font=("Inter", 14))
    white_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w", columnspan=1)

    tk.Label(save_window, text=labels['black'], font=("Inter", 14), bg="#F8E7BB").grid(row=1, column=0, padx=20, pady=5, sticky="e")
    black_entry = tk.Entry(save_window, font=("Inter", 14))
    black_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w", columnspan=1)

    tk.Label(save_window, text=labels['tournament'], font=("Inter", 14), bg="#F8E7BB").grid(row=2, column=0, padx=20, pady=5, sticky="e")
    tournament_entry = tk.Entry(save_window, font=("Inter", 14))
    tournament_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w", columnspan=1)

    tk.Label(save_window, text=labels['result'], font=("Inter", 14), bg="#F8E7BB").grid(row=3, column=0, padx=20, pady=5, sticky="e")
    result_var = tk.StringVar(value="1-0")
    result_frame = tk.Frame(save_window, bg="#F8E7BB")
    result_frame.grid(row=3, column=1, columnspan=3, sticky="w")

    tk.Radiobutton(result_frame, text="1 - 0", variable=result_var, value="1-0", bg="#F8E7BB", font=("Inter", 14)).pack(side="left")
    tk.Radiobutton(result_frame, text="1/2 - 1/2", variable=result_var, value="1/2-1/2", bg="#F8E7BB", font=("Inter", 14)).pack(side="left", padx=5)
    tk.Radiobutton(result_frame, text="0 - 1", variable=result_var, value="0-1", bg="#F8E7BB", font=("Inter", 14)).pack(side="left", padx=5)

    tk.Label(save_window, text=labels['round'], font=("Inter", 14), bg="#F8E7BB").grid(row=4, column=0, padx=20, pady=5, sticky="e")
    round_entry = tk.Entry(save_window, font=("Inter", 14), width=10, validate="key", validatecommand=vcmd_numeric_month)
    round_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    tk.Label(save_window, text=labels['elo_white'], font=("Inter", 14), bg="#F8E7BB").grid(row=0, column=2, padx=30, pady=5, sticky="e")
    elo_white_entry = tk.Entry(save_window, font=("Inter", 14), width=10, validate="key", validatecommand=vcmd_numeric_elo)
    elo_white_entry.grid(row=0, column=3, padx=10, pady=5, sticky="w")

    tk.Label(save_window, text=labels['elo_black'], font=("Inter", 14), bg="#F8E7BB").grid(row=1, column=2, padx=30, pady=5, sticky="e")
    elo_black_entry = tk.Entry(save_window, font=("Inter", 14), width=10, validate="key", validatecommand=vcmd_numeric_elo)
    elo_black_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

    tk.Label(save_window, text=labels['year'], font=("Inter", 14), bg="#F8E7BB").grid(row=2, column=2, padx=30, pady=5, sticky="e")
    year_entry = tk.Entry(save_window, font=("Inter", 14), width=10, validate="key", validatecommand=vcmd_numeric_year)
    year_entry.grid(row=2, column=3, padx=10, pady=5, sticky="w")

    tk.Label(save_window, text=labels['month'], font=("Inter", 14), bg="#F8E7BB").grid(row=3, column=2, padx=30, pady=5, sticky="e")
    month_entry = tk.Entry(save_window, font=("Inter", 14), width=10, validate="key", validatecommand=vcmd_numeric_month)
    month_entry.grid(row=3, column=3, padx=10, pady=5, sticky="w")

    tk.Label(save_window, text=labels['day'], font=("Inter", 14), bg="#F8E7BB").grid(row=4, column=2, padx=30, pady=5, sticky="e")
    day_entry = tk.Entry(save_window, font=("Inter", 14), width=10, validate="key", validatecommand=vcmd_numeric_day)
    day_entry.grid(row=4, column=3, padx=10, pady=5, sticky="w")

    button_frame = tk.Frame(save_window, bg="#F8E7BB")
    button_frame.grid(row=5, column=0, columnspan=6, pady=20)

    save_button = tk.Button(button_frame, text="Save", font=("Inter", 14), bg="#F2CA5C", width=10,
                            command=lambda: save_analysis(entry_vars, pgn_string, save_window))
    save_button.pack(side="left", padx=10)
    
    reset_button = tk.Button(button_frame, text="Reset", font=("Inter", 14), bg="#F2CA5C", width=10, command=lambda: reset_fields(entry_vars))
    reset_button.pack(side="left", padx=10)

    cancel_button = tk.Button(button_frame, text="Discard", font=("Inter", 14), bg="#F2CA5C", width=10, command=save_window.destroy)
    cancel_button.pack(side="left", padx=10)

    entry_vars['white'] = white_entry
    entry_vars['black'] = black_entry
    entry_vars['tournament'] = tournament_entry
    entry_vars['round'] = round_entry
    entry_vars['result'] = result_var
    entry_vars['elo_white'] = elo_white_entry
    entry_vars['elo_black'] = elo_black_entry
    entry_vars['year'] = year_entry
    entry_vars['month'] = month_entry
    entry_vars['day'] = day_entry

    save_window.transient(root)
    save_window.grab_set()
    root.wait_window(save_window)


def save_analysis(entry_vars, pgn_string, save_window):
    # Dohvaćanje unesenih podataka
    analysis_data = {key: var.get() if isinstance(var, tk.Entry) else var.get() for key, var in entry_vars.items()}

    try:
        game = chess.pgn.Game()

        game.headers["White"] = analysis_data["white"]
        game.headers["Black"] = analysis_data["black"]
        game.headers["Event"] = analysis_data["tournament"]
        game.headers["WhiteElo"] = analysis_data["elo_white"]
        game.headers["BlackElo"] = analysis_data["elo_black"]
        game.headers["Round"] = analysis_data["round"]
        game.headers["Result"] = analysis_data["result"]
        game.headers["Date"] = f"{analysis_data['year']}.{analysis_data['month']}.{analysis_data['day']}"

        moves = chess.pgn.read_game(io.StringIO(pgn_string))
        
        def add_variations(source_node, target_node):
            for move in source_node.variations:
                new_node = target_node.add_variation(move.move)
                add_variations(move, new_node)

        add_variations(moves, game)

        pgn_file_path = config.my_analyzes_pgn_file_path

        if not os.path.exists(pgn_file_path):
            os.makedirs(pgn_file_path)

        with open(pgn_file_path, "a") as pgn_file:
            print(game, file=pgn_file, end="\n\n")

        game_data = {
            'white': analysis_data["white"],
            'black': analysis_data["black"],
            'result': analysis_data["result"],
            'white_elo': analysis_data["elo_white"],
            'black_elo': analysis_data["elo_black"],
            'date': f"{analysis_data['year']}.{analysis_data['month']}.{analysis_data['day']}",
            'tournament': analysis_data["tournament"],
            'round': analysis_data["round"],
            'notation': pgn_string
        }
        db.save_analysis_to_database(game_data)

        save_window.destroy()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save analysis: {e}")

def reset_fields(entry_vars):
    for var in entry_vars.values():
        if isinstance(var, tk.Entry):
            var.delete(0, tk.END)
        elif isinstance(var, tk.StringVar):
            var.set("1-0")
