import tkinter as tk
from PIL import Image, ImageTk
import chess
import os, sys

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import config
from helper.helper_methods import board_to_image

def start_game_screen(color, white_time, white_increment, black_time, black_increment, level):
    gameScreenWindow = tk.Toplevel()
    gameScreenWindow.title(f"Play Vs Computer - level: {level}")
    screen_width, screen_height = config.get_screen_dimensions(gameScreenWindow)
    gameScreenWindow.geometry(f"{screen_width}x{screen_height}")
    gameScreenWindow.configure(bg="#F8E7BB")
    
    # Create the main frames
    board_frame = tk.Frame(gameScreenWindow, width=int(screen_width * 0.60), height=screen_height, bg="#660000")
    board_frame.pack(side="left", padx=0, pady=0, fill="both", expand=True)

    info_frame = tk.Frame(gameScreenWindow, bg="#F8E7BB", width=int(screen_width * 0.35), relief="flat", bd=10)
    info_frame.pack(side="right", fill="y", expand=True, padx=0, pady=0)

    # Initialize Chessboard
    board = chess.Board()

    board_image_path = board_to_image(board, size=900)
    board_image = ImageTk.PhotoImage(Image.open(board_image_path))
    
    board_label = tk.Label(board_frame, image=board_image)
    board_label.image = board_image
    board_label.pack(expand=True)

    # White Time Display with color box
    white_time_container = tk.Frame(info_frame, bg="#F8E7BB")
    white_time_container.grid(row=0, column=0, pady=40, padx=40, sticky="ew")

    white_color_box = tk.Label(white_time_container, bg="white", width=4, height=2, borderwidth=2, relief="solid")
    white_color_box.grid(row=0, column=0, padx=(0, 20))

    white_time_label = tk.Label(white_time_container, text=f"{white_time}:00", font=("Inter", 72), bg="#F8E7BB", fg="#000000", borderwidth=2, relief="solid", padx=20, pady=10)
    white_time_label.grid(row=0, column=1)

    # Black Time Display with color box
    black_time_container = tk.Frame(info_frame, bg="#F8E7BB")
    black_time_container.grid(row=1, column=0, pady=20, padx=40, sticky="ew")

    black_color_box = tk.Label(black_time_container, bg="black", width=4, height=2, borderwidth=2, relief="solid")
    black_color_box.grid(row=0, column=0, padx=(0, 20))

    black_time_label = tk.Label(black_time_container, text=f"{black_time}:00", font=("Inter", 72), bg="#F8E7BB", fg="#000000", borderwidth=2, relief="solid", padx=20, pady=10)
    black_time_label.grid(row=0, column=1)

    # For Resign Button at the bottom
    resign_button = tk.Button(info_frame, text="Resign and Leave", font=("Inter", 20), bg="#F2CA5C", fg="#660000", width=20, height=2, borderwidth=2, relief="solid")
    resign_button.grid(row=3, column=0, pady=200, sticky="s")

    gameScreenWindow.mainloop()
