"""Hằng số trò chơi Flappy Bird (Arcade 3.3.3)."""
import sys
from pathlib import Path

import pyglet
# Tắt DirectWrite/font antialiasing toàn cục để render pixel art font 100% sắc nét (1-bit binary alpha)
pyglet.options.text_antialiasing = False

# Thư mục gốc, tài nguyên assets & dữ liệu lưu trữ
if getattr(sys, "frozen", False):
    # Đang chạy từ file thực thi PyInstaller (bundle tạm thời chứa assets)
    PROJECT_ROOT = Path(sys._MEIPASS)
    # File save_data.json lưu cạnh file .exe để lưu trữ vĩnh viễn tiến trình chơi
    USER_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    USER_ROOT = PROJECT_ROOT

ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = USER_ROOT / "data"
SAVE_FILE = DATA_DIR / "save_data.json"

# Kích thước màn hình ảo (Virtual Viewport)
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FLOOR_HEIGHT = 108.0          # Mặt sàn từ Y = 0 đến Y = 108
PLAYABLE_TOP = SCREEN_HEIGHT  # Y = 512
PLAYABLE_BOTTOM = FLOOR_HEIGHT # Y = 108
PLAYABLE_HEIGHT = PLAYABLE_TOP - PLAYABLE_BOTTOM # 404 px

# Chu kỳ vật lý cố định (Fixed timestep)
FIXED_DT = 1.0 / 60.0

# Thông số vật lý của Chim (Arcade: Y hướng lên)
# Gốc Pygame: Flap -9 px/frame (30fps) -> Arcade: ~+270 px/s
FLAP_VELOCITY = 280.0
# Gốc Pygame: Acc +1 px/frame^2 (30fps) -> Arcade: ~-900 px/s^2
GRAVITY = -850.0
# Gốc Pygame: Max drop 10 px/frame (30fps) -> Arcade: ~-450 px/s
TERMINAL_VELOCITY = -450.0

# Góc xoay chim (Độ)
ROT_FLAP = 25.0               # Ngửa lên khi vỗ cánh
ROT_VEL = -180.0              # Tốc độ chúc đầu xuống khi rơi (độ/s)
ROT_MIN = -90.0               # Góc chúc tối đa khi rơi
ROT_MAX = 25.0                # Góc ngửa tối đa

# Kích thước Hitbox chuẩn cố định của chim (Bất biến)
STANDARD_HITBOX_WIDTH = 34.0
STANDARD_HITBOX_HEIGHT = 24.0

# Vị trí ban đầu của chim
BIRD_START_X = int(SCREEN_WIDTH * 0.28)
BIRD_START_Y = int(FLOOR_HEIGHT + PLAYABLE_HEIGHT * 0.5)

# Ống nước (Pipes)
PIPE_WIDTH = 52.0
PIPE_HEIGHT = 320.0
PIPE_HORIZONTAL_SPACING = 175.0  # Khoảng cách tối thiểu giữa 2 cột ống

# Thông số độ khó (Difficulty Curve milestones)
INITIAL_PIPE_SPEED = 180.0
MAX_PIPE_SPEED = 300.0
INITIAL_PIPE_GAP = 150.0
MIN_PIPE_GAP = 110.0
LERP_SPEED_FACTOR = 4.0          # Tốc độ hội tụ của Lerp qua từng delta_time

# Kinh tế & Thành tựu
SCORE_PER_COIN = 5               # Cứ 5 điểm nhận 1 coin

# Font Retro 8-bit Pixel Art & Safe Fallback
FONT_DIR = ASSETS_DIR / "fonts"
FONT_RETRO_PATH = FONT_DIR / "PressStart2P-Regular.ttf"
FONT_RETRO_NAME = "Press Start 2P"
FONT_RETRO_FAMILY = ("Press Start 2P", "Arial")


def ensure_retro_font_loaded() -> bool:
    """Nạp font Press Start 2P toàn cục vào Arcade/Pyglet an toàn."""
    if FONT_RETRO_PATH.exists():
        try:
            import arcade
            arcade.load_font(FONT_RETRO_PATH)
            return True
        except Exception:
            return False
    return False

