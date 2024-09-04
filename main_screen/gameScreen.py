import tkinter as tk
from PIL import Image, ImageTk
import chess
import chess.engine
import cairosvg
import os
import sys
import threading

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import config

class ChessGUI:
    def __init__(self, root, board, flipped, player_color, white_time, black_time, white_increment, black_increment):
        self.board = board
        self.root = root
        self.flipped = flipped
        self.player_color = player_color
        self.engine = None
        self.game_over = False  # Dodano za provjeru je li igra završena

        self.white_time = int(white_time) * 60
        self.black_time = int(black_time) * 60
        self.white_increment = int(white_increment)
        self.black_increment = int(black_increment)

        self.timer_running = False

        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.selected_square = None
        self.highlighted_squares = []

        self.engine = chess.engine.SimpleEngine.popen_uci("/home/daniel/Desktop/stockfish/stockfish-ubuntu-x86-64-avx2")

        self.init_time_labels(root)
        self.root.after(100, self.draw_board)
        self.canvas.bind("<Button-1>", self.on_click)
        self.start_timer()

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
        if self.game_over:  # Onemogućavanje daljnjih poteza
            return

        col = event.x // self.square_size
        row = event.y // self.square_size

        if self.flipped:
            col = 7 - col
            row = 7 - row

        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)
            print(f"Clicked on square: {chess.square_name(square)}")

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
        if self.game_over:  # Ako je igra već gotova, AI ne treba igrati
            return
        threading.Thread(target=self._run_ai_move, daemon=True).start()

    def _run_ai_move(self):
        if self.board.is_game_over() or self.game_over: 
            return

        if self.board.turn == chess.WHITE:
            self.start_white_timer()
        else:
            self.start_black_timer()

        result = self.engine.play(self.board, chess.engine.Limit(time=10))

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

        if self.white_time <= 0:
            result = "0-1" if self.player_color == chess.WHITE else "1-0"
            message = "White's time is up! Black wins."
        elif self.black_time <= 0:
            result = "1-0" if self.player_color == chess.BLACK else "0-1"
            message = "Black's time is up! White wins."
        else:
            result = self.get_game_result()

        self.show_result_menu(result, message)


    def pause_timers(self):
        self.timer_running = False
        self.pause_white_timer()
        self.pause_black_timer()

    def get_game_result(self):
        if self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                return "0-1"  
            else:
                return "1-0" 
        elif self.board.is_stalemate():
            return "1/2-1/2"  
        elif self.board.is_insufficient_material():
            return "1/2-1/2"  # Remi zbog nedovoljnog materijala
        elif self.board.is_seventyfive_moves():
            return "1/2-1/2"  # Remi zbog pravila 75 poteza
        elif self.board.is_fivefold_repetition():
            return "1/2-1/2"  # Remi zbog ponavljanja poteza
        return "Unknown"

    def show_result_menu(self, result, message):
        result_window = tk.Toplevel(self.root)
        result_window.title("Game Over")

        result_label = tk.Label(result_window, text=f"User vs Stockfish: {result}", font=("Inter", 24))
        result_label.pack(pady=20)

        message_label = tk.Label(result_window, text=message, font=("Inter", 16))
        message_label.pack(pady=10)

        save_button = tk.Button(result_window, text="Save", font=("Inter", 14), command=self.save_game)
        save_button.pack(side="left", padx=20, pady=20)

        cancel_button = tk.Button(result_window, text="Cancel", font=("Inter", 14), command=result_window.destroy)
        cancel_button.pack(side="right", padx=20, pady=20)

    def save_game(self):
        print("Igra spremljena")
        # Implementiraj logiku za spremanje rezultata


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

    chess_gui = ChessGUI(board_frame, board, flipped=flipped, player_color=chess.WHITE if color.lower() == "white" else chess.BLACK, white_time=white_time, black_time=black_time, white_increment=white_increment, black_increment=black_increment)

    resign_button = tk.Button(info_frame, text="Resign and Leave", font=("Inter", 16), bg="#F2CA5C", fg="#660000", width=20, height=2, borderwidth=2, relief="solid")
    resign_button.grid(row=3, column=0, pady=50, sticky="s")

    gameScreenWindow.mainloop()
