"""Công cụ tự động sinh sprite pixel art placeholder và chuẩn bị âm thanh."""
import math
import os
import shutil
import struct
import wave
from pathlib import Path

from PIL import Image, ImageDraw

from ..constants import ASSETS_DIR, SCREEN_HEIGHT, SCREEN_WIDTH


def create_pipe_texture(color_body=(115, 191, 46), color_highlight=(142, 221, 62), color_shadow=(85, 142, 34), color_border=(50, 80, 20)) -> Image.Image:
    """Tạo sprite ống nước retro chuẩn 52x320 px với vành miệng ống (collar/lip)."""
    w, h = 52, 320
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    lip_h = 24
    # Vẽ thân ống (lip_h đến h)
    draw.rectangle([2, lip_h, w - 3, h - 1], fill=color_body, outline=color_border)
    # Highlight & shadow thân
    draw.line([6, lip_h + 1, 6, h - 2], fill=color_highlight, width=3)
    draw.line([w - 6, lip_h + 1, w - 6, h - 2], fill=color_shadow, width=4)

    # Vẽ vành miệng ống (collar)
    draw.rectangle([0, 0, w - 1, lip_h], fill=color_body, outline=color_border)
    draw.line([4, 1, 4, lip_h - 1], fill=color_highlight, width=3)
    draw.line([w - 4, 1, w - 4, lip_h - 1], fill=color_shadow, width=4)

    return im


def create_background_day() -> Image.Image:
    """Tạo nền ban ngày bầu trời xanh mây trắng và đồi cỏ 288x512."""
    w, h = SCREEN_WIDTH, SCREEN_HEIGHT
    im = Image.new("RGBA", (w, h), (78, 192, 202, 255))
    draw = ImageDraw.Draw(im)

    # Đồi xanh phía xa
    draw.ellipse([-50, 360, 180, 500], fill=(138, 208, 116, 255))
    draw.ellipse([100, 370, 340, 520], fill=(120, 192, 100, 255))

    # Mây trắng pixel
    for cx, cy in [(40, 100), (190, 70), (120, 180)]:
        draw.ellipse([cx, cy, cx + 50, cy + 25], fill=(240, 250, 255, 230))
        draw.ellipse([cx + 15, cy - 10, cx + 45, cy + 20], fill=(255, 255, 255, 255))

    return im


def create_background_night() -> Image.Image:
    """Tạo nền ban đêm bầu trời đen/lam đậm sao và trăng 288x512."""
    w, h = SCREEN_WIDTH, SCREEN_HEIGHT
    im = Image.new("RGBA", (w, h), (11, 26, 44, 255))
    draw = ImageDraw.Draw(im)

    # Mặt trăng
    draw.ellipse([210, 50, 250, 90], fill=(245, 240, 200, 255))
    draw.ellipse([200, 45, 240, 85], fill=(11, 26, 44, 255))

    # Đồi tối
    draw.ellipse([-50, 360, 180, 500], fill=(24, 48, 64, 255))
    draw.ellipse([100, 370, 340, 520], fill=(18, 38, 52, 255))

    return im


def create_base_texture() -> Image.Image:
    """Tạo sprite mặt đất cuộn ngang 336x112 với cỏ xanh và đất vàng."""
    w, h = 336, 112
    im = Image.new("RGBA", (w, h), (222, 216, 149, 255))
    draw = ImageDraw.Draw(im)

    # Viền cỏ xanh trên cùng
    draw.rectangle([0, 0, w - 1, 14], fill=(115, 191, 46, 255), outline=(50, 80, 20, 255))
    draw.line([0, 4, w - 1, 4], fill=(142, 221, 62, 255), width=2)

    # Các sọc chéo họa tiết pixel của đất
    for x in range(0, w, 16):
        draw.line([x, 15, x + 10, h - 1], fill=(210, 200, 130, 255), width=2)

    return im


def create_coin_texture() -> Image.Image:
    """Tạo icon đồng xu vàng 24x24 pixel."""
    w, h = 24, 24
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    draw.ellipse([2, 2, 21, 21], fill=(247, 181, 0, 255), outline=(180, 120, 0, 255), width=2)
    draw.ellipse([6, 6, 17, 17], fill=(255, 220, 50, 255))
    draw.point((8, 8), fill=(255, 255, 255, 255))
    draw.point((9, 8), fill=(255, 255, 255, 255))

    return im


def create_bird_skin(
    size: tuple[int, int],
    body_color: tuple[int, int, int],
    belly_color: tuple[int, int, int],
    wing_color: tuple[int, int, int],
    beak_color: tuple[int, int, int],
    extra_feature: str = "",
) -> Image.Image:
    """Tạo sprite chim pixel art căn giữa trong canvas `size`, giữ vùng thân ~34x24."""
    w, h = size
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    # Tâm canvas
    cx, cy = w // 2, h // 2

    # Thân chim (bầu dục 32x22 quanh tâm)
    bw, bh = 16, 11
    draw.ellipse([cx - bw, cy - bh, cx + bw, cy + bh], fill=body_color, outline=(40, 40, 40, 255), width=2)
    draw.ellipse([cx - bw + 4, cy + 2, cx + 4, cy + bh - 2], fill=belly_color)

    # Cánh chim
    draw.ellipse([cx - 10, cy - 3, cx + 2, cy + 6], fill=wing_color, outline=(40, 40, 40, 255), width=1)

    # Mắt to tròn trắng + con ngươi đen
    eye_x, eye_y = cx + 8, cy - 4
    draw.ellipse([eye_x - 4, eye_y - 4, eye_x + 4, eye_y + 4], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    draw.ellipse([eye_x + 1, eye_y - 2, eye_x + 3, eye_y], fill=(0, 0, 0, 255))

    # Mỏ cam nhọn hướng về bên phải
    draw.polygon([(cx + 12, cy - 2), (cx + 18, cy + 2), (cx + 12, cy + 5)], fill=beak_color, outline=(40, 40, 40, 255))

    # Tính năng đặc biệt (Phụ kiện / Visor / Vương miện)
    if extra_feature == "cyber":
        # Visor kính công nghệ xanh neon
        draw.rectangle([eye_x - 6, eye_y - 3, eye_x + 5, eye_y + 3], fill=(0, 255, 200, 230), outline=(0, 180, 150, 255))
        draw.line([cx - bw, cy, cx - 2, cy], fill=(0, 255, 200, 255), width=2)
    elif extra_feature == "crown":
        # Vương miện vàng ngọc đỏ trên đầu
        top_y = cy - bh
        draw.polygon(
            [(cx - 6, top_y), (cx - 8, top_y - 7), (cx - 3, top_y - 4), (cx, top_y - 9), (cx + 3, top_y - 4), (cx + 8, top_y - 7), (cx + 6, top_y)],
            fill=(255, 215, 0, 255),
            outline=(180, 120, 0, 255),
        )
        draw.point((cx, top_y - 5), fill=(255, 0, 50, 255))

    return im


def generate_synthesized_wav(filepath: Path, duration: float = 0.15, freq: float = 440.0, volume: float = 0.5) -> None:
    """Tạo file wav âm thanh đơn giản bằng thư viện chuẩn wave nếu thiếu file audio."""
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(filepath), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        data = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            # Sine wave kết hợp decay
            envelope = math.exp(-3.0 * t / duration)
            sample_val = int(32767.0 * volume * envelope * math.sin(2.0 * math.pi * freq * t))
            sample_val = max(-32768, min(32767, sample_val))
            data.extend(struct.pack("<h", sample_val))

        wav_file.writeframes(data)


def ensure_audio_files(audio_dir: Path) -> None:
    """Sao chép audio từ thư mục tham khảo (nếu có FLAPPY_REF_AUDIO_DIR), hoặc tự tổng hợp wav fallback."""
    audio_dir.mkdir(parents=True, exist_ok=True)
    ref_audio_env = os.environ.get("FLAPPY_REF_AUDIO_DIR")
    ref_audio_dir = Path(ref_audio_env) if ref_audio_env else None
    sfx_specs = {
        "wing.wav": 480.0,
        "hit.wav": 160.0,
        "die.wav": 120.0,
        "point.wav": 880.0,
        "swoosh.wav": 300.0,
    }

    for sfx_name, freq in sfx_specs.items():
        dest = audio_dir / sfx_name
        if dest.exists() and dest.stat().st_size > 0:
            continue

        # Thử copy từ source tham khảo nếu được cấu hình
        if ref_audio_dir is not None and (ref_audio_dir / sfx_name).exists():
            shutil.copy2(ref_audio_dir / sfx_name, dest)
        else:
            # Fallback tạo tiếng bíp điện tử chuẩn
            generate_synthesized_wav(dest, duration=0.18, freq=freq)


def create_star_particle_texture() -> Image.Image:
    """Tạo sprite hạt sao vàng 8x8 pixel."""
    w, h = 8, 8
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    # Thân sao vàng
    draw.rectangle([3, 1, 4, 6], fill=(255, 215, 0, 255))
    draw.rectangle([1, 3, 6, 4], fill=(255, 215, 0, 255))
    draw.rectangle([2, 2, 5, 5], fill=(255, 235, 50, 255))
    # Điểm sáng tâm
    draw.point((3, 3), fill=(255, 255, 255, 255))
    draw.point((4, 3), fill=(255, 255, 255, 255))
    return im


def create_heart_particle_texture() -> Image.Image:
    """Tạo sprite hạt tim hồng 8x8 pixel."""
    w, h = 8, 8
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    # 2 tai tim
    draw.rectangle([1, 1, 2, 3], fill=(255, 80, 130, 255))
    draw.rectangle([5, 1, 6, 3], fill=(255, 80, 130, 255))
    # Thân tim
    draw.rectangle([2, 1, 5, 4], fill=(255, 60, 110, 255))
    draw.rectangle([2, 4, 5, 5], fill=(255, 50, 100, 255))
    draw.rectangle([3, 6, 4, 6], fill=(230, 40, 80, 255))
    # Highlight
    draw.point((2, 2), fill=(255, 180, 210, 255))
    draw.point((5, 2), fill=(255, 180, 210, 255))
    return im


def create_fire_particle_texture() -> Image.Image:
    """Tạo sprite hạt lửa đỏ cam 8x8 pixel."""
    w, h = 8, 8
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    # Đế lửa đỏ đậm
    draw.rectangle([2, 5, 5, 7], fill=(220, 40, 20, 255))
    # Thân lửa cam
    draw.rectangle([2, 3, 5, 5], fill=(255, 120, 20, 255))
    draw.rectangle([3, 1, 4, 3], fill=(255, 200, 40, 255))
    # Nhân trắng sáng
    draw.rectangle([3, 4, 4, 5], fill=(255, 255, 180, 255))
    return im


def create_custom_trail_placeholder() -> Image.Image:
    """Tạo sprite placeholder cho Custom Trail (viên ngọc tím 16x16 pixel)."""
    w, h = 16, 16
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    # Hình thoi kim cương tím neon
    diamond = [(8, 1), (14, 8), (8, 14), (2, 8)]
    draw.polygon(diamond, fill=(160, 60, 240, 255), outline=(100, 20, 180, 255))
    inner = [(8, 3), (12, 8), (8, 12), (4, 8)]
    draw.polygon(inner, fill=(200, 110, 255, 255))
    # Điểm sáng trung tâm
    draw.rectangle([7, 7, 9, 9], fill=(255, 230, 255, 255))
    return im


def generate_trail_sprites(trails_dir: Path | None = None, overwrite: bool = False) -> None:
    """Tạo các sprite hạt vệt bay pixel art vào thư mục assets/trails/ nếu chưa tồn tại."""
    target_dir = trails_dir or (ASSETS_DIR / "trails")
    target_dir.mkdir(parents=True, exist_ok=True)

    def _save_if(img: Image.Image, path: Path) -> None:
        # Không bao giờ ghi đè sprite custom thật đã tồn tại
        if not path.exists():
            img.save(path)

    _save_if(create_star_particle_texture(), target_dir / "money.png")
    _save_if(create_heart_particle_texture(), target_dir / "heart.png")
    _save_if(create_fire_particle_texture(), target_dir / "fiery.png")
    _save_if(create_custom_trail_placeholder(), target_dir / "primo.png")


def generate_all_assets(overwrite: bool = False) -> None:
    """Tạo toàn bộ placeholder assets cho game nếu chưa có (mặc định không ghi đè)."""
    sprites_dir = ASSETS_DIR / "sprites"
    skins_dir = ASSETS_DIR / "skins"
    trails_dir = ASSETS_DIR / "trails"
    audio_dir = ASSETS_DIR / "audio"

    sprites_dir.mkdir(parents=True, exist_ok=True)
    skins_dir.mkdir(parents=True, exist_ok=True)
    trails_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    def _save_if(img: Image.Image, path: Path) -> None:
        if overwrite or not path.exists():
            img.save(path)

    # 1. Sprites môi trường
    _save_if(create_background_day(), sprites_dir / "background-day.png")
    _save_if(create_background_night(), sprites_dir / "background-night.png")
    _save_if(create_base_texture(), sprites_dir / "base.png")
    _save_if(create_pipe_texture(), sprites_dir / "pipe-green.png")
    _save_if(
        create_pipe_texture(color_body=(220, 60, 60), color_highlight=(250, 100, 100), color_shadow=(160, 40, 40)),
        sprites_dir / "pipe-red.png",
    )
    _save_if(create_coin_texture(), sprites_dir / "coin.png")

    # 2. Skins chim (Kích thước linh hoạt, thân chim chuẩn)
    _save_if(
        create_bird_skin((34, 24), body_color=(250, 200, 40), belly_color=(255, 230, 120), wing_color=(240, 120, 40), beak_color=(255, 100, 0)),
        skins_dir / "classic.png",
    )
    _save_if(
        create_bird_skin((32, 32), body_color=(40, 150, 240), belly_color=(120, 200, 255), wing_color=(20, 90, 190), beak_color=(255, 150, 0)),
        skins_dir / "blue_bird.png",
    )
    _save_if(
        create_bird_skin((32, 32), body_color=(230, 50, 50), belly_color=(255, 120, 120), wing_color=(170, 20, 20), beak_color=(255, 180, 0)),
        skins_dir / "red_bird.png",
    )
    _save_if(
        create_bird_skin((48, 32), body_color=(180, 190, 200), belly_color=(130, 140, 150), wing_color=(90, 100, 110), beak_color=(0, 220, 200), extra_feature="cyber"),
        skins_dir / "cyber_bird.png",
    )
    _save_if(
        create_bird_skin((64, 64), body_color=(255, 215, 0), belly_color=(255, 245, 150), wing_color=(218, 165, 32), beak_color=(255, 90, 0), extra_feature="crown"),
        skins_dir / "golden_bird.png",
    )

    # 3. Trails sprites (ngang hàng với skins)
    generate_trail_sprites(trails_dir, overwrite=overwrite)

    # 4. Âm thanh
    ensure_audio_files(audio_dir)
    print("Assets ensured successfully!")


def ensure_assets_exist(overwrite: bool = False) -> None:
    """Tự động kiểm tra và sinh asset nếu thiếu mà không ghi đè tài nguyên hiện có."""
    import sys
    if getattr(sys, "frozen", False):
        return

    required_files = [
        ASSETS_DIR / "sprites" / "background-day.png",
        ASSETS_DIR / "sprites" / "base.png",
        ASSETS_DIR / "sprites" / "pipe-green.png",
        ASSETS_DIR / "skins" / "yellow.png",
        ASSETS_DIR / "audio" / "wing.wav",
    ]
    if any(not f.exists() for f in required_files):
        generate_all_assets(overwrite=overwrite)

    # Đảm bảo thư mục trail sprites luôn có sẵn các sprite cơ bản
    generate_trail_sprites(ASSETS_DIR / "trails", overwrite=False)


if __name__ == "__main__":
    generate_all_assets()


