
import logging
from pathlib import Path
from typing import Optional

import arcade

from ..constants import ASSETS_DIR

logger = logging.getLogger(__name__)


class AudioService:
    def __init__(self, audio_dir: Optional[Path] = None) -> None:
        self.audio_dir = audio_dir or (ASSETS_DIR / "audio")
        self.sounds: dict[str, Optional[arcade.Sound]] = {}
        self._load_sounds()

    def _load_sounds(self) -> None:
        sound_names = ["wing", "point", "hit", "die", "swoosh"]
        for name in sound_names:
            file_path = self.audio_dir / f"{name}.wav"
            if file_path.exists():
                try:
                    self.sounds[name] = arcade.load_sound(file_path)
                except Exception as e:
                    logger.warning("Không thể nạp âm thanh %s: %s", file_path, e)
                    self.sounds[name] = None
            else:
                self.sounds[name] = None

    def play(self, name: str) -> None:

        sound = self.sounds.get(name)
        if sound:
            try:
                arcade.play_sound(sound)
            except Exception as e:
                logger.debug("Lỗi khi phát âm thanh %s: %s", name, e)

    def play_wing(self) -> None:
        self.play("wing")

    def play_point(self) -> None:
        self.play("point")

    def play_hit(self) -> None:
        self.play("hit")

    def play_die(self) -> None:
        self.play("die")

    def play_swoosh(self) -> None:
        self.play("swoosh")
