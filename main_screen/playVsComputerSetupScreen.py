import os, sys

# Dodana putanja do ostalih datoteka
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helper.helper_methods import load_and_resize_image_PhotoImage
import gameScreen
from helper import config
from PIL import Image, ImageTk
from tkinter import messagebox
import tkinter as tk

def open_play_vs_computer_window():

    def on_click(event):
        if event.widget == white_radio:
            color_var.set("white")
            update_buttons()
        elif event.widget == black_radio:
            color_var.set("black")
            update_buttons()

    def update_buttons():
        if color_var.get() == "white":
            white_radio.itemconfig(white_image_id, image=checked_image)
            black_radio.itemconfig(black_image_id, image=unchecked_image)
        else:
            white_radio.itemconfig(white_image_id, image=unchecked_image)
            black_radio.itemconfig(black_image_id, image=checked_image)

    def validate_time_format(value):
        return value.isdigit() or value == ""

    def select_level(level):
        selected_level.set(level)
        update_level_buttons()

    def update_level_buttons():
        for button in level_buttons:
            if button.cget("text") == selected_level.get():
                button.config(bg="#660000", fg="#F2CA5C")
            else:
                button.config(bg="#F2CA5C", fg="#660000")

    def on_play_button_click():
        selected_color = color_var.get()
        if selected_color not in ["white", "black"]:
            messagebox.showwarning("Selection Error", "Please select a color (White or Black).")
            return

        white_time = white_time_entry.get()
        white_increment = white_increment_entry.get() if white_increment_entry.get() else "0"

        black_time = black_time_entry.get()
        black_increment = black_increment_entry.get() if black_increment_entry.get() else "0"

        if not white_time or not black_time:
            messagebox.showwarning("Time Error", "Please enter time for both White and Black players.")
            return

        selected_level_value = selected_level.get()
        if not selected_level_value:
            messagebox.showwarning("Level Error", "Please select a level.")
            return

        # if all conditions are satisfied, close this window and open the game screen
        play_window.destroy()

        gameScreen.start_game_screen(
            selected_color,
            white_time,
            white_increment,
            black_time,
            black_increment,
            selected_level_value
        )

    play_window = tk.Toplevel()
    play_window.title("Play vs Computer")
    play_window.geometry("1350x940")
    play_window.configure(bg="#F8E7BB")

    main_frame = tk.Frame(play_window, bg="#F8E7BB")
    main_frame.pack(pady=40)

    # Color Label
    color_label = tk.Label(main_frame, text="Color:", bg="#F8E7BB", font=("Inter", 40))
    color_label.grid(row=0, column=0, padx=200, pady=20, sticky="n")

    # Time Label
    time_label = tk.Label(main_frame, text="Time:", bg="#F8E7BB", font=("Inter", 40))
    time_label.grid(row=0, column=1, padx=200, pady=20, sticky="n")

    # Color Frame
    color_frame = tk.Frame(main_frame, bg="#F8E7BB")
    color_frame.grid(row=1, column=0, padx=20, pady=10)

    color_var = tk.StringVar(value="white")

    unchecked_image = load_and_resize_image_PhotoImage(config.unchecked_image_path, (30, 30))
    checked_image = load_and_resize_image_PhotoImage(config.checked_image_path, (30, 30))

    # Spremite reference na slike
    play_window.unchecked_image = unchecked_image
    play_window.checked_image = checked_image

    white_radio = tk.Canvas(color_frame, width=200, height=50, bg="#F8E7BB", highlightthickness=0)
    white_image_id = white_radio.create_image(10, 25, anchor="w", image=checked_image)
    white_radio.create_text(50, 25, anchor="w", text="White", font=("Inter", 32), fill="#000000")
    white_radio.pack(pady=10)
    white_radio.bind("<Button-1>", on_click)

    black_radio = tk.Canvas(color_frame, width=200, height=50, bg="#F8E7BB", highlightthickness=0)
    black_image_id = black_radio.create_image(10, 25, anchor="w", image=unchecked_image)
    black_radio.create_text(50, 25, anchor="w", text="Black", font=("Inter", 32), fill="#000000")
    black_radio.pack(pady=10)
    black_radio.bind("<Button-1>", on_click)

    update_buttons()

    # Validation command for time entry fields
    vcmd = (play_window.register(validate_time_format), '%P')

    # Time Frame
    time_frame = tk.Frame(main_frame, bg="#F8E7BB")
    time_frame.grid(row=1, column=1, padx=20, pady=10)

    # White Time Entry
    white_time_frame = tk.Frame(time_frame, bg="#F8E7BB")
    white_time_frame.grid(row=0, column=0, pady=10)

    white_time_label = tk.Label(white_time_frame, text="White time:", bg="#F8E7BB", font=("Inter", 20))
    white_time_label.grid(row=0, column=0, padx=5)

    white_time_entry = tk.Entry(white_time_frame, width=7, font=("Inter", 24), borderwidth=3, relief="solid",
                                validate="key", validatecommand=vcmd,
                                highlightthickness=2, highlightbackground="#660000", highlightcolor="#660000")
    white_time_entry.grid(row=0, column=1, padx=5)

    white_increment_label = tk.Label(white_time_frame, text="Increment:", bg="#F8E7BB", font=("Inter", 20))
    white_increment_label.grid(row=0, column=2, padx=5)

    white_increment_entry = tk.Entry(white_time_frame, width=4, font=("Inter", 24), borderwidth=3, relief="solid",
                                     validate="key", validatecommand=vcmd,
                                     highlightthickness=2, highlightbackground="#660000", highlightcolor="#660000")
    white_increment_entry.grid(row=0, column=3, padx=5)

    # Black Time Entry
    black_time_frame = tk.Frame(time_frame, bg="#F8E7BB")
    black_time_frame.grid(row=1, column=0, pady=10)

    black_time_label = tk.Label(black_time_frame, text="Black time:", bg="#F8E7BB", font=("Inter", 20))
    black_time_label.grid(row=0, column=0, padx=8)

    black_time_entry = tk.Entry(black_time_frame, width=7, font=("Inter", 24), borderwidth=3, relief="solid",
                                validate="key", validatecommand=vcmd,
                                highlightthickness=2, highlightbackground="#660000", highlightcolor="#660000")
    black_time_entry.grid(row=0, column=1, padx=5)

    black_increment_label = tk.Label(black_time_frame, text="Increment:", bg="#F8E7BB", font=("Inter", 20))
    black_increment_label.grid(row=0, column=2, padx=5)

    black_increment_entry = tk.Entry(black_time_frame, width=4, font=("Inter", 24), borderwidth=3, relief="solid",
                                     validate="key", validatecommand=vcmd,
                                     highlightthickness=2, highlightbackground="#660000", highlightcolor="#660000")
    black_increment_entry.grid(row=0, column=3, padx=5)

    # Level Label
    level_label = tk.Label(play_window, text="Level:", bg="#F8E7BB", font=("Inter", 40))
    level_label.pack(pady=10)

    # Frame for Levels
    level_frame = tk.Frame(play_window, bg="#F8E7BB")
    level_frame.pack(pady=5)

    selected_level = tk.StringVar(value="")

    levels = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", 
              "Level 6", "Level 7", "Level 8", "Level 9", "Level 10"]

    # Create two rows for the levels
    row_1_frame = tk.Frame(level_frame, bg="#F8E7BB")
    row_1_frame.pack(pady=10)

    row_2_frame = tk.Frame(level_frame, bg="#F8E7BB")
    row_2_frame.pack(pady=10)

    level_buttons = []

    # First 5 levels in row 1
    for level in levels[:5]:
        button = tk.Button(row_1_frame, text=level, bg="#F2CA5C", fg="#660000", font=("Inter", 24), width=10, height=1, borderwidth=4, relief="solid",
                        command=lambda lvl=level: select_level(lvl),
                        highlightthickness=2, highlightbackground="#660000", highlightcolor="#660000")
        button.pack(side="left", padx=10, pady=10)
        level_buttons.append(button)

    # Remaining 5 levels in row 2
    for level in levels[5:]:
        button = tk.Button(row_2_frame, text=level, bg="#F2CA5C", fg="#660000", font=("Inter", 24), width=10, height=1, borderwidth=4, relief="solid",
                        command=lambda lvl=level: select_level(lvl),
                        highlightthickness=2, highlightbackground="#660000", highlightcolor="#660000")
        button.pack(side="left", padx=10, pady=10)
        level_buttons.append(button)

    # Play Button
    play_button = tk.Button(play_window, text="Play", bg="#F2CA5C", fg="#660000", font=("Inter", 32), width=10, height=2, borderwidth=4, relief="solid",
                            highlightthickness=2, highlightbackground="#660000", highlightcolor="#660000", command=on_play_button_click)
    play_button.pack(pady=40)



