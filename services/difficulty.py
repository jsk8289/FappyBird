"""Dịch vụ đường cong độ khó (Difficulty Curve) với Lerp liên tục."""
from ..constants import (
    INITIAL_PIPE_GAP,
    INITIAL_PIPE_SPEED,
    LERP_SPEED_FACTOR,
    MAX_PIPE_SPEED,
    MIN_PIPE_GAP,
)


class DifficultyService:
    def __init__(self) -> None:
        self.current_speed: float = INITIAL_PIPE_SPEED
        self.current_gap: float = INITIAL_PIPE_GAP

    def get_target_difficulty(self, score: int) -> tuple[float, float]:
        """Tính toán mục tiêu (target_speed, target_gap) bằng nội suy tuyến tính dựa theo score.

        Các mốc độ khó chuẩn:
        - score <= 0: (180.0, 150.0)
        - 0 < score < 10: lerp từ (180, 150) lên (220, 135)
        - 10 <= score < 25: lerp từ (220, 135) lên (260, 120)
        - 25 <= score < 50: lerp từ (260, 120) lên (300, 110)
        - score >= 50: (300.0, 110.0)
        """
        if score <= 0:
            return (180.0, 150.0)
        elif score < 10:
            t = score / 10.0
            return (180.0 + (220.0 - 180.0) * t, 150.0 + (135.0 - 150.0) * t)
        elif score < 25:
            t = (score - 10.0) / 15.0
            return (220.0 + (260.0 - 220.0) * t, 135.0 + (120.0 - 135.0) * t)
        elif score < 50:
            t = (score - 25.0) / 25.0
            return (260.0 + (300.0 - 260.0) * t, 120.0 + (110.0 - 120.0) * t)
        else:
            return (MAX_PIPE_SPEED, MIN_PIPE_GAP)

    def update(self, dt: float, score: int) -> None:
        """Cập nhật các giá trị tốc độ và khoảng hở hiện tại mượt mà qua lerp."""
        target_speed, target_gap = self.get_target_difficulty(score)
        factor = min(1.0, LERP_SPEED_FACTOR * dt)

        # Lerp: current = current + (target - current) * factor
        self.current_speed += (target_speed - self.current_speed) * factor
        self.current_gap += (target_gap - self.current_gap) * factor

    def reset(self) -> None:
        """Đặt lại độ khó ban đầu khi bắt đầu ván mới."""
        self.current_speed = INITIAL_PIPE_SPEED
        self.current_gap = INITIAL_PIPE_GAP
