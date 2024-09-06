import sys
import os
from threading import Thread

# dodana putanja do ostalih datoteka
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helper import helper_methods
from helper import database_utils
from helper import config
import playVsComputerSetupScreen
from analysis_board import open_analysis_board_window

import tkinter as tk
from PIL import ImageTk

# Funkcija za kreiranje loading screen-a
def show_loading_screen(root):
    loading_screen = tk.Toplevel(root)
    loading_screen.geometry(f"{400}x{200}")
    loading_screen.title("Loading...")
    loading_screen.configure(bg="#F8E7BB")

    loading_screen.grab_set()  
    loading_screen.transient(root)  
    loading_screen.update() 
    
    loading_label = tk.Label(loading_screen, text="Loading ChessHub... Please wait.", font=("Helvetica", 16), fg="#660000", bg="#F8E7BB")
    loading_label.pack(expand=True)
    
    return loading_screen

# UI komponente
def create_appbar(root):
    appbar = tk.Frame(root, bg=config.appbar_color, height=50)
    appbar.pack(side="top", fill="x")
    app_title = tk.Label(appbar, text="ChessHub", bg=config.appbar_color, fg="#F2CA5C", font=config.app_title_font)
    app_title.pack(pady=10)
    return appbar

def create_content_frame(root):
    content_frame = tk.Frame(root, bg=config.background_color)
    content_frame.pack(pady=20, padx=20, anchor="w", side="top", fill="x")
    return content_frame

def create_horizontal_line(parent_frame, color="#660000"):
    line = tk.Frame(parent_frame, bg=color, height=2)
    line.pack(side="top", fill="x", pady=10)
    return line

def create_vertical_line(parent_frame, color="#660000"):
    line = tk.Frame(parent_frame, bg=color, width=2)
    line.pack(side="left", fill="y", padx=10)
    return line

def create_play_vs_computer_button(parent_frame):
    button_frame = tk.Frame(parent_frame, bg="#660000", padx=4, pady=4)
    button_frame.pack(side="left", padx=10)

    playVsComputer_btn = tk.Button(button_frame, text="Play vs Computer", bg=config.button_color, fg=config.button_text_color, font=config.button_font, height=2, width=20, bd=0, command=playVsComputerSetupScreen.open_play_vs_computer_window)
    playVsComputer_btn.pack()
    
    return playVsComputer_btn

def create_icon_with_label(parent_frame, image_path, image_size, text, command=None):
    image = helper_methods.load_and_resize_image(image_path, image_size)
    icon_photo = ImageTk.PhotoImage(image)
    frame = tk.Frame(parent_frame, bg=config.background_color)
    frame.pack(side="left", padx=30)
    icon_button = tk.Button(frame, image=icon_photo, bg=config.background_color, borderwidth=0, command=command)
    icon_button.image = icon_photo
    icon_button.pack(side="top")
    label = tk.Label(frame, text=text, bg=config.background_color, fg=config.button_text_color, font=config.label_font)
    label.pack(side="top")
    return frame

def create_icon_with_table_button_myGames(content_frame, table_frame, image_path, image_size, text):
    icon_image = helper_methods.load_and_resize_image(image_path, image_size)
    icon_photo = ImageTk.PhotoImage(icon_image)
    icon_button = tk.Button(content_frame, image=icon_photo, text=text, compound="top", command=lambda: database_utils.display_my_games(table_frame))
    icon_button.image = icon_photo
    icon_button.pack(side="left", padx=20)

def create_icon_with_table_button(content_frame, table_frame, image_path, image_size, text):
    icon_image = helper_methods.load_and_resize_image(image_path, image_size)
    icon_photo = ImageTk.PhotoImage(icon_image)
    icon_button = tk.Button(content_frame, image=icon_photo, text=text, compound="top", command=lambda: database_utils.display_data(table_frame))
    icon_button.image = icon_photo
    icon_button.pack(side="left", padx=20)

def initialize_data(root, loading_screen):
    database_utils.parse_pgn_and_store_in_db(config.pgn_file_path)
    database_utils.create_my_games_table() 
    if os.path.exists(config.my_games_pgn_file_path):
        database_utils.clear_my_games_table()
        database_utils.parse_my_games_pgn(config.my_games_pgn_file_path)

    loading_screen.destroy()

def start_initialization_in_background(root):
    loading_screen = show_loading_screen(root)
    
    # Inicijalizaciju podataka pokrećemo u pozadini koristeći Thread
    thread = Thread(target=initialize_data, args=(root, loading_screen))
    thread.start()

root = tk.Tk()
root.title("ChessHub")
screen_width, screen_height = config.get_screen_dimensions(root)
root.geometry(f"{screen_width}x{screen_height}")
root.configure(bg=config.background_color)

start_initialization_in_background(root)

create_appbar(root)
content_frame = create_content_frame(root)
table_frame = tk.Frame(root, bg=config.background_color)
table_frame.pack(side="bottom", fill="x", expand=False)

create_play_vs_computer_button(content_frame)
create_vertical_line(content_frame)
create_icon_with_label(content_frame, config.analysis_board_image_path, (76, 76), "Analysis board", command=open_analysis_board_window)
create_vertical_line(content_frame)
create_icon_with_label(content_frame, config.find_player_image_path, (94, 94), "Find Player")
create_horizontal_line(root)
create_vertical_line(content_frame)
create_icon_with_table_button(content_frame, table_frame, config.chessHubDatabase_image_path, (100, 100), "ChessHub Database")
create_vertical_line(content_frame)
create_icon_with_table_button_myGames(content_frame, table_frame, config.myGames_image_path, (100, 100), "MyGames")

root.mainloop()
