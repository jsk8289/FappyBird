"""Công cụ sao chép và chuẩn hóa 5 texture vịt/phượng hoàng từ Desktop sang assets/skins/."""
from pathlib import Path
from PIL import Image

from ..constants import ASSETS_DIR

DUCKS_SRC_DIR = Path(r"C:\Users\Admin\Desktop\ducks\trimmed")

DUCK_ASSET_MAPPINGS = {
    "Yello.png": "yellow.png",
    "Electric Blue Pixel Bird Sprite.png": "electric.png",
    "Cybernetic Pixel Art Duck Sprite.png": "cyber.png",
    "Royal Golden Bird Pixel Sprite.png": "royal.png",
    "Fiery Pixel Phoenix Sprite.png": "fiery.png",
}


def import_duck_skins(src_dir: Path = DUCKS_SRC_DIR, dst_dir: Path = ASSETS_DIR / "skins") -> None:
    """Sao chép 5 texture mới vào assets/skins/ và bảo đảm định dạng RGBA."""
    dst_dir.mkdir(parents=True, exist_ok=True)

    for src_filename, dst_filename in DUCK_ASSET_MAPPINGS.items():
        src_path = src_dir / src_filename
        dst_path = dst_dir / dst_filename

        if not src_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file nguồn: {src_path}")

        with Image.open(src_path) as img:
            rgba_img = img.convert("RGBA")
            rgba_img.save(dst_path, "PNG")
            print(f"Imported: {src_filename} -> {dst_path.name} ({rgba_img.size})")


if __name__ == "__main__":
    import_duck_skins()
