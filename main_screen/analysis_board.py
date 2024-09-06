import sys
import tkinter as tk
from PIL import Image, ImageTk
import chess
import cairosvg
import os

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helper import config

class ChessGUI:
    def __init__(self, root, analysisWindow, board):
        self.board = board
        self.root = root
        self.analysisWindow = analysisWindow

        self.canvas = tk.Canvas(root, bg="#000000")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.selected_square = None
        self.highlighted_squares = []
        self.flipped = False  # Optional: Can add a button to flip the board for fun

        self.root.after(100, self.draw_board)
        self.canvas.bind("<Button-1>", self.on_click)

    def board_to_image(self, size):
        arrows = [chess.svg.Arrow(square, square, color="#033313") for square in self.highlighted_squares]
        svg_data = chess.svg.board(board=self.board, size=size, flipped=self.flipped, arrows=arrows)
        output_path = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/assets/analysis_board.png"
        cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=output_path)
        return output_path

    def draw_board(self):
        self.root.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.size = min(canvas_width, canvas_height)
        self.square_size = self.size // 8

        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas.pack_propagate(0)  

        board_image_path = self.board_to_image(self.size)
        board_image = Image.open(board_image_path)
        board_image = board_image.resize((self.size, self.size), Image.LANCZOS)

        self.board_image = ImageTk.PhotoImage(board_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.board_image)

    def promote_pawn(self, move):
        promotion_window = tk.Toplevel(self.root)
        promotion_window.title("Choose promotion piece")

        save_directory = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/assets/promoted_pieces"

        def create_image(piece_symbol):
            """Generira sliku šahovske figure koristeći chess.svg."""
            piece = chess.Piece.from_symbol(piece_symbol)
            svg_data = chess.svg.piece(piece)

            svg_file_path = os.path.join(save_directory, f"{piece_symbol}.svg")
            png_file_path = os.path.join(save_directory, f"{piece_symbol}.png")

            with open(svg_file_path, 'w') as svg_file:
                svg_file.write(svg_data)

            cairosvg.svg2png(url=svg_file_path, write_to=png_file_path)

            image = Image.open(png_file_path)
            return ImageTk.PhotoImage(image)

        promotion_map = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}

        def promote_to(piece_symbol):
            promotion_piece = promotion_map[piece_symbol]
            promotion_move = chess.Move(move.from_square, move.to_square, promotion=promotion_piece)
            if promotion_move in self.board.legal_moves:
                self.board.push(promotion_move)
                self.selected_square = None
                self.highlighted_squares = []
                self.draw_board()
            else:
                print("Invalid promotion move!")
            promotion_window.destroy()

        queen_image = create_image('Q')
        rook_image = create_image('R')
        bishop_image = create_image('B')
        knight_image = create_image('N')

        tk.Button(promotion_window, image=queen_image, command=lambda: promote_to('q')).grid(row=0, column=0)
        tk.Button(promotion_window, image=rook_image, command=lambda: promote_to('r')).grid(row=0, column=1)
        tk.Button(promotion_window, image=bishop_image, command=lambda: promote_to('b')).grid(row=0, column=2)
        tk.Button(promotion_window, image=knight_image, command=lambda: promote_to('n')).grid(row=0, column=3)

        promotion_window.transient(self.root)
        promotion_window.grab_set()
        self.root.wait_window(promotion_window)

    def on_click(self, event):
        col = event.x // self.square_size
        row = event.y // self.square_size

        if self.flipped:
            col = 7 - col
            row = 7 - row

        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)

            if self.selected_square is None:
                if self.board.piece_at(square):
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

                # Provjeri za promociju pješaka (ako pješak stiže do posljednjeg reda)
                if self.board.piece_at(self.selected_square).piece_type == chess.PAWN and (
                        (self.board.color_at(self.selected_square) == chess.WHITE and chess.square_rank(square) == 7) or 
                        (self.board.color_at(self.selected_square) == chess.BLACK and chess.square_rank(square) == 0)
                ):
                    self.promote_pawn(move)
                elif move in self.board.legal_moves:
                    self.board.push(move)
                    self.selected_square = None
                    self.highlighted_squares = []
                    self.draw_board()
                else:
                    print("Invalid move!")
                    self.selected_square = None
                    self.highlighted_squares = []
            self.draw_board()

def open_analysis_board_window():
    analysisWindow = tk.Toplevel()
    analysisWindow.title("Analysis Board")
    screen_width, screen_height = config.get_screen_dimensions(analysisWindow)
    analysisWindow.geometry(f"{screen_width}x{screen_height}")
    analysisWindow.configure(bg="#F8E7BB")

    # Definiraj veličinu šahovske ploče
    board_size = min(screen_width * 0.7, screen_height * 0.9)

    # Kreiraj board_frame koji ima točnu širinu i visinu ploče
    board_frame = tk.Frame(analysisWindow, width=int(board_size), height=int(board_size), bg="#660000")
    board_frame.pack(side="left", padx=10, pady=10, anchor="n")
    board_frame.pack_propagate(0)

    info_frame = tk.Frame(analysisWindow, bg="#FFFFFF", width=int(screen_width * 0.20), relief="flat", bd=10)
    info_frame.pack(side="right", fill="y", expand=True)

    board = chess.Board()

    chess_gui = ChessGUI(board_frame, analysisWindow, board)


