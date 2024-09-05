import datetime
import tkinter as tk
from PIL import Image, ImageTk
import chess  # type: ignore
import chess.engine  # type: ignore
import cairosvg  # type: ignore
import os
import sys
import threading
import time

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helper import config
import playVsComputerSetupScreen

class ChessGUI:
    def __init__(self, root, gameScreenWindow, board, flipped, player_color, white_time, black_time, white_increment, black_increment, level):
        self.board = board
        self.root = root
        self.gameScreenWindow = gameScreenWindow 
        self.flipped = flipped
        self.player_color = player_color
        self.level = level
        self.engine = None
        self.game_over = False

        self.white_time = int(white_time) * 60
        self.black_time = int(black_time) * 60
        self.white_increment = int(white_increment)
        self.black_increment = int(black_increment)

        self.timer_running = False

        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.selected_square = None
        self.highlighted_squares = []

        # Mapa razina (1-10) na Stockfish Skill Level (0-20)
        self.level_map = {
            "Level 1": {"skill_level": 0, "threads": 1, "hash": 8, "elo": 1320, "move_overhead": 400, "nodestime": 10, "limit_strength": True},
            "Level 2": {"skill_level": 2, "threads": 1, "hash": 16, "elo": 1400, "move_overhead": 300, "nodestime": 20, "limit_strength": True},
            "Level 3": {"skill_level": 4, "threads": 1, "hash": 64, "elo": 1600, "move_overhead": 200, "nodestime": 40, "limit_strength": True},
            "Level 4": {"skill_level": 6, "threads": 1, "hash": 128, "elo": 1800, "move_overhead": 150, "nodestime": 80, "limit_strength": True},
            "Level 5": {"skill_level": 9, "threads": 2, "hash": 256, "elo": 2000, "move_overhead": 125, "nodestime": 160, "limit_strength": True},
            "Level 6": {"skill_level": 12, "threads": 2, "hash": 512, "elo": 2200, "move_overhead": 100, "nodestime": 320, "limit_strength": False},
            "Level 7": {"skill_level": 14, "threads": 4, "hash": 512, "elo": 2400, "move_overhead": 75, "nodestime": 400, "limit_strength": False},
            "Level 8": {"skill_level": 16, "threads": 4, "hash": 1024, "elo": 2600, "move_overhead": 50, "nodestime": 500, "limit_strength": False},
            "Level 9": {"skill_level": 18, "threads": 6, "hash": 1024, "elo": 2800, "move_overhead": 30, "nodestime": 600, "limit_strength": False},
            "Level 10": {"skill_level": 20, "threads": 8, "hash": 2048, "elo": 3000, "move_overhead": 20, "nodestime": 800, "limit_strength": False}
        }

        self.init_engine()

        self.init_time_labels(root)
        self.root.after(100, self.draw_board)
        self.canvas.bind("<Button-1>", self.on_click)
        self.start_timer()

    def init_engine(self):
        self.engine = chess.engine.SimpleEngine.popen_uci(config.STOCKFISH_PATH)

        # Dohvati postavke za odabranu razinu
        config_options = self.level_map[self.level]
        stockfish_skill_level = config_options["skill_level"]
        

        # Konfiguriranje motora s više opcija
        self.engine.configure({
            "Skill Level": stockfish_skill_level,
            "Threads": config_options["threads"],
            "Hash": config_options["hash"],
            "UCI_LimitStrength": config_options["limit_strength"],
            "UCI_Elo": config_options["elo"],
            "Move Overhead": config_options["move_overhead"],
            "nodestime": config_options["nodestime"]
        })

        print(f"Stockfish configured with: {config_options}")

    def start_timer(self):
        if self.board.turn == chess.WHITE:
            if self.player_color == chess.WHITE:
                self.start_white_timer()
            else:
                self.root.after(200, self.make_ai_move)
        else:
            if self.player_color == chess.BLACK:
                self.start_black_timer()
            else:
                self.root.after(200, self.make_ai_move)

    def init_time_labels(self, root):
        info_frame = root.master.winfo_children()[1]
        white_time_container = tk.Frame(info_frame, bg="#F8E7BB")
        white_time_container.grid(row=0, column=0, pady=20, padx=20, sticky="ew")

        white_color_box = tk.Label(white_time_container, bg="white", width=4, height=2, borderwidth=2, relief="solid")
        white_color_box.grid(row=0, column=0, padx=(0, 10))

        self.white_time_label = tk.Label(white_time_container, text=self.format_time(self.white_time), font=("Inter", 36), bg="#F8E7BB", fg="#000000", borderwidth=2, relief="solid", padx=10, pady=5)
        self.white_time_label.grid(row=0, column=1)

        black_time_container = tk.Frame(info_frame, bg="#F8E7BB")
        black_time_container.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        black_color_box = tk.Label(black_time_container, bg="black", width=4, height=2, borderwidth=2, relief="solid")
        black_color_box.grid(row=0, column=0, padx=(0, 10))

        self.black_time_label = tk.Label(black_time_container, text=self.format_time(self.black_time), font=("Inter", 36), bg="#F8E7BB", fg="#000000", borderwidth=2, relief="solid", padx=10, pady=5)
        self.black_time_label.grid(row=0, column=1)

    def board_to_image(self, size):
        arrows = [chess.svg.Arrow(square, square, color="#033313") for square in self.highlighted_squares]
        svg_data = chess.svg.board(board=self.board, size=size, flipped=self.flipped, arrows=arrows)
        output_path = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/assets/chessboard.png"
        cairosvg.svg2png(bytestring=svg_data, write_to=output_path)
        return output_path

    def draw_board(self):
        self.root.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.size = min(canvas_width, canvas_height)
        self.square_size = self.size // 8

        board_image_path = self.board_to_image(self.size)
        board_image = Image.open(board_image_path)
        board_image = board_image.resize((self.size, self.size), Image.LANCZOS)

        self.board_image = ImageTk.PhotoImage(board_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.board_image)

    def format_time(self, time_in_seconds):
        minutes = time_in_seconds // 60
        seconds = time_in_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def start_white_timer(self):
        self.timer_running = True
        self.white_timer = self.root.after(1000, self.update_white_time)

    def update_white_time(self):
        if self.timer_running and not self.game_over:
            self.white_time -= 1
            self.white_time_label.config(text=self.format_time(self.white_time))
            if self.white_time > 0:
                self.start_white_timer()
            else:
                self.end_game("White's time is up!")

    def pause_white_timer(self):
        if hasattr(self, 'white_timer'):
            self.root.after_cancel(self.white_timer)
        self.white_time += self.white_increment
        self.white_time_label.config(text=self.format_time(self.white_time))
        self.timer_running = False

    def start_black_timer(self):
        self.timer_running = True
        self.black_timer = self.root.after(1000, self.update_black_time)

    def update_black_time(self):
        if self.timer_running and not self.game_over:
            self.black_time -= 1
            self.black_time_label.config(text=self.format_time(self.black_time))
            if self.black_time > 0:
                self.start_black_timer()
            else:
                self.end_game("Black's time is up!")

    def pause_black_timer(self):
        if hasattr(self, 'black_timer'):
            self.root.after_cancel(self.black_timer)
        self.black_time += self.black_increment
        self.black_time_label.config(text=self.format_time(self.black_time))
        self.timer_running = False

    def on_click(self, event):
        if self.game_over:
            return

        col = event.x // self.square_size
        row = event.y // self.square_size

        if self.flipped:
            col = 7 - col
            row = 7 - row

        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)

            if self.board.turn == self.player_color:
                if self.selected_square is None:
                    if self.board.piece_at(square) and self.board.color_at(square) == self.player_color:
                        self.highlighted_squares = [
                            move.to_square for move in self.board.legal_moves if move.from_square == square
                        ]
                        if self.highlighted_squares:
                            self.selected_square = square
                        else:
                            self.selected_square = None
                            self.highlighted_squares = []
                    else:
                        self.selected_square = None
                        self.highlighted_squares = []
                else:
                    move = chess.Move(self.selected_square, square)
                    if move in self.board.legal_moves:
                        self.board.push(move)
                        self.selected_square = None
                        self.highlighted_squares = []
                        self.timer_running = False
                        self.pause_white_timer() if self.board.turn == chess.BLACK else self.pause_black_timer()
                        self.draw_board()
                        self.root.after(200, self.make_ai_move)
                    else:
                        self.selected_square = None
                        self.highlighted_squares = []
                self.draw_board()

    def make_ai_move(self):
        if self.game_over:
            return
        threading.Thread(target=self._run_ai_move, daemon=True).start()

    def _run_ai_move(self):
        if self.board.is_game_over() or self.game_over:
            self.end_game()
            return

        # Prilagodba time_limit ovisno o preostalom vremenu i razini
        if self.board.turn == chess.WHITE:
            self.start_white_timer()
        else:
            self.start_black_timer()

        # Koristi Limit koji uključuje preostalo vrijeme i dodatak
        limit = chess.engine.Limit(
            white_clock=self.white_time,
            black_clock=self.black_time,
            white_inc=self.white_increment,
            black_inc=self.black_increment
        )

        result = self.engine.play(self.board, limit)

        if self.game_over or self.board.is_game_over() or self.white_time <= 0 or self.black_time <= 0:
            return
        else:
            self.board.push(result.move)

        if self.board.turn == chess.WHITE:
            self.pause_black_timer()
            self.start_white_timer()
        else:
            self.pause_white_timer()
            self.start_black_timer()

        self.root.after(0, self.draw_board)

        if self.board.is_game_over():
            self.end_game()

    def end_game(self, message="Game over"):
        self.pause_timers()
        self.engine.quit()
        self.game_over = True
        result = self.get_game_result()
        self.show_result_menu(result, message)

    def pause_timers(self):
        self.timer_running = False
        self.pause_white_timer()
        self.pause_black_timer()

    def get_game_result(self):
        if self.white_time <= 0:
            return "0-1"
        elif self.black_time <= 0:
            return "1-0"
        if self.board.is_checkmate():
            return "0-1" if self.board.turn == chess.WHITE else "1-0"
        elif self.board.is_stalemate():
            return "1/2-1/2"
        elif self.board.is_insufficient_material():
            return "1/2-1/2"
        elif self.board.is_seventyfive_moves():
            return "1/2-1/2"
        elif self.board.is_fivefold_repetition():
            return "1/2-1/2"
        return "*"

    def show_result_menu(self, result, message):
        result_window = tk.Toplevel(self.root)
        result_window.title("Game Over")

        def new_game():
            result_window.destroy()
            self.gameScreenWindow.destroy()
            playVsComputerSetupScreen.open_play_vs_computer_window()

        def save_game():
            game = chess.pgn.Game()
            game.headers["White"] = "User" if self.player_color == chess.WHITE else f"Stockfish - {self.level}"
            game.headers["Black"] = "User" if self.player_color == chess.BLACK else f"Stockfish - {self.level}"
            game.headers["Result"] = self.get_game_result()
            game.headers["WhiteTime"] = self.format_time(self.white_time)
            game.headers["BlackTime"] = self.format_time(self.black_time)
            game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")

            node = game
            for move in self.board.move_stack:
                node = node.add_main_variation(move)

            pgn_file_path = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/MyGames.pgn"
            with open(pgn_file_path, "a") as pgn_file:
                print(game, file=pgn_file, end="\n\n")

        def close_and_leave():
            """Zatvara sve prozore i ponovno pokreće aplikaciju."""
            self.root.quit()
            self.root.destroy()

            python = sys.executable
            os.execl(python, python, *sys.argv)

        result_label = tk.Label(result_window, text=f"User vs Stockfish: {result}", font=("Inter", 24), pady=20)
        result_label.pack()

        message_label = tk.Label(result_window, text=message, font=("Inter", 16))
        message_label.pack(pady=10)

        button_style = {
            "font": ("Inter", 16),
            "bg": "#F2CA5C",
            "fg": "#660000",
            "width": 20,
            "height": 2,
            "borderwidth": 2,
            "relief": "solid",
            "highlightbackground": "#480202",
            "highlightthickness": 2
        }

        save_button = tk.Button(result_window, text="Save", command=save_game, **button_style)
        save_button.pack(side="left", padx=20, pady=20)

        newGame_button = tk.Button(result_window, text="New Game", command=new_game, **button_style)
        newGame_button.pack(side="left", padx=20, pady=20)

        cancel_button = tk.Button(result_window, text="Close and leave", command=close_and_leave, **button_style)
        cancel_button.pack(side="right", padx=20, pady=20)


def start_game_screen(color, white_time, white_increment, black_time, black_increment, level):
    gameScreenWindow = tk.Toplevel()
    gameScreenWindow.title(f"Play Vs Computer - {level}")
    screen_width, screen_height = config.get_screen_dimensions(gameScreenWindow)
    gameScreenWindow.geometry(f"{screen_width}x{screen_height}")
    gameScreenWindow.configure(bg="#F8E7BB")

    board_frame = tk.Frame(gameScreenWindow, width=int(screen_width * 0.80), height=screen_height, bg="#660000")
    board_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

    info_frame = tk.Frame(gameScreenWindow, bg="#F8E7BB", width=int(screen_width * 0.20), relief="flat", bd=10)
    info_frame.pack(side="right", fill="y", expand=True, padx=10, pady=10)

    board = chess.Board()

    flipped = True if color.lower() == "black" else False

    chess_gui = ChessGUI(board_frame, gameScreenWindow, board, flipped=flipped, player_color=chess.WHITE if color.lower() == "white" else chess.BLACK, white_time=white_time, black_time=black_time, white_increment=white_increment, black_increment=black_increment, level=level)

    resign_button = tk.Button(info_frame, text="Resign and Leave", font=("Inter", 16), bg="#F2CA5C", fg="#660000", width=20, height=2, borderwidth=2, relief="solid")
    resign_button.grid(row=3, column=0, pady=50, sticky="s")

    gameScreenWindow.mainloop()
