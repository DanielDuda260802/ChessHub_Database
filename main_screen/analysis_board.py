import sys
import tkinter as tk
from PIL import Image, ImageTk
import chess # type: ignore
import cairosvg # type: ignore
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
        self.flipped = False

        # Notation button
        self.current_move_index = 0
        self.moves = list(board.move_stack)
        self.notation_moves = []

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
                san_notation = self.board.san(move)
                self.board.push(promotion_move)
                self.notation_moves.append(san_notation)
                self.selected_square = None
                self.highlighted_squares = []
                self.update_notation()
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
                    san_notation = self.board.san(move)
                    self.board.push(move)
                    self.notation_moves.append(san_notation)

                    self.selected_square = None
                    self.highlighted_squares = []

                    self.moves = list(self.board.move_stack)
                    self.current_move_index = len(self.moves)

                    self.update_notation()
                    self.draw_board()
                else:
                    print("Invalid move!")
                    self.selected_square = None
                    self.highlighted_squares = []
            self.draw_board()

    def update_board(self):
        new_board = chess.Board()
        for move in self.moves[:self.current_move_index]:
            new_board.push(move)
        self.board = new_board
        self.draw_board()
        self.update_notation()

    def prev_move(self):
        if self.current_move_index > 0:
            self.current_move_index -= 1
            self.update_board()

    def next_move(self):
        if self.current_move_index < len(self.moves):
            self.current_move_index += 1
            self.update_board()

    def update_notation(self):
        """Updates the notation text box with the current moves."""
        notation_text.config(state="normal")
        notation_text.delete(1.0, tk.END)
        
        notation_str = " ".join(f"{i//2 + 1}. {self.notation_moves[i]} {self.notation_moves[i + 1] if i + 1 < len(self.notation_moves) else ''}" for i in range(0, len(self.notation_moves), 2))

        notation_list = notation_str.split()
        move_index = 0 
        
        def on_click(event):
            """Handles clicking on a move in the notation to jump to that move."""
            index = notation_text.index(f"@{event.x},{event.y}")
            clicked_tag = notation_text.tag_names(index)

            if clicked_tag and clicked_tag[0].startswith("move_"):
                clicked_move_index = int(clicked_tag[0].split("_")[1]) + 1
                self.current_move_index = clicked_move_index
                self.update_board()

        notation_text.bind("<Button-1>", on_click)

        for i, move in enumerate(notation_list):
            current_position = notation_text.index("end-1c")

            if move.endswith('.'):
                notation_text.insert(current_position, f"{move} ")
            else:
                start_idx = notation_text.index("end-1c")
                notation_text.insert(start_idx, f"{move} ")
                end_idx = notation_text.index("end-1c")

                tag_name = f"move_{move_index}"
                notation_text.tag_add(tag_name, start_idx, end_idx)

                if move_index == self.current_move_index - 1:
                    notation_text.tag_add("highlight", start_idx, end_idx)

                move_index += 1

        notation_text.tag_config("highlight", font=("Inter", 16, "bold"))
        notation_text.config(state="disabled")


def select_button(selected_button, buttons, content_frames, chess_gui=None):
    for button in buttons:
        button.config(font=("Inter", 24, "normal"))
    selected_button.config(font=("Inter", 24, "bold"))

    # Sakrij sve frameove
    for frame in content_frames:
        frame.pack_forget()

    # Prikaži odgovarajući frame
    content_frames[buttons.index(selected_button)].pack(fill="both", expand=True)

    # Ako je odabrana kartica "Notation", prikaži gumbe za poteze
    if selected_button["text"] == "Notation" and chess_gui:
        notation_text.pack(fill="both", expand=True)
        nav_frame.pack(side="bottom", padx=20)
    else:
        notation_text.pack_forget()
        nav_frame.pack_forget()

def open_analysis_board_window():
    analysisWindow = tk.Toplevel()
    analysisWindow.title("Analysis Board")
    screen_width, screen_height = config.get_screen_dimensions(analysisWindow)
    analysisWindow.geometry(f"{screen_width}x{screen_height}")
    analysisWindow.configure(bg="#480202")

    board_size = min(screen_width * 0.7, screen_height * 0.9)

    board_frame = tk.Frame(analysisWindow, width=int(board_size), height=int(board_size), bg="#660000")
    board_frame.pack(side="left", padx=10, pady=10, anchor="n")
    board_frame.pack_propagate(0)

    info_frame = tk.Frame(analysisWindow, bg="#F8E7BB", width=int(screen_width * 0.20), relief="flat", bd=10)
    info_frame.pack(side="right", fill="both", expand=True)

    buttons_frame = tk.Frame(info_frame, bg="#F8E7BB")
    buttons_frame.pack(side="top", fill="x")

    button_style = {
        "font": ("Inter", 24),
        "bg": "#F2CA5C",  
        "fg": "#000000",  
        "width": 15,
        "height": 2,
        "highlightbackground": "#660000", 
        "highlightthickness": 4
    }

    notation_button = tk.Button(buttons_frame, text="Notation", **button_style, command=lambda: select_button(notation_button, buttons))
    notation_button.pack(side="left", fill="x", padx=2)

    reference_button = tk.Button(buttons_frame, text="Reference", **button_style, command=lambda: select_button(reference_button, buttons))
    reference_button.pack(side="left", fill="x", padx=2)

    kibitzer_button = tk.Button(buttons_frame, text="Add Kibitzer", **button_style, command=lambda: select_button(kibitzer_button, buttons))
    kibitzer_button.pack(side="left", fill="x", padx=2)

    buttons = [notation_button, reference_button, kibitzer_button]

    notation_frame = tk.Frame(info_frame, bg="#F8E7BB")
    reference_frame = tk.Frame(info_frame, bg="#F8E7BB")
    kibitzer_frame = tk.Frame(info_frame, bg="#F8E7BB")

    content_frames = [notation_frame, reference_frame, kibitzer_frame]

    # Notation text area
    global notation_text
    notation_text = tk.Text(info_frame, font=("Inter", 16), bg="#F8E7BB", fg="#000000", wrap="word", state="disabled", relief="flat")
    notation_text.pack(fill="both", expand=True)

    board = chess.Board()
    chess_gui = ChessGUI(board_frame, analysisWindow, board)
    
    global nav_frame
    nav_frame = tk.Frame(info_frame, bg="#F8E7BB")

    prev_button = tk.Button(nav_frame, text="⟨", command=chess_gui.prev_move, font=("Inter", 24, "bold"), bg="#F2CA5C", fg="#660000", bd=0, width=20, height=2)
    prev_button.config(highlightbackground="#480202", highlightthickness=4)
    prev_button.pack(side="left", padx=10)

    next_button = tk.Button(nav_frame, text="⟩", command=chess_gui.next_move, font=("Inter", 24, "bold"), bg="#F2CA5C", fg="#660000", bd=0, width=20, height=2)
    next_button.config(highlightbackground="#480202", highlightthickness=4)
    next_button.pack(side="left")

    analysisWindow.bind("<Left>", lambda event: chess_gui.prev_move())
    analysisWindow.bind("<Right>", lambda event: chess_gui.next_move())

    nav_frame.pack_forget()

    # Select button logic
    notation_button.config(command=lambda: select_button(notation_button, buttons, content_frames, chess_gui))
    reference_button.config(command=lambda: select_button(reference_button, buttons, content_frames))
    kibitzer_button.config(command=lambda: select_button(kibitzer_button, buttons, content_frames))

    select_button(notation_button, buttons, content_frames, chess_gui)
    chess_gui.update_notation()