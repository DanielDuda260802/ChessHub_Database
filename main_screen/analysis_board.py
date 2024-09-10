import sys
import tkinter as tk
from PIL import Image, ImageTk
import chess # type: ignore
import chess.pgn # type: ignore
import cairosvg # type: ignore
import os

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helper import config

class ChessGUI:
    def __init__(self, root, analysisWindow, board, notation_text, nav_frame):
        self.board = board
        self.root = root
        self.analysisWindow = analysisWindow
        self.notation_text = notation_text
        self.nav_frame = nav_frame

        # PGN
        self.game = chess.pgn.Game()
        self.current_node = self.game

        self.current_move_index = 0
        self.fen_dict = {}

        self.canvas = tk.Canvas(root, bg="#000000")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.selected_square = None
        self.highlighted_squares = []
        self.flipped = False

        self.root.after(100, self.draw_board)
        self.canvas.bind("<Button-1>", self.on_click)

        # Gumb za promociju varijante (početno je skriven)
        self.promote_button = tk.Button(nav_frame, text="Promote to Main", command=self.promote_to_main_variation, font=("Inter", 20), bg="#F2CA5C", fg="#000000")
        self.promote_button.pack_forget()

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
                matching_variation = None
                for variation in self.current_node.variations:
                    if variation.move == promotion_move:
                        matching_variation = variation
                        break

                if matching_variation:    
                    # ako već postoji, koristi postojeći čvor
                    self.current_node = matching_variation
                else:
                    # Dodaj novu varijantu ako potez nije odigran
                    self.current_node = self.current_node.add_variation(promotion_move)
                
                self.update_notation(current_move=promotion_move)
                self.board.push(promotion_move)
                
                if self.current_node.is_main_variation():
                    self.promote_button.pack_forget()
                else:
                    self.promote_button.pack(side="top", pady=10)
                
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

                if self.board.piece_at(self.selected_square).piece_type == chess.PAWN and (
                        (self.board.color_at(self.selected_square) == chess.WHITE and chess.square_rank(square) == 7) or 
                        (self.board.color_at(self.selected_square) == chess.BLACK and chess.square_rank(square) == 0)
                ):
                    self.promote_pawn(move)
                elif move in self.board.legal_moves:
                    # Provjera postoji li taj kao sljedeći potez u nekoj od varijanti
                    matching_variation = None
                    for variation in self.current_node.variations:
                        if variation.move == move:
                            matching_variation = variation
                            break
                    
                    if matching_variation:
                        # ako postoji, postavi current_node na varijantu s tim potezom
                        self.current_node = matching_variation
                    elif move in self.board.legal_moves:
                        # ako potez već nije odigran, dodaj ga kao novu varijantu
                        self.current_node = self.current_node.add_variation(move)
                    else:
                        self.selected_square = None
                        self.highlighted_squares = []
                        return

                    self.update_notation(current_move=move)
                    self.board.push(move)

                    if self.current_node.is_main_variation():
                        self.promote_button.pack_forget()
                    else:
                        self.promote_button.pack(side="top", pady=10)
                    
                    self.selected_square = None
                    self.highlighted_squares = []
                    

                    self.draw_board()
                    
            self.draw_board()

    def update_board(self):
        new_board = chess.Board()
        node = self.game

        # krećemo od korjena (početne pozicije) i prolazimo kroz sve varijante dok ne dođemo do current_node
        while node != self.current_node:
            for variation in node.variations:
                if variation == self.current_node or variation.move in self.board.move_stack:
                    node = variation
                    new_board.push(node.move)
        self.board = new_board
        self.draw_board()
        
    def prev_move(self):
        if self.current_node.parent:            
            self.current_node = self.current_node.parent
            if len(self.board.move_stack) > 0:
                self.board.pop()

            if self.current_node.is_main_variation():
                self.promote_button.pack_forget()
            else:
                self.promote_button.pack(side="top", pady=10)                
        
            if len(self.board.move_stack) > 0:
                self.board.pop()

            self.update_notation(current_move=self.current_node.move)

            if self.current_node.move:
                self.board.push(self.current_node.move)
            self.current_move_index -= 1

            self.update_board()
        else:
            print("No previous move available!")

    def next_move(self):
        if self.current_node.variations:
            if len(self.current_node.variations) == 1:
                move = self.current_node.variations[0].move
                self.update_notation(current_move=move)
                self.board.push(move)  
                self.current_node = self.current_node.variations[0]
                self.current_move_index += 1

                self.update_board()

            else:
                self.show_variation_menu() 
        else:
            print("No next move available!")

    def show_variation_menu(self):
        variation_window = tk.Toplevel(self.analysisWindow)
        variation_window.title("Choose a Variation")
        variation_window.geometry("300x200")

        variation_window.grab_set()

        listbox = tk.Listbox(variation_window, font=("Inter", 18))
        listbox.pack(fill=tk.BOTH, padx=10, pady=15, expand=True)

        def select_variation(event=None):
            selected_index = listbox.curselection()
            if selected_index:
                variation = self.current_node.variations[selected_index[0]]
                move = variation.move
                self.update_notation(current_move=move)
                self.current_node = variation
                self.board.push(move)
                self.current_move_index += 1
                self.update_board()

                if selected_index[0] == 0: 
                    self.promote_button.pack_forget()
                else:
                    self.promote_button.pack(side="top", pady=10)

                variation_window.destroy()

        for i, variation in enumerate(self.current_node.variations):
            move_san = self.board.san(variation.move)
            listbox.insert(tk.END, f"Variation {i + 1}: {move_san}")

        listbox.selection_set(0)

        listbox.bind("<Return>", select_variation)
        listbox.bind("<Right>", select_variation)
        listbox.bind("<Double-Button-1>", select_variation)
        listbox.focus_set()

    def promote_to_main_variation(self):
        if not self.current_node.is_main_variation():
            parent_node = self.current_node.parent
            parent_node.promote(self.current_node)  

            self.update_notation(current_move=self.current_node.move)

            self.highlight_promoted_move_with_fen(self.current_node.move)
        
    def highlight_promoted_move_with_fen(self, move):
        """Boldanje poteza pomoću kombinacije FEN-a prethodne pozicije i SAN poteza"""
        self.notation_text.tag_remove("highlight", "1.0", tk.END) 

        previous_fen = self.current_node.parent.board().fen() if self.current_node.parent else None

        if previous_fen and previous_fen in self.fen_dict:
            temp_board = self.current_node.parent.board()

            promoted_move_san = temp_board.san(move)

            san_list = self.fen_dict[previous_fen]
            for san_move, move_idx, var_idx in san_list:
                if san_move == promoted_move_san:
                    end_idx = f"{move_idx} + {len(san_move)} chars"
                    self.notation_text.tag_add("highlight", move_idx, end_idx)
                    self.notation_text.tag_config("highlight", background="yellow", foreground="black", font=("Inter", 16, "bold"))
                    return

    def update_notation(self, current_move=None):
        """Ažuriramo PGN notaciju i ističemo trenutni potez."""
        self.notation_text.config(state="normal")
        self.notation_text.delete(1.0, tk.END)

        exporter = chess.pgn.StringExporter(headers=False, variations=True, comments=True)
        pgn = self.game.accept(exporter)

        self.notation_text.insert(tk.END, pgn)

        self.fen_dict = {}

        stack = [(self.game, chess.Board(), "1.0", 0)] 

        while stack:
            node, board, current_position, variation_index = stack.pop()

            for i, variation in enumerate(node.variations):
                move = variation.move

                pre_move_fen = board.fen()

                if move not in board.legal_moves:
                    print(f"Illegal move: {move} in {board.fen()}")
                    continue

                san_move = board.san(move)
                board.push(move)

                move_idx = self.notation_text.search(san_move, current_position, tk.END)

                if not move_idx:
                    print(f"Potez {san_move} nije pronađen u tekstu.")
                    continue

                if pre_move_fen not in self.fen_dict:
                    self.fen_dict[pre_move_fen] = [(san_move, move_idx, i)]
                else:
                    self.fen_dict[pre_move_fen].append((san_move, move_idx, i))

                current_position = self.notation_text.index(f"{move_idx} + {len(san_move)}c")
                stack.append((variation, board.copy(), current_position, i)) 
                board.pop()

        if current_move:
            try:
                current_fen = self.board.fen()

                if current_fen in self.fen_dict:
                    san_list = self.fen_dict[current_fen]
                    if len(san_list) == 1:
                        san_move, move_idx, var_idx = san_list[0]
                        end_idx = f"{move_idx} + {len(san_move)} chars"
                        self.notation_text.tag_add("highlight", move_idx, end_idx)
                    else:
                        # Ako postoji više poteza s istim FEN-om, usporedimo SAN i varijaciju
                        for san_move, move_idx, var_idx in san_list:
                            if san_move == self.board.san(current_move):
                                end_idx = f"{move_idx} + {len(san_move)} chars"
                                self.notation_text.tag_add("highlight", move_idx, end_idx)
                                break
                else:
                    print("FEN nije pronađen u rječniku!")
                    print(self.fen_dict)
                    print(f"TRAZENI FEN: {current_fen}")
            except AssertionError:
                print(f"Potez {current_move} nije legalan u trenutnoj poziciji.")
                print(self.board)

        self.notation_text.tag_config("highlight", background="yellow", foreground="black", font=("Inter", 16, "bold"))
        self.notation_text.config(state="disabled")

def select_button(selected_button, buttons, content_frames, chess_gui=None):
    for button in buttons:
        button.config(font=("Inter", 24, "normal"))
    selected_button.config(font=("Inter", 24, "bold"))

    for frame in content_frames:
        frame.pack_forget()

    content_frames[buttons.index(selected_button)].pack(fill="both", expand=True)

    if selected_button["text"] == "Notation" and chess_gui:
        chess_gui.notation_text.pack(fill="both", expand=True)
        chess_gui.nav_frame.pack(side="bottom", padx=20)
    else:
        chess_gui.notation_text.pack_forget()
        chess_gui.promote_button.forget()
        chess_gui.nav_frame.pack_forget()

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

    notation_text_height = screen_height // 50
    notation_text = tk.Text(notation_frame, font=("Inter", 16), bg="#F8E7BB", fg="#000000", wrap="word", state="disabled", relief="flat", height=notation_text_height)
    notation_text.pack(side="top", fill="x", padx=10, pady=10)

    notation_control_frame = tk.Frame(notation_frame, bg="#F8E7BB")
    notation_control_frame.pack(side="bottom", pady=10)

    nav_frame = tk.Frame(notation_control_frame, bg="#F8E7BB")

    board = chess.Board()
    chess_gui = ChessGUI(board_frame, analysisWindow, board, notation_text, nav_frame)

    promote_button = tk.Button(notation_control_frame, text="Promote to Main", command=chess_gui.promote_to_main_variation, font=("Inter", 20), bg="#F2CA5C", fg="#000000")
    chess_gui.promote_button = promote_button
    promote_button.pack_forget()

    prev_button = tk.Button(nav_frame, text="⟨", command=chess_gui.prev_move, font=("Inter", 24, "bold"), bg="#F2CA5C", fg="#660000", bd=0, width=20, height=2)
    prev_button.config(highlightbackground="#480202", highlightthickness=4)
    prev_button.pack(side="left", padx=10)

    next_button = tk.Button(nav_frame, text="⟩", command=chess_gui.next_move, font=("Inter", 24, "bold"), bg="#F2CA5C", fg="#660000", bd=0, width=20, height=2)
    next_button.config(highlightbackground="#480202", highlightthickness=4)
    next_button.pack(side="left")

    nav_frame.pack(side="top", pady=10)

    analysisWindow.bind("<Left>", lambda event: chess_gui.prev_move())
    analysisWindow.bind("<Right>", lambda event: chess_gui.next_move())

    notation_button.config(command=lambda: select_button(notation_button, buttons, content_frames, chess_gui))
    reference_button.config(command=lambda: select_button(reference_button, buttons, content_frames, chess_gui))
    kibitzer_button.config(command=lambda: select_button(kibitzer_button, buttons, content_frames, chess_gui))

    select_button(notation_button, buttons, content_frames, chess_gui)
