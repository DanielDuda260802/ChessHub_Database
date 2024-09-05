import tkinter as tk
from PIL import Image, ImageTk
import chess # type: ignore
import chess.svg # type: ignore
import sqlite3
import chess.pgn # type: ignore
import io
import re

import sys
import os

# Dodana putanja do ostalih datoteka
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helper import config
from helper.helper_methods import board_to_image
from helper import database_utils

def open_game_window(game_id, source_table):
    conn = database_utils.connect_to_database()
    cursor = conn.cursor()

    if source_table == "games":
        cursor.execute("SELECT white, white_elo, black, black_elo, result, notation FROM games WHERE id=?", (game_id,))
        game_data = cursor.fetchone()
        white, white_elo, black, black_elo, result, notation = game_data
    elif source_table == "my_games":
        cursor.execute("SELECT white, black, result, white_time, black_time, date, moves FROM my_games WHERE id=?", (game_id,))
        game_data = cursor.fetchone()
        white, black, result, white_time, black_time, date, notation = game_data
        white_elo, black_elo = white_time, black_time  # Ovdje ćemo prikazati vrijeme umjesto Elo ocjene

    conn.close()

    # Kreiraj novi prozor za prikaz igre
    new_window = tk.Toplevel()
    new_window.title(f"Game: {white} vs {black}")
    screen_width, screen_height = config.get_screen_dimensions(new_window)
    new_window.geometry(f"{screen_width}x{screen_height}")
    
    # Frame za prikaz ploče
    board_frame = tk.Frame(new_window, width=int(screen_width * 0.60), height=screen_height, bg="#660000")
    board_frame.pack(side="left", padx=0, pady=0, fill="both", expand=True)
    
    # Kreiranje šahovske ploče
    board = chess.Board()
    current_move_index = 0

    # Učitavanje notacije kao PGN ili sekvencija poteza
    pgn = io.StringIO(notation)
    game = chess.pgn.read_game(pgn)
    moves = list(game.mainline_moves()) if game else list(chess.pgn.read_headers(pgn))
    
    def update_board():
        new_board = chess.Board()
        for move in moves[:current_move_index]:
            new_board.push(move)
        board_image_path = board_to_image(new_board, size=900)
        board_image = ImageTk.PhotoImage(image=Image.open(board_image_path))
        board_label.config(image=board_image)
        board_label.image = board_image
        update_notation_text()

    # Prikaz početne ploče
    board_image_path = board_to_image(board, size=900)
    board_image = ImageTk.PhotoImage(image=Image.open(board_image_path))
    board_label = tk.Label(board_frame, image=board_image)
    board_label.image = board_image
    board_label.pack(expand=True)

    # Info frame (za prikaz podataka)
    info_frame = tk.Frame(new_window, bg="#F8E7BB", width=int(screen_width * 0.35), relief="flat", bd=10)
    info_frame.pack(side="right", fill="y", expand=False, padx=0, pady=0)
    
    # Prikaz osnovnih informacija o igri
    if source_table == "games":
        info_text = f"{white} {white_elo} - {black} {black_elo}\n{result}\n\n"
    elif source_table == "my_games":
        info_text = f"{white} {white_elo} - {black} {black_elo}\n {result}"
    
    info_label = tk.Label(info_frame, text=info_text, bg="#F8E7BB", font=("Inter", 24, "bold"), anchor="center")
    info_label.pack(side="top", padx=10)

    # Prikaz notacije
    notation_text = tk.Text(info_frame, bg="#F8E7BB", wrap="word", font=("Inter", 16), bd=0, relief="flat")
    notation_text.insert("1.0", notation)
    notation_text.config(state="disabled") 
    notation_text.pack(side="top", fill="both", expand=True)

    # Navigacija između poteza
    nav_frame = tk.Frame(info_frame, bg="#F8E7BB")
    nav_frame.pack(side="bottom", padx=20)

    def prev_move():
        nonlocal current_move_index
        if current_move_index > 0:
            current_move_index -= 1
            update_board()

    def next_move():
        nonlocal current_move_index
        if current_move_index < len(moves):
            current_move_index += 1
            update_board()

    # Navigacijski gumbi
    prev_button = tk.Button(nav_frame, text="⟨", command=prev_move, font=("Inter", 24, "bold"), bg="#F2CA5C", fg="#660000", bd=0, width=20, height=2)
    prev_button.config(highlightbackground="#480202", highlightthickness=4)
    prev_button.pack(side="left", padx=10)

    next_button = tk.Button(nav_frame, text="⟩", command=next_move, font=("Inter", 24, "bold"), bg="#F2CA5C", fg="#660000", bd=0, width=20, height=2)
    next_button.config(highlightbackground="#480202", highlightthickness=4)
    next_button.pack(side="left")

    new_window.bind("<Left>", lambda event: prev_move())
    new_window.bind("<Right>", lambda event: next_move())

    # Ažuriraj notaciju kod promjene poteza
    def update_notation_text():
        notation_text.config(state="normal") 
        notation_text.delete("1.0", "end")  

        notation_list = notation.split()
        move_index = 0  # Brojimo samo stvarne poteze (ne i brojeve poteza)
        tag_map = {}  # Mapa za praćenje tagova po potezima

        def on_click(event):
            index = notation_text.index(f"@{event.x},{event.y}")
            clicked_tag = notation_text.tag_names(index)

            if clicked_tag and clicked_tag[0].startswith("move_"):
                nonlocal current_move_index
                current_move_index = int(clicked_tag[0].split("_")[1]) + 1
                update_board()

        notation_text.bind("<Button-1>", on_click)

        for i, move in enumerate(notation_list):
            current_position = notation_text.index("end-1c")

            if move.endswith('.'):  # Ako je trenutni element broj poteza (npr. "1.")
                notation_text.insert(current_position, f"{move} ")
            else:
                start_idx = notation_text.index("end-1c")
                notation_text.insert(start_idx, f"{move} ")
                end_idx = notation_text.index("end-1c")

                # Dodajemo tag za svaki potez sa identifikatorom
                tag_name = f"move_{move_index}"
                notation_text.tag_add(tag_name, start_idx, end_idx)
                tag_map[move_index] = tag_name

                if move_index == current_move_index - 1: 
                    notation_text.tag_add("highlight", start_idx, end_idx)

                move_index += 1

        notation_text.tag_config("highlight", font=("Inter", 16, "bold")) 
        notation_text.config(state="disabled")
