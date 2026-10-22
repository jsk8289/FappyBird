"""Thực thể Bird với Hitbox chuẩn hóa bất biến và động học bay/rơi."""
from typing import Optional

import arcade
import arcade.hitbox as hb

from ..constants import (
    FLAP_VELOCITY,
    GRAVITY,
    ROT_FLAP,
    ROT_MAX,
    ROT_MIN,
    ROT_VEL,
    STANDARD_HITBOX_HEIGHT,
    STANDARD_HITBOX_WIDTH,
    TERMINAL_VELOCITY,
)


class Bird(arcade.Sprite):
    def __init__(
        self,
        texture: Optional[arcade.Texture] = None,
        scale: Optional[float] = None,
        center_x: float = 0.0,
        center_y: float = 0.0,
        **kwargs,
    ) -> None:
        # Tự động tính scale sao cho chiều cao hiển thị luôn = STANDARD_HITBOX_HEIGHT (24.0 px)
        if scale is None:
            if texture is not None and getattr(texture, "height", 0) > 0:
                scale = STANDARD_HITBOX_HEIGHT / float(texture.height)
            else:
                scale = 1.0

        super().__init__(
            path_or_texture=texture,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
            **kwargs,
        )

        # Chuẩn hóa Hitbox bất biến: cố định 34x24 px bất chấp kích thước texture
        hw = STANDARD_HITBOX_WIDTH / 2.0
        hh = STANDARD_HITBOX_HEIGHT / 2.0
        standard_points = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        self.hit_box = hb.RotatableHitBox(standard_points, position=self.position)

        # Vận tốc theo trục Y
        self.velocity_y: float = 0.0

    def set_skin_texture(self, texture: Optional[arcade.Texture]) -> None:
        """Cập nhật texture mới cho chim và tự động cân chỉnh scale phù hợp."""
        if texture is not None:
            self.texture = texture
            if getattr(texture, "height", 0) > 0:
                self.scale = STANDARD_HITBOX_HEIGHT / float(texture.height)
            else:
                self.scale = 1.0

            # Phòng vệ: Tái khẳng định Hitbox chuẩn 34x24 px tâm (0, 0)
            hw = STANDARD_HITBOX_WIDTH / 2.0
            hh = STANDARD_HITBOX_HEIGHT / 2.0
            standard_points = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
            self.hit_box = hb.RotatableHitBox(standard_points, position=self.position)
        else:
            self.scale = 1.0


    def flap(self) -> None:
        """Thực hiện cú nhảy (vỗ cánh): gán vận tốc hướng lên và ngửa góc."""
        self.velocity_y = FLAP_VELOCITY
        self.angle = ROT_FLAP

    def update_physics(self, dt: float) -> None:
        """Cập nhật trọng lực, tọa độ và góc xoay qua từng bước thời gian dt."""
        # 1. Trọng lực & Giới hạn tốc độ rơi
        self.velocity_y = max(TERMINAL_VELOCITY, self.velocity_y + GRAVITY * dt)
        self.center_y += self.velocity_y * dt

        # 2. Xoay góc (Chúc đầu xuống khi rơi)
        if self.velocity_y < 0:
            self.angle = max(ROT_MIN, min(ROT_MAX, self.angle + ROT_VEL * dt))
        else:
            self.angle = min(ROT_MAX, max(ROT_MIN, self.angle))
