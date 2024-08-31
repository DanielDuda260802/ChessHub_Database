import io
import sys
import os

# dodana putanja do ostalih datoteka
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helper.helper_methods import load_and_resize_image

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import chess.pgn
import chess_board
import config
import playVsComputerSetupScreen

# UI komponente
def create_appbar(root):
    appbar = tk.Frame(root, bg=config.appbar_color, height=50)
    appbar.pack(side="top", fill="x")
    app_title = tk.Label(appbar, text="ChessHub", bg=config.appbar_color, fg="#F2CA5C", font=config.app_title_font)
    app_title.pack(pady=10)
    return appbar

def create_content_frame(root):
    content_frame = tk.Frame(root, bg=config.background_color)
    content_frame.pack(pady=20, padx=20, anchor="w", side="top", fill="x")
    return content_frame

def create_horizontal_line(parent_frame, color="#660000"):
    line = tk.Frame(parent_frame, bg=color, height=2)
    line.pack(side="top", fill="x", pady=10)
    return line

def create_vertical_line(parent_frame, color="#660000"):
    line = tk.Frame(parent_frame, bg=color, width=2)
    line.pack(side="left", fill="y", padx=10)
    return line

def create_play_vs_computer_button(parent_frame):
    button_frame = tk.Frame(parent_frame, bg="#660000", padx=4, pady=4)
    button_frame.pack(side="left", padx=10)

    playVsComputer_btn = tk.Button(button_frame, text="Play vs Computer", bg=config.button_color, fg=config.button_text_color, font=config.button_font, height=2, width=20, bd=0, command=playVsComputerSetupScreen.open_play_vs_computer_window)
    playVsComputer_btn.pack()
    
    return playVsComputer_btn

def create_icon_with_label(parent_frame, image_path, image_size, text):
    image = load_and_resize_image(image_path, image_size)
    icon_photo = ImageTk.PhotoImage(image)
    frame = tk.Frame(parent_frame, bg=config.background_color)
    frame.pack(side="left", padx=30)
    icon = tk.Label(frame, image=icon_photo, bg=config.background_color)
    icon.image = icon_photo
    icon.pack(side="top")
    label = tk.Label(frame, text=text, bg=config.background_color, fg=config.button_text_color, font=config.label_font)
    label.pack(side="top")
    return frame

# Funkcionalnost baze podataka
def connect_to_database():
    return sqlite3.connect('chess_db.sqlite')

def save_batch_to_database(cursor, games_batch):
    insert_query = '''
        INSERT INTO games (site, date, round, white, black, result, white_elo, black_elo, eco, event_date, notation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    data_to_insert = [
        (
            game['Site'], game['Date'], game['Round'], 
            game['White'], game['Black'], game['Result'], 
            game['WhiteElo'], game['BlackElo'], 
            game['ECO'], game['EventDate'], game['Notation']
        )
        for game in games_batch
    ]
    cursor.executemany(insert_query, data_to_insert)


def parse_pgn_and_store_in_db(pgn_file_path, batch_size=1000):
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT,
            date TEXT,
            round TEXT,
            white TEXT,
            black TEXT,
            result TEXT,
            white_elo INTEGER,
            black_elo INTEGER,
            eco TEXT,   
            event_date TEXT,
            notation TEXT
        )
    ''')

    games_batch = []
    with open(pgn_file_path, "r", encoding="ISO-8859-1") as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        while game:
            # Pravilno dobivanje notacije u PGN formatu
            exporter = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
            notation = game.accept(exporter)

            game_data = {
                "Site": game.headers.get("Site", ""),
                "Date": game.headers.get("Date", ""),
                "Round": game.headers.get("Round", ""),
                "White": game.headers.get("White", ""),
                "Black": game.headers.get("Black", ""),
                "Result": game.headers.get("Result", ""),
                "WhiteElo": game.headers.get("WhiteElo", ""),
                "BlackElo": game.headers.get("BlackElo", ""),
                "ECO": game.headers.get("ECO", ""),
                "EventDate": game.headers.get("EventDate", ""),
                "Notation": notation.strip()
            }

            games_batch.append(game_data)

            if len(games_batch) >= batch_size:
                save_batch_to_database(cursor, games_batch)
                games_batch = []

            # Čitaj sledeću partiju
            game = chess.pgn.read_game(pgn_file)

        if games_batch:
            save_batch_to_database(cursor, games_batch)

    conn.commit()
    cursor.close()
    conn.close()

def fetch_data_from_database():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games")
    rows = cursor.fetchall()
    conn.close()
    return rows

def display_data(table_frame):
    data = fetch_data_from_database()
    tree = ttk.Treeview(table_frame, columns=("Number", "White", "Elo W", "Black", "Elo B", "Result", "Site", "Date"), show="headings", height=15)
    tree.heading("Number", text="Number")
    tree.heading("White", text="White")
    tree.heading("Elo W", text="Elo W")
    tree.heading("Black", text="Black")
    tree.heading("Elo B", text="Elo B")
    tree.heading("Result", text="Result")
    tree.heading("Site", text="Site")
    tree.heading("Date", text="Date")
    for i, (game_id, site, date, round, white, black, result, white_elo, black_elo, eco, event_date, notation) in enumerate(data):
        tree.insert("", "end", values=(game_id, white, white_elo, black, black_elo, result, site, date))
    tree.pack(side="top", fill="x")

    def on_item_click(event):
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, "values")
        game_id = values[0]
        chess_board.open_game_window(game_id)

    tree.bind("<Double-1>", on_item_click)

def create_icon_with_table_button(content_frame, table_frame, image_path, image_size, text):
    icon_image = load_and_resize_image(image_path, image_size)
    icon_photo = ImageTk.PhotoImage(icon_image)
    icon_button = tk.Button(content_frame, image=icon_photo, text=text, compound="top", command=lambda: display_data(table_frame))
    icon_button.image = icon_photo
    icon_button.pack(side="left", padx=20)

root = tk.Tk()
root.title("ChessHub")
screen_width, screen_height = config.get_screen_dimensions(root)
root.geometry(f"{screen_width}x{screen_height}")
root.configure(bg=config.background_color)

create_appbar(root)
content_frame = create_content_frame(root)
table_frame = tk.Frame(root, bg=config.background_color)
table_frame.pack(side="bottom", fill="x", expand=False)

parse_pgn_and_store_in_db(config.pgn_file_path)

create_play_vs_computer_button(content_frame)
create_vertical_line(content_frame)
create_icon_with_label(content_frame, config.analysis_board_image_path, (76, 76), "Analysis board")
create_vertical_line(content_frame)
create_icon_with_label(content_frame, config.find_player_image_path, (94, 94), "Find Player")
create_horizontal_line(root)
create_vertical_line(content_frame)
create_icon_with_table_button(content_frame, table_frame, config.chessHubDabase_image_path, (100,100), "ChessHub Database")

root.mainloop()
