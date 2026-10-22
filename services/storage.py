"""Dịch vụ lưu trữ và nạp dữ liệu tiến trình (SaveData)."""
import json
import logging
import os
from pathlib import Path
from typing import Optional

from ..constants import SAVE_FILE
from ..models.save_data import SaveData

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self, save_path: Optional[Path] = None) -> None:
        self.save_path = save_path or SAVE_FILE

    def load(self) -> SaveData:
        """Nạp dữ liệu từ file JSON. Tự động fallback về mặc định nếu lỗi hoặc chưa có file."""
        if not self.save_path.exists():
            return SaveData()

        try:
            with open(self.save_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            return SaveData.from_dict(data)
        except (json.JSONDecodeError, OSError, ValueError, TypeError) as e:
            logger.warning("Không thể đọc file save_data.json (%s). Sử dụng dữ liệu mặc định.", e)
            return SaveData()

    def save(self, save_data: SaveData) -> bool:
        """Ghi dữ liệu ra file JSON an toàn bằng cơ chế atomic write (.tmp -> rename)."""
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.save_path.with_suffix(".tmp")

            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(save_data.to_dict(), f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            # Atomic replace (an toàn trên cả Windows lẫn Unix)
            os.replace(temp_path, self.save_path)
            return True
        except OSError as e:
            logger.error("Lỗi khi lưu save_data.json: %s", e)
            return False
