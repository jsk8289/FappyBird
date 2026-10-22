"""Thực thể Mặt đất (Floor) cuộn ngang tuần hoàn mượt mà."""
import arcade

from ..constants import ASSETS_DIR, FLOOR_HEIGHT


class Floor(arcade.Sprite):
    def __init__(self, texture_path: str = str(ASSETS_DIR / "sprites" / "base.png")) -> None:
        super().__init__(path_or_texture=texture_path)
        # base.png có kích cỡ 336x112, họa tiết lặp chu kỳ mỗi 16 px
        self.pattern_repeat: float = 16.0
        self.scroll_offset: float = 0.0
        self.reset()

    def update_scroll(self, dt: float, world_speed: float) -> None:
        """Cuộn mặt sàn sang trái theo chu kỳ vân 16px liền mạch, không để hở viền."""
        self.scroll_offset = (self.scroll_offset + world_speed * dt) % self.pattern_repeat
        self.left = -self.scroll_offset

    def reset(self) -> None:
        """Khởi tạo lại trạng thái mặt sàn tại gốc tọa độ."""
        self.scroll_offset = 0.0
        self.left = 0.0
        self.top = FLOOR_HEIGHT

