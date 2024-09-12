import json
import os
import sqlite3
import sys
from tkinter import ttk
import chess  # type: ignore
import chess.pgn  # type: ignore

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helper.helper_methods import hash_fen

class ChessDatabase:
    def __init__(self):
        self.db_path = '/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/database/chess_db.sqlite'
        self.conn = self.connect_to_database()  
        if self.conn:
            self.cursor = self.conn.cursor()
            self.create_tables()
        else:
            print("Nije moguće uspostaviti vezu s bazom podataka.")

    def connect_to_database(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Greška pri povezivanju s bazom podataka: {e}")
            return None

    def create_tables(self):
        self.cursor.execute('''
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

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fens (
                game_id INTEGER,
                move_number INTEGER,
                fen TEXT,
                fen_hash TEXT,
                FOREIGN KEY(game_id) REFERENCES games(id)
            )
        ''')

        self.cursor.execute('''
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

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS my_analyzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            white TEXT,
            black TEXT,
            result TEXT,
            white_elo INTEGER,
            black_elo INTEGER,
            date TEXT,
            tournament TEXT,
            round TEXT,
            notation TEXT
        )
        ''')
        self.conn.commit()

    def close_connection(self):
        """Zatvara vezu s bazom podataka."""
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def database_exists_and_has_data(self):
        """Provjerava postoji li baza podataka i ima li tablica games podatke."""
        self.cursor.execute("SELECT COUNT(*) FROM games")
        result = self.cursor.fetchone()
        return result[0] > 0

    def save_to_gamesTable_database(self, cursor, game_data):
        insert_query = '''
            INSERT INTO games (site, date, round, white, black, result, white_elo, black_elo, eco, event_date, notation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_query, (
            game_data['Site'], game_data['Date'], game_data['Round'],
            game_data['White'], game_data['Black'], game_data['Result'],
            game_data['WhiteElo'], game_data['BlackElo'],
            game_data['ECO'], game_data['EventDate'], game_data['Notation']
        ))
        
        return cursor.lastrowid
    
    def save_fens_to_database(self, cursor, game_id, fens):
        insert_query = '''
            INSERT INTO fens (game_id, move_number, fen, fen_hash)
            VALUES (?, ?, ?, ?)
        '''
        cursor.executemany(insert_query, [
            (game_id, fen['move_number'], fen['fen'], fen['fen_hash']) for fen in fens
        ])
    
    def save_analysis_to_database(self, game_data):
        insert_query = '''
            INSERT INTO my_analyzes (white, black, result, white_elo, black_elo, date, tournament, round, notation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(insert_query, (
            game_data['white'], game_data['black'], game_data['result'],
            game_data['white_elo'], game_data['black_elo'], game_data['date'],
            game_data['tournament'], game_data['round'], game_data['notation']
        ))
        self.conn.commit()

    def parse_pgn_and_store_in_db(self, pgn_file_path, batch_size=1000):
        conn = self.connect_to_database()
        cursor = conn.cursor()

        with open(pgn_file_path, "r", encoding="ISO-8859-1") as pgn_file:
            game = chess.pgn.read_game(pgn_file)
            while game:
                exporter = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
                notation = game.accept(exporter)

                board = chess.Board()
                fens = []
            
                fen = board.fen()
                fen_hash = hash_fen(fen)
                move_count = 0

                moves = list(game.mainline_moves())
                
                # Inicijalni FEN
                fens.append({
                    "move_number": move_count,
                    "fen": fen,
                    "fen_hash": fen_hash
                })

                move_count += 1

                for idx, move in enumerate(moves):
                    try:
                        if board.is_legal(move):
                            board.push(move)
                        else:
                            print(f"nelegalan potez {move}. Preskacem partiju")
                            break
                    except AssertionError as e:
                        print(f"Greška prilikom primjene poteza {move}. Trenutni FEN: {board.fen()}. Greška {e}")
                        break

                    # Pripremi novi FEN
                    fen = board.fen()
                    fen_hash = hash_fen(fen)

                    fens.append({
                        "move_number": move_count,
                        "fen": fen,
                        "fen_hash": fen_hash
                    })

                    move_count += 1

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

                # Spremi partiju u bazu
                game_id = self.save_to_gamesTable_database(cursor, game_data)

                # Spremi FEN-ove u bazu
                self.save_fens_to_database(cursor, game_id, fens)

                # Učitaj sljedeću partiju
                game = chess.pgn.read_game(pgn_file)

        conn.commit()
        cursor.close()
        conn.close()

    def fetch_games_data_from_database(self):
        self.cursor.execute("SELECT * FROM games")
        rows = self.cursor.fetchall()
        return rows

    def display_data(self, table_frame):
        for widget in table_frame.winfo_children():
            widget.destroy()

        data = self.fetch_games_data_from_database()
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

            self.cursor.execute('''
                SELECT white, white_elo, black, black_elo, result, notation 
                FROM games 
                WHERE id = ?
            ''', (game_id,))
            game_data = self.cursor.fetchone()
            
            if game_data:
                white, white_elo, black, black_elo, result, notation = game_data

                from main_screen import analysis_board
                analysis_board.open_analysis_board_window(
                    notation=notation, 
                    white=white, 
                    white_elo=white_elo, 
                    black=black, 
                    black_elo=black_elo, 
                    result=result
                )
            else:
                print(f"Podaci za partiju s id {game_id} nisu pronađeni.")

        tree.bind("<Double-1>", on_item_click)

    # --- My Games --- 

    def parse_my_games_pgn(self, pgn_file_path):
        games_batch = []
        with open(pgn_file_path, "r", encoding="ISO-8859-1") as pgn_file:
            game = chess.pgn.read_game(pgn_file)
            while game:
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
                self.cursor.execute('''
                    INSERT INTO my_games (white, black, result, white_time, black_time, date, moves)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (game["White"], game["Black"], game["Result"], game["WhiteTime"], game["BlackTime"], game["Date"], game["Moves"]))

        self.conn.commit()

    def fetch_my_games_from_database(self):
        self.cursor.execute("SELECT id, white, black, result, white_time, black_time, date FROM my_games")
        rows = self.cursor.fetchall()
        return rows

    def display_my_games(self, table_frame):
        for widget in table_frame.winfo_children():
            widget.destroy()

        data = self.fetch_my_games_from_database()
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

            self.cursor.execute('''
                SELECT white, white_time, black, black_time, result, moves 
                FROM my_games 
                WHERE id = ?
            ''', (game_id,))
            game_data = self.cursor.fetchone()
            
            if game_data:
                white, white_time, black, black_time, result, moves = game_data

                from main_screen import analysis_board
                analysis_board.open_analysis_board_window(
                    notation=moves, 
                    white=white, 
                    white_elo=white_time, 
                    black=black, 
                    black_elo=black_time, 
                    result=result
                )
            else:
                print(f"Podaci za partiju s id {game_id} nisu pronađeni.")

        tree.bind("<Double-1>", on_item_click)

    def clear_my_games_table(self):
        self.cursor.execute('DELETE FROM my_games')
        self.conn.commit()
    
    # --- Reference --- 
    def get_game_data_for_fen(self, fen):
        conn = sqlite3.connect('/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/database/chess_db.sqlite')
        cursor = conn.cursor()

        # Query that finds all games that match the FEN
        cursor.execute('''
            SELECT g.id, g.white, g.black, g.white_elo, g.black_elo, g.result, g.event_date, g.site, g.date, g.notation
            FROM games AS g
            JOIN fens AS f ON g.id = f.game_id
            WHERE f.fen_hash = ?
        ''', (fen,))
        
        games = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return games
    
    def get_move_number_for_fen(self, fen):
        conn = sqlite3.connect('/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/database/chess_db.sqlite')
        cursor = conn.cursor()

        # Query that finds all games that match the FEN and also fetches the move_number from fens
        cursor.execute('''
            SELECT f.game_id, f.move_number
            FROM fens AS f
            WHERE f.fen_hash = ?
        ''', (fen,))
        
        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return result
    
    def get_game_on_click(self, game_id):
        conn = sqlite3.connect('/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/database/chess_db.sqlite')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT white, white_elo, black, black_elo, result, notation 
            FROM games 
            WHERE id = ?
        ''', (game_id,))
        game_data = cursor.fetchone()
                
        cursor.close()
        conn.close()
        
        return game_data