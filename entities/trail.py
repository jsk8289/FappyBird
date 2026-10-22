"""Thực thể quản lý hiệu ứng vệt bay (Trail Emitter, Particle & Ghost Snapshot)."""
import random
from typing import Any, Optional, Union

import arcade

from ..constants import ASSETS_DIR
from ..models.trail import DEFAULT_TRAILS, TRAILS_SPRITES_DIR, Trail


class TrailParticle(arcade.Sprite):

    """Hạt vệt bay di chuyển với vận tốc (vx, vy), tuổi thọ cố định và alpha mờ dần."""

    def __init__(
        self,
        texture: Optional[arcade.Texture] = None,
        scale: float = 1.0,
        center_x: float = 0.0,
        center_y: float = 0.0,
        vx: float = 0.0,
        vy: float = 0.0,
        life: float = 1.0,
        max_alpha: int = 220,
        color: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        super().__init__(
            path_or_texture=texture,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )
        self.vx = vx
        self.vy = vy
        self.life = max(0.01, life)
        self.max_alpha = max_alpha
        self.age = 0.0
        self.color = (color[0], color[1], color[2], max_alpha)

    def update_particle(self, dt: float) -> bool:
        """Cập nhật tọa độ và độ trong suốt. Trả về False nếu hạt đã hết hạn."""
        self.age += dt
        if self.age >= self.life:
            return False

        self.center_x += self.vx * dt
        self.center_y += self.vy * dt

        progress = min(1.0, self.age / self.life)
        new_alpha = int(self.max_alpha * (1.0 - progress))
        cur_rgb = self.color[:3]
        self.color = (cur_rgb[0], cur_rgb[1], cur_rgb[2], max(0, new_alpha))
        return True


class GhostSnapshot(arcade.Sprite):
    """Bóng ma chụp lại hình dáng, tỷ lệ scale và góc nghiêng của chim, trôi lùi theo thế giới."""

    def __init__(
        self,
        texture: Optional[arcade.Texture] = None,
        scale: float = 1.0,
        center_x: float = 0.0,
        center_y: float = 0.0,
        angle: float = 0.0,
        vx: float = 0.0,
        life: float = 0.80,
        max_alpha: int = 160,
        color_tint: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        super().__init__(
            path_or_texture=texture,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
            angle=angle,
        )
        self.vx = vx
        self.life = max(0.01, life)
        self.max_alpha = max_alpha
        self.age = 0.0
        self.color = (color_tint[0], color_tint[1], color_tint[2], max_alpha)

    def update_ghost(self, dt: float) -> bool:
        """Cập nhật độ mờ dần và vị trí trôi ngang. Trả về False khi hết hạn."""
        self.age += dt
        if self.age >= self.life:
            return False

        self.center_x += self.vx * dt

        progress = min(1.0, self.age / self.life)
        new_alpha = int(self.max_alpha * (1.0 - progress))
        cur_rgb = self.color[:3]
        self.color = (cur_rgb[0], cur_rgb[1], cur_rgb[2], max(0, new_alpha))
        return True


class TrailEmitter:
    """Quản lý sinh hạt, vòng đời và vẽ các hiệu ứng vệt bay (Particle & Ghost)."""

    MAX_PARTICLES: int = 50
    EMIT_INTERVAL: float = 0.08
    PARTICLE_LIFE: float = 1.0
    GHOST_LIFE: float = 0.80
    BURST_COUNT: int = 5
    BURST_LIFE: float = 0.25
    BURST_ALPHA: int = 240
    BURST_OFFSET_X: float = 14.0
    BURST_OFFSET_Y: float = 10.0
    BURST_VELOCITY_Y_RANGE: tuple[float, float] = (20.0, 30.0)

    def __init__(
        self,
        active_trail_id: Optional[str] = None,
        is_active: bool = True,
        preview_mode: bool = False,
    ) -> None:
        self.particles = arcade.SpriteList()
        self.current_trail: Optional[Trail] = None
        self.particle_texture: Optional[arcade.Texture] = None
        self.particle_scale: float = 2.0
        self.emit_timer: float = 0.0
        self.is_active: bool = is_active
        self.preview_mode: bool = preview_mode
        if active_trail_id:
            self.set_trail(active_trail_id)

    @property
    def active_trail_id(self) -> str:
        return self.current_trail.id if self.current_trail else "none"

    @property
    def emit_interval(self) -> float:
        return 0.045 if self.preview_mode else self.EMIT_INTERVAL

    @property
    def particle_life(self) -> float:
        return self.PARTICLE_LIFE

    @property
    def ghost_life(self) -> float:
        return self.GHOST_LIFE

    def calculate_auto_scale(self, texture: Optional[arcade.Texture]) -> float:
        """Chuẩn hóa kích thước hạt theo Bounding Box (cạnh lớn nhất nằm trong khung 18x18 px)."""
        if not texture:
            return 2.0
        w = float(getattr(texture, "width", 18.0) or 18.0)
        h = float(getattr(texture, "height", 18.0) or 18.0)
        max_dim = max(1.0, max(w, h))
        return 18.0 / max_dim

    def set_trail(self, trail: Union[Trail, str, None]) -> None:
        """Chuyển đổi sang cấu hình vệt bay mới và nạp trước texture hạt nếu cần."""
        if isinstance(trail, str):
            trail = next((t for t in DEFAULT_TRAILS if t.id == trail), None)

        self.current_trail = trail
        self.clear()
        self.emit_timer = 0.0
        self.particle_texture = None
        self.particle_scale = 2.0

        if not trail or trail.trail_type == "none":
            return

        if trail.trail_type == "particle":
            try:
                self.particle_texture = arcade.load_texture(trail.sprite_path)
            except Exception:
                try:
                    self.particle_texture = arcade.load_texture(TRAILS_SPRITES_DIR / "primo.png")
                except Exception:
                    self.particle_texture = None

            self.particle_scale = self.calculate_auto_scale(self.particle_texture)

    def _add_particle(self, sprite: arcade.Sprite) -> None:
        """Thêm hạt mới vào danh sách kèm chính sách FIFO (giải phóng hạt cũ nhất khi vượt ngưỡng 50)."""
        while len(self.particles) >= self.MAX_PARTICLES:
            oldest = self.particles[0]
            oldest.remove_from_sprite_lists()
        self.particles.append(sprite)

    def update(
        self,
        dt: float,
        world_speed: float = 180.0,
        bird_x: float = 0.0,
        bird_y: float = 0.0,
        bird_angle: float = 0.0,
        bird_texture: Optional[arcade.Texture] = None,
        bird_scale: float = 1.0,
        bird_pos: Optional[tuple[float, float]] = None,
        bird_sprite: Optional[arcade.Sprite] = None,
        **kwargs: Any,
    ) -> None:
        """Cập nhật toàn bộ hạt hiện có và sinh hạt mới theo định kỳ khi bay."""
        # 1. Cập nhật các hạt / bóng ma đang sống
        for p in list(self.particles):
            if isinstance(p, TrailParticle):
                if not p.update_particle(dt):
                    p.remove_from_sprite_lists()
            elif isinstance(p, GhostSnapshot):
                if not p.update_ghost(dt):
                    p.remove_from_sprite_lists()

        if not self.is_active:
            return

        if bird_pos is not None:
            bird_x, bird_y = bird_pos
        if bird_sprite is not None:
            bird_x = bird_sprite.center_x
            bird_y = bird_sprite.center_y
            bird_angle = bird_sprite.angle
            bird_texture = bird_sprite.texture
            bird_scale = getattr(bird_sprite, "scale", 1.0)

        # 2. Sinh hạt mới nếu đang trang bị trail hoạt động
        if not self.current_trail or self.current_trail.trail_type == "none":
            return

        self.emit_timer += dt
        interval = max(0.001, self.emit_interval)
        drift_vx = -0.55 * world_speed

        while self.emit_timer >= interval:
            self.emit_timer -= interval
            spawn_x = bird_x - 14.0
            spawn_y = bird_y + random.uniform(-3.0, 3.0)

            if self.current_trail.trail_type == "particle" and self.particle_texture:
                vx = drift_vx + random.uniform(-8.0, 8.0)
                vy = self._get_vertical_velocity(self.current_trail.id)
                scale = self.particle_scale * random.uniform(0.5, 1.0)
                particle = TrailParticle(
                    texture=self.particle_texture,
                    scale=scale,
                    center_x=spawn_x,
                    center_y=spawn_y,
                    vx=vx,
                    vy=vy,
                    life=self.particle_life,
                    max_alpha=220,
                    color=self.current_trail.color_tint,
                )
                self._add_particle(particle)

            elif self.current_trail.trail_type == "ghost" and bird_texture:
                ghost = GhostSnapshot(
                    texture=bird_texture,
                    scale=bird_scale,
                    center_x=bird_x,
                    center_y=bird_y,
                    angle=bird_angle,
                    vx=drift_vx,
                    life=self.ghost_life,
                    max_alpha=150,
                    color_tint=self.current_trail.color_tint,
                )
                self._add_particle(ghost)

    def burst(
        self,
        bird_x: float,
        bird_y: float,
        _bird_angle: float = 0.0,
        _bird_texture: Optional[arcade.Texture] = None,
        _bird_scale: float = 1.0,
        _world_speed: float = 180.0,
        **kwargs: Any,
    ) -> None:
        """Kích hoạt phản hồi thị giác tức thì khi chim ấn nhảy (flap).

        Sinh các hạt ngẫu nhiên xung quanh thân chim, không lùi về sau,
        nổi nhẹ lên theo đà nhảy và tan biến cực nhanh (0.25s).
        Loại vệt Ghost không sinh thêm khi nhảy.
        """
        if not self.is_active or not self.current_trail or self.current_trail.trail_type != "particle" or not self.particle_texture:
            return

        for _ in range(self.BURST_COUNT):
            spawn_x = bird_x + random.uniform(-self.BURST_OFFSET_X, self.BURST_OFFSET_X)
            spawn_y = bird_y + random.uniform(-self.BURST_OFFSET_Y, self.BURST_OFFSET_Y)
            vx = random.uniform(-5.0, 5.0)
            vy = random.uniform(self.BURST_VELOCITY_Y_RANGE[0], self.BURST_VELOCITY_Y_RANGE[1])
            scale = self.particle_scale * random.uniform(0.5, 1.0)
            particle = TrailParticle(
                texture=self.particle_texture,
                scale=scale,
                center_x=spawn_x,
                center_y=spawn_y,
                vx=vx,
                vy=vy,
                life=self.BURST_LIFE,
                max_alpha=self.BURST_ALPHA,
                color=self.current_trail.color_tint,
            )
            self._add_particle(particle)

    def _get_vertical_velocity(self, trail_id: str) -> float:
        """Tính vận tốc dọc phù hợp với từng chủ đề hạt."""
        if trail_id in ("fire", "fiery"):
            return random.uniform(20.0, 50.0)
        elif trail_id == "heart":
            return random.uniform(5.0, 25.0)
        elif trail_id in ("star", "money"):
            return random.uniform(-15.0, 15.0)
        elif trail_id in ("custom", "primo"):
            return random.uniform(-10.0, 20.0)
        else:
            return random.uniform(-10.0, 20.0)

    def draw(self) -> None:
        """Vẽ toàn bộ hạt qua batch draw của SpriteList."""
        self.particles.draw()

    def clear(self) -> None:
        """Dọn dẹp sạch sẽ toàn bộ hạt trên màn hình."""
        self.particles.clear()
