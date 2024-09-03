import tkinter as tk
from PIL import Image, ImageTk
import chess
import cairosvg
import os, sys

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import config
from helper.helper_methods import board_to_image

class ChessGUI:
    def __init__(self, root, board, flipped):
        self.board = board
        self.root = root
        self.flipped = flipped

        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.selected_square = None
        self.highlighted_squares = []
        
        # Draw the board after the window has loaded
        self.root.after(100, self.draw_board)  # Ensures the board is drawn after the window is fully loaded

        self.canvas.bind("<Button-1>", self.on_click)

    def board_to_image(self, size):
        # Create arrows (dots) for possible moves
        arrows = [chess.svg.Arrow(square, square, color="#033313") for square in self.highlighted_squares]


        svg_data = chess.svg.board(board=self.board, size=size, flipped=self.flipped, arrows=arrows)
        output_path = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/assets/chessboard.png"
        cairosvg.svg2png(bytestring=svg_data, write_to=output_path)
        return output_path

    def draw_board(self):
        self.root.update_idletasks()  # Osiguraj da se prozor u potpunosti prikazuje

        # Pronađi manju dimenziju da zadržiš kvadratni oblik
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.size = min(canvas_width, canvas_height)
        self.square_size = self.size // 8

        board_image_path = self.board_to_image(self.size) 
        board_image = Image.open(board_image_path)
        board_image = board_image.resize((self.size, self.size), Image.LANCZOS) 

        self.board_image = ImageTk.PhotoImage(board_image)
        self.canvas.delete("all")  # Očisti prethodne slike sa platna
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.board_image)

    def on_click(self, event):
        col = event.x // self.square_size
        row = event.y // self.square_size

        if self.flipped:
            col = 7 - col
            row = 7 - row

        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)
            print(f"Clicked on square: {chess.square_name(square)}")

            if self.selected_square is None:
                if self.board.piece_at(square):
                    # Select the square and show possible moves
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
                # Try to make the move
                move = chess.Move(self.selected_square, square)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.selected_square = None
                    self.highlighted_squares = []
                else:
                    self.selected_square = None
                    self.highlighted_squares = []

            # Redraw the board with updated highlights
            self.draw_board()


def start_game_screen(color, white_time, white_increment, black_time, black_increment, level):
    gameScreenWindow = tk.Toplevel()
    gameScreenWindow.title(f"Play Vs Computer - level: {level}")
    screen_width, screen_height = config.get_screen_dimensions(gameScreenWindow)
    gameScreenWindow.geometry(f"{screen_width}x{screen_height}")
    gameScreenWindow.configure(bg="#F8E7BB")

    board_frame = tk.Frame(gameScreenWindow, width=int(screen_width * 0.80), height=screen_height, bg="#660000")
    board_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

    info_frame = tk.Frame(gameScreenWindow, bg="#F8E7BB", width=int(screen_width * 0.20), relief="flat", bd=10)
    info_frame.pack(side="right", fill="y", expand=True, padx=10, pady=10)

    board = chess.Board()

    flipped = True if color.lower() == "black" else False

    chess_gui = ChessGUI(board_frame, board, flipped=flipped)

    white_time_container = tk.Frame(info_frame, bg="#F8E7BB")
    white_time_container.grid(row=0, column=0, pady=20, padx=20, sticky="ew")

    white_color_box = tk.Label(white_time_container, bg="white", width=4, height=2, borderwidth=2, relief="solid")
    white_color_box.grid(row=0, column=0, padx=(0, 10))

    white_time_label = tk.Label(white_time_container, text=f"{white_time}:00", font=("Inter", 36), bg="#F8E7BB", fg="#000000", borderwidth=2, relief="solid", padx=10, pady=5)
    white_time_label.grid(row=0, column=1)

    black_time_container = tk.Frame(info_frame, bg="#F8E7BB")
    black_time_container.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

    black_color_box = tk.Label(black_time_container, bg="black", width=4, height=2, borderwidth=2, relief="solid")
    black_color_box.grid(row=0, column=0, padx=(0, 10))

    black_time_label = tk.Label(black_time_container, text=f"{black_time}:00", font=("Inter", 36), bg="#F8E7BB", fg="#000000", borderwidth=2, relief="solid", padx=10, pady=5)
    black_time_label.grid(row=0, column=1)

    resign_button = tk.Button(info_frame, text="Resign and Leave", font=("Inter", 16), bg="#F2CA5C", fg="#660000", width=20, height=2, borderwidth=2, relief="solid")
    resign_button.grid(row=3, column=0, pady=50, sticky="s")

    gameScreenWindow.mainloop()
