import os
import sqlite3
import sys
from tkinter import ttk
import chess # type: ignore
import chess.pgn # type: ignore

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main_screen import chess_board

def connect_to_database():
    db_path = '/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/database/chess_db.sqlite'
    
    # Kreiramo direktorij ako ne postoji
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    return sqlite3.connect(db_path)

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

            game = chess.pgn.read_game(pgn_file)

        if games_batch:
            save_batch_to_database(cursor, games_batch)

    conn.commit()
    cursor.close()
    conn.close()

def fetch_games_data_from_database():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games")
    rows = cursor.fetchall()
    conn.close()
    return rows

def display_data(table_frame):
    for widget in table_frame.winfo_children():
        widget.destroy()

    data = fetch_games_data_from_database()
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
        chess_board.open_game_window(game_id, "games")  

    tree.bind("<Double-1>", on_item_click)

def create_my_games_table():
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS my_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            white TEXT,
            black TEXT,
            result TEXT,
            white_time TEXT,
            black_time TEXT,
            date TEXT,
            moves TEXT
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def parse_my_games_pgn(pgn_file_path):
    conn = connect_to_database()
    cursor = conn.cursor()

    games_batch = []
    with open(pgn_file_path, "r", encoding="ISO-8859-1") as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        while game:
            # Pravilno dobivanje notacije u PGN formatu
            exporter = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
            notation = game.accept(exporter)

            game_data = {
                "White": game.headers.get("White", ""),
                "Black": game.headers.get("Black", ""),
                "Result": game.headers.get("Result", ""),
                "WhiteTime": game.headers.get("WhiteTime", ""),
                "BlackTime": game.headers.get("BlackTime", ""),
                "Date": game.headers.get("Date", ""),
                "Moves": notation.strip()
            }

            games_batch.append(game_data)

            game = chess.pgn.read_game(pgn_file)

        for game in games_batch:
            cursor.execute('''
                INSERT INTO my_games (white, black, result, white_time, black_time, date, moves)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (game["White"], game["Black"], game["Result"], game["WhiteTime"], game["BlackTime"], game["Date"], game["Moves"]))

    conn.commit()
    cursor.close()
    conn.close()

def fetch_my_games_from_database():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id, white, black, result, white_time, black_time, date FROM my_games")
    rows = cursor.fetchall()
    conn.close()
    return rows

def display_my_games(table_frame):
    # Očisti prethodni sadržaj
    for widget in table_frame.winfo_children():
        widget.destroy()

    data = fetch_my_games_from_database()
    tree = ttk.Treeview(table_frame, columns=("Number", "White", "Black", "Result", "WhiteTime", "BlackTime", "Date"), show="headings", height=15)
    
    tree.heading("Number", text="Number")
    tree.heading("White", text="White")
    tree.heading("Black", text="Black")
    tree.heading("Result", text="Result")
    tree.heading("WhiteTime", text="White Time")
    tree.heading("BlackTime", text="Black Time")
    tree.heading("Date", text="Date")

    for i, (game_id, white, black, result, white_time, black_time, date) in enumerate(data):
        tree.insert("", "end", values=(game_id, white, black, result, white_time, black_time, date))
    
    tree.pack(side="top", fill="x")

    def on_item_click(event):
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, "values")
        game_id = values[0]
        chess_board.open_game_window(game_id, "my_games")

    tree.bind("<Double-1>", on_item_click)

def clear_my_games_table():
    conn = connect_to_database()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM my_games')
    
    conn.commit()
    cursor.close()
    conn.close()