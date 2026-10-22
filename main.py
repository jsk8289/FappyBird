
from typing import Optional

import pyglet
# Tắt DirectWrite/font antialiasing toàn cục cho pixel art typography
pyglet.options.text_antialiasing = False
import pyglet.gl as gl

import arcade
from arcade.texture_atlas.atlas_default import DefaultTextureAtlas

from .constants import ASSETS_DIR, SCREEN_HEIGHT, SCREEN_WIDTH, ensure_retro_font_loaded
from .models.save_data import SaveData
from .services.audio import AudioService
from .services.skin_manager import SkinManager
from .services.storage import StorageService
from .services.trail_manager import TrailManager
from .tools.generate_placeholders import ensure_assets_exist

# Cấu hình Nearest-Neighbor toàn cục cho mọi SpriteList
arcade.SpriteList.DEFAULT_TEXTURE_FILTER = (gl.GL_NEAREST, gl.GL_NEAREST)

# Patch DefaultTextureAtlas.resize để duy trì GL_NEAREST khi atlas mở rộng
_orig_atlas_resize = DefaultTextureAtlas.resize

#GL_NEAREST
def _nearest_atlas_resize(self, size, force=False):
    _orig_atlas_resize(self, size, force=force)
    if hasattr(self, "_texture") and self._texture is not None:
        self._texture.filter = (gl.GL_NEAREST, gl.GL_NEAREST)


DefaultTextureAtlas.resize = _nearest_atlas_resize


class FlappyWindow(arcade.Window):
    def __init__(self, storage: Optional[StorageService] = None, visible: bool = True) -> None:
        #Tự động tạo asset placeholder nếu thiếu trước khi engine khởi chạy (DX-1)
        ensure_assets_exist()
        ensure_retro_font_loaded()

        super().__init__(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            title="Flappy Bird",
            resizable=True,
            antialiasing=False,
            visible=visible,
        )

        #Cấu hình bộ lọc Nearest-Neighbor cho atlas chính của context
        if hasattr(self.ctx, "default_atlas") and self.ctx.default_atlas:
            self.ctx.default_atlas.texture.filter = (gl.GL_NEAREST, gl.GL_NEAREST)

        #phần âm thanh
        self.storage = storage or StorageService()
        self.save_data: SaveData = self.storage.load()
        self.audio = AudioService()
        self.skin_manager = SkinManager()
        self.trail_manager = TrailManager()

        #Cache texture của skin đang trang bị
        self.current_skin_texture: Optional[arcade.Texture] = None
        self.reload_skin_texture()

        #Cờ Debug Mode (DX-2)
        self.debug_hitbox: bool = False
        self.god_mode: bool = False

    def reload_skin_texture(self) -> None:

        equipped_id = self.save_data.equipped_skin
        skin_obj = self.skin_manager.get_skin(equipped_id) or self.skin_manager.skins[0]
        try:
            self.current_skin_texture = arcade.load_texture(skin_obj.sprite_path)
        except Exception:
            self.current_skin_texture = arcade.load_texture(ASSETS_DIR / "skins" / "yellow.png")

    def save_progress(self) -> None:

        self.storage.save(self.save_data)


def main() -> None:
    window = FlappyWindow()
    from .views.start_view import StartView

    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
