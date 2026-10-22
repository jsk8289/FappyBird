
from pathlib import Path
from typing import Optional

import arcade

from ..constants import ASSETS_DIR, SCREEN_HEIGHT, SCREEN_WIDTH


class ScoreDisplay:


    def __init__(self, digits_dir: Optional[Path] = None, center_y: float = SCREEN_HEIGHT - 60.0) -> None:
        self.digits_dir = digits_dir or (ASSETS_DIR / "sprites" / "digits")
        self.center_y = center_y
        self.digit_textures: dict[int, arcade.Texture] = {}
        self.load_textures()

        self.sprites = arcade.SpriteList()
        self.current_score: int = -1
        self.set_score(0)

    def load_textures(self) -> None:

        for i in range(10):
            p = self.digits_dir / f"{i}.png"
            if p.exists():
                self.digit_textures[i] = arcade.load_texture(p)

    def set_score(self, score: int) -> None:

        score = max(0, score)
        if score == self.current_score:
            return
        self.current_score = score
        self.sprites.clear()

        score_str = str(score)
        textures = [self.digit_textures.get(int(ch)) for ch in score_str]
        if any(t is None for t in textures):
            return

        total_width = sum(t.width for t in textures)
        start_x = (SCREEN_WIDTH - total_width) / 2.0

        current_x = start_x
        for t in textures:
            s = arcade.Sprite(t)
            s.center_x = current_x + t.width / 2.0
            s.center_y = self.center_y
            self.sprites.append(s)
            current_x += t.width

    def draw(self) -> None:

        self.sprites.draw()
