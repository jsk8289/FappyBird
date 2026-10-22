"""Công cụ nhập và chuẩn hóa assets retro từ repo tham khảo sang định dạng RGBA (Arcade 3.3.3)."""
import os
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

from ..constants import ASSETS_DIR

REF_SPRITES_DIR = Path(r"E:\stolen\FlapPyBird\assets\sprites")
UPLOADED_ROBIN_PATH = Path(
    r"C:\Users\Admin\.gemini\antigravity\brain\39ea0ca2-276d-4ce6-b430-ffc6abb069df\.user_uploaded\media_1791903218785_dd8671c3.png"
)


def convert_and_save(src_path: Path, dst_path: Path) -> None:
    """Đọc ảnh (kể cả bảng màu Palette 'P'), chuyển sang RGBA và lưu PNG."""
    with Image.open(src_path) as img:
        rgba = img.convert("RGBA")
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        rgba.save(dst_path, "PNG")


def erase_grey_bird_from_message(dst_path: Path) -> None:
    """Xóa bỏ hoàn toàn icon chim màu xám trong message.png (rows 168..202, cols 68..112)."""
    with Image.open(dst_path) as img:
        rgba = img.convert("RGBA")
        draw = ImageDraw.Draw(rgba)
        draw.rectangle([68, 168, 112, 202], fill=(0, 0, 0, 0))
        rgba.save(dst_path, "PNG")


def create_pixel_cyber_bird(base_bird_path: Path, dst_path: Path) -> None:
    """Tạo skin Cyber Bird pixel art 34x24 dựa trên phôi chim gốc với visor neon cyan."""
    with Image.open(base_bird_path) as img:
        rgba = img.convert("RGBA")
    
    # Đổi bảng màu vàng sang tông kim loại bạc/xám
    data = list(rgba.getdata())
    new_data = []
    for r, g, b, a in data:
        if a == 0:
            new_data.append((0, 0, 0, 0))
        elif r > 200 and g > 150 and b < 100:  # Thân vàng
            gray = int(r * 0.3 + g * 0.59 + b * 0.11)
            new_data.append((gray, min(255, gray + 10), min(255, gray + 25), a))
        elif r > 200 and g < 100:  # Mỏ cam
            new_data.append((0, 220, 200, a))  # Mỏ cyan công nghệ
        else:
            new_data.append((r, g, b, a))
    
    rgba.putdata(new_data)
    draw = ImageDraw.Draw(rgba)
    
    # Visor kính công nghệ xanh neon cyan qua vùng mắt
    # Mắt chim thường ở quanh x=20..28, y=6..14
    draw.rectangle([18, 8, 27, 12], fill=(0, 255, 210, 240), outline=(0, 180, 150, 255))
    draw.line([12, 10, 17, 10], fill=(0, 255, 210, 255), width=1)
    
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(dst_path, "PNG")


def create_pixel_golden_bird(base_bird_path: Path, dst_path: Path) -> None:
    """Tạo skin Golden Bird pixel art 34x24 dựa trên phôi chim gốc với vương miện hoàng kim trên đỉnh mào đầu."""
    with Image.open(base_bird_path) as img:
        rgba = img.convert("RGBA")
    
    # 1. Tăng ánh kim rực rỡ cho thân chim
    data = list(rgba.getdata())
    new_data = []
    for r, g, b, a in data:
        if a == 0:
            new_data.append((0, 0, 0, 0))
        elif r > 180 and g > 120 and b < 120:  # Thân vàng óng
            new_data.append((255, 225, 30, a))
        else:
            new_data.append((r, g, b, a))
    
    rgba.putdata(new_data)
    draw = ImageDraw.Draw(rgba)
    
    # 2. Vương miện hoàng kim 3 chóp trên mào đầu (x=13..19, y=0..2)
    # Hoàn toàn nằm ngoài vùng mắt (x >= 20), bảo toàn 100% kích thước 34x24 và hitbox
    GOLD_LIGHT = (255, 245, 100, 255)
    GOLD_MID = (255, 215, 0, 255)
    GOLD_DARK = (180, 130, 0, 255)
    RUBY = (230, 25, 25, 255)
    
    # Row 0: 3 đỉnh chóp vàng ánh kim
    draw.point((13, 0), fill=GOLD_LIGHT)
    draw.point((16, 0), fill=GOLD_LIGHT)
    draw.point((19, 0), fill=GOLD_LIGHT)
    
    # Row 1: Thân vương miện + ngọc ruby ở tâm
    for x in range(13, 20):
        if x in (13, 19):
            draw.point((x, 1), fill=GOLD_DARK)
        elif x == 16:
            draw.point((x, 1), fill=RUBY)
        else:
            draw.point((x, 1), fill=GOLD_MID)
            
    # Row 2: Đai đế vương miện viền đậm ôm sát mào đầu
    for x in range(13, 19):
        draw.point((x, 2), fill=GOLD_DARK)
    
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(dst_path, "PNG")


def import_all_assets(
    ref_dir: Path = REF_SPRITES_DIR,
    uploaded_robin: Optional[Path] = UPLOADED_ROBIN_PATH,
) -> None:
    """Nhập toàn bộ sprites và skins chuẩn."""
    sprites_dst = ASSETS_DIR / "sprites"
    digits_dst = sprites_dst / "digits"
    skins_dst = ASSETS_DIR / "skins"

    sprites_dst.mkdir(parents=True, exist_ok=True)
    digits_dst.mkdir(parents=True, exist_ok=True)
    skins_dst.mkdir(parents=True, exist_ok=True)

    # 1. Môi trường & UI Banners
    env_sprites = [
        "background-day.png",
        "background-night.png",
        "base.png",
        "pipe-green.png",
        "pipe-red.png",
        "message.png",
        "gameover.png",
    ]
    for name in env_sprites:
        src = ref_dir / name
        if src.exists():
            dst = sprites_dst / name
            convert_and_save(src, dst)
            if name == "message.png":
                erase_grey_bird_from_message(dst)

    # 2. Chữ số retro 0-9
    for i in range(10):
        src = ref_dir / f"{i}.png"
        if src.exists():
            convert_and_save(src, digits_dst / f"{i}.png")

    # 3. Skins cơ bản (Lấy midflap tĩnh 34x24 px)
    skin_mappings = {
        "classic.png": ref_dir / "yellowbird-midflap.png",
        "blue_bird.png": ref_dir / "bluebird-midflap.png",
        "red_bird.png": ref_dir / "redbird-midflap.png",
    }
    for dst_name, src in skin_mappings.items():
        if src.exists():
            convert_and_save(src, skins_dst / dst_name)

    # 4. Skins tinh chỉnh nâng cao
    classic_path = skins_dst / "classic.png"
    if classic_path.exists():
        create_pixel_cyber_bird(classic_path, skins_dst / "cyber_bird.png")
        create_pixel_golden_bird(classic_path, skins_dst / "golden_bird.png")

    # 5. Custom Skin Robin Thiên Thần (Bảo toàn 100% độ phân giải 1023x512)
    if uploaded_robin and uploaded_robin.exists():
        convert_and_save(uploaded_robin, skins_dst / "custom_robin.png")
    
    print("Authentic assets and custom skin imported successfully!")


if __name__ == "__main__":
    import_all_assets()
