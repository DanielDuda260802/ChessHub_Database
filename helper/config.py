import os

base_dir = os.path.dirname(os.path.dirname(__file__))
assets_dir = os.path.join(base_dir, "assets")

analysis_board_image_path = os.path.join(assets_dir, "AnalysisBoard.png")
find_player_image_path = os.path.join(assets_dir, "FindPlayer.png")
chessHubDatabase_image_path = os.path.join(assets_dir, "Database.png")
myGames_image_path = os.path.join(assets_dir, "MyGames.png")
unchecked_image_path = os.path.join(assets_dir, "unchecked_image.png")
checked_image_path = os.path.join(assets_dir, "checked_image.png")

# Screen dimensions
def get_screen_dimensions(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    return screen_width, screen_height

# Colors
appbar_color = "#660000"
background_color = "#F8E7BB"
button_color = "#F2CA5C"
button_text_color = "#660000"

# Fonts
app_title_font = ("Inter", 24, "bold")
button_font = ("Inter", 24)
label_font = ("Inter", 16)

# pgn_file_path
pgn_file_path = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/pgn/twic1536.pgn"

# my_games_pgn_file_path
my_games_pgn_file_path = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/pgn/MyGames.pgn"
my_analyzes_pgn_file_path = "/home/daniel/Desktop/3.godinapreddiplomskogstudija/6.semestar/Zavrsni_Rad/ChessHub_Database/data/pgn/MyAnalyzes.pgn"
# Assuming Stockfish binary is available locally
STOCKFISH_PATH = "/home/daniel/Desktop/stockfish/stockfish-ubuntu-x86-64-avx2"