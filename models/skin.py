"""Định nghĩa dữ liệu Skin và danh mục skin mặc định."""
from dataclasses import dataclass
from typing import Literal

from ..constants import ASSETS_DIR

UnlockType = Literal["default", "coin", "highscore", "total_coins"]


@dataclass(frozen=True)
class Skin:
    id: str
    name: str
    price: int
    unlock_type: UnlockType
    unlock_value: int
    sprite_path: str
    description: str = ""


# Danh mục 6 skin khởi tạo
DEFAULT_SKINS: list[Skin] = [
    Skin(
        id="yellow",
        name="Yellow Duck",
        price=0,
        unlock_type="default",
        unlock_value=0,
        sprite_path=str(ASSETS_DIR / "skins" / "yellow.png"),
        description="The friendly yellow duck.\nUnlocked by Default",
    ),
    Skin(
        id="electric",
        name="Lightning Blue",
        price=10,
        unlock_type="coin",
        unlock_value=10,
        sprite_path=str(ASSETS_DIR / "skins" / "electric.png"),
        description="Agile electric flyer.\nUnlock: 10 Coins",
    ),
    Skin(
        id="cyber",
        name="Cybernetic",
        price=0,
        unlock_type="highscore",
        unlock_value=25,
        sprite_path=str(ASSETS_DIR / "skins" / "cyber.png"),
        description="Futuristic cyborg duck.\nUnlock: High Score >= 25",
    ),
    Skin(
        id="royal",
        name="Royal Gold",
        price=0,
        unlock_type="total_coins",
        unlock_value=100,
        sprite_path=str(ASSETS_DIR / "skins" / "royal.png"),
        description="Crowned majestic duck.\nUnlock: Total Coins >= 100",
    ),
    Skin(
        id="fiery",
        name="Fiery Phoenix",
        price=0,
        unlock_type="highscore",
        unlock_value=50,
        sprite_path=str(ASSETS_DIR / "skins" / "fiery.png"),
        description="Blazing mythical phoenix.\nUnlock: High Score >= 50",
    ),
    Skin(
        id="custom_robin",
        name="Angel Robin",
        price=0,
        unlock_type="default",
        unlock_value=0,
        sprite_path=str(ASSETS_DIR / "skins" / "custom_robin.png"),
        description="Heavenly angel robin.\nUnlocked by Default",
    ),
]

