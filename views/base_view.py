"""BaseView quản lý Camera2D ảo (288x512), Letterbox và F11 Fullscreen."""
from typing import TYPE_CHECKING, Tuple

import arcade
from arcade.camera import Camera2D
from arcade.types import Rect

from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH

if TYPE_CHECKING:
    from ..main import FlappyWindow


class BaseView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self._camera: Camera2D | None = None

    @property
    def flappy_window(self) -> "FlappyWindow":
        return self.window  # type: ignore

    def on_show_view(self) -> None:
        """Kích hoạt khi chuyển sang view này."""
        if not self._camera:
            self._camera = Camera2D(window=self.window)
        if self.window and hasattr(self.window, "ctx") and hasattr(self.window.ctx, "default_atlas") and self.window.ctx.default_atlas:
            import pyglet.gl as gl
            self.window.ctx.default_atlas.texture.filter = (gl.GL_NEAREST, gl.GL_NEAREST)
        self.update_camera()

    def update_camera(self, width: int | None = None, height: int | None = None) -> None:
        """Tính toán tỷ lệ Letterbox/Pillarbox và gán viewport ảo 288x512."""
        if not self._camera:
            return

        win_w = width if width is not None else self.window.width
        win_h = height if height is not None else self.window.height
        if win_w <= 0 or win_h <= 0:
            return

        scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
        vp_w = max(1, int(SCREEN_WIDTH * scale))
        vp_h = max(1, int(SCREEN_HEIGHT * scale))
        vp_left = int((win_w - vp_w) / 2.0)
        vp_bottom = int((win_h - vp_h) / 2.0)

        vp_rect = Rect.from_kwargs(
            left=vp_left,
            right=vp_left + vp_w,
            bottom=vp_bottom,
            top=vp_bottom + vp_h,
        )
        self._camera.viewport = vp_rect
        self._camera.width = float(SCREEN_WIDTH)
        self._camera.height = float(SCREEN_HEIGHT)
        self._camera.position = (SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0)
        self._camera.scissor = vp_rect

    def on_resize(self, width: int, height: int) -> None:
        """Tự động tính lại letterbox khi cửa sổ thay đổi kích thước."""
        super().on_resize(width, height)
        self.update_camera(width, height)

    def unproject_mouse(self, x: float, y: float) -> Tuple[float, float]:
        """Ánh xạ tọa độ chuột từ pixel màn hình thực sang tọa độ thế giới ảo 288x512."""
        if not self._camera:
            return x, y
        vec = self._camera.unproject((x, y))
        return vec.x, vec.y

    def on_draw(self) -> None:
        """Xóa toàn bộ viền màn hình màu đen và kích hoạt camera chiếu thế giới ảo."""
        self.window.ctx.scissor = None
        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)
        self.clear(color=(0, 0, 0, 255))
        if self._camera:
            self._camera.use()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Hỗ trợ phím tắt F11 chuyển đổi Fullscreen toàn cục."""
        if symbol == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.update_camera()
