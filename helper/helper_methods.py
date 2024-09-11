import hashlib
from PIL import Image, ImageTk
import chess.svg # type: ignore
import cairosvg # type: ignore

def load_and_resize_image(path, size):
    """Loads an image from a given path and resizes it to the given size."""
    image = Image.open(path)
    image = image.resize(size, Image.LANCZOS)
    return image  # PIL.Image objekt

def load_and_resize_image_PhotoImage(path, size):
    """Loads an image from a given path and resizes it to the given size."""
    image = Image.open(path)
    image = image.resize(size, Image.LANCZOS)
    photo_image = ImageTk.PhotoImage(image)  
    return photo_image  # PhotoImage objekt


def board_to_image(board, size):  
    svg_data = chess.svg.board(board=board, size=size)
    output_path = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/assets/chessboard.png"
    cairosvg.svg2png(bytestring=svg_data, write_to=output_path)
    return output_path

def hash_fen(fen):
    """Generira hash FEN-a koristeći SHA-256 za bržu pretragu."""
    return hashlib.sha256(fen.encode('utf-8')).hexdigest()