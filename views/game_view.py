"""GameView điều khiển vòng lặp chơi chính, va chạm, tính điểm và coin."""
import arcade

from ..constants import (
    ASSETS_DIR,
    BIRD_START_X,
    BIRD_START_Y,
    FIXED_DT,
    FLOOR_HEIGHT,
    FONT_RETRO_FAMILY,
    SCORE_PER_COIN,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from ..entities.bird import Bird
from ..entities.floor import Floor
from ..entities.pipe import PipeManager
from ..entities.score_display import ScoreDisplay
from ..entities.trail import TrailEmitter
from ..services.difficulty import DifficultyService
from .base_view import BaseView


class GameView(BaseView):
    def __init__(self) -> None:
        super().__init__()
        # Đối tượng môi trường
        self.background = arcade.Sprite(ASSETS_DIR / "sprites" / "background-day.png")
        self.background.center_x = SCREEN_WIDTH / 2.0
        self.background.center_y = SCREEN_HEIGHT / 2.0

        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.background)

        self.floor = Floor()
        self.floor_list = arcade.SpriteList()
        self.floor_list.append(self.floor)

        self.pipe_manager = PipeManager()
        self.difficulty = DifficultyService()
        self.trail_emitter = TrailEmitter()

        # Đối tượng chim
        self.bird: Bird | None = None
        self.bird_list = arcade.SpriteList()

        # Trạng thái gameplay
        self.score: int = 0
        self.coins_earned: int = 0
        self.accumulator: float = 0.0
        self.is_dead: bool = False

        # Khởi tạo hiển thị điểm retro và các đối tượng arcade.Text
        self.score_display = ScoreDisplay()
        self.score_text = arcade.Text(
            "0",
            SCREEN_WIDTH / 2.0,
            SCREEN_HEIGHT - 45.0,
            arcade.color.WHITE,
            font_size=28,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.coins_text = arcade.Text(
            "COINS: 0",
            SCREEN_WIDTH - 10.0,
            SCREEN_HEIGHT - 16.0,
            (255, 215, 0, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="right",
            anchor_y="center",
        )
        self.god_mode_text = arcade.Text(
            "GOD MODE ON",
            10.0,
            SCREEN_HEIGHT - 16.0,
            arcade.color.GREEN,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
        )


    def on_show_view(self) -> None:
        super().on_show_view()
        self.reset_game()

    def reset_game(self) -> None:
        """Khởi tạo lại trạng thái khi bắt đầu ván mới."""
        self.score = 0
        self.coins_earned = 0
        self.accumulator = 0.0
        self.is_dead = False
        self.score_display.set_score(0)
        self.score_text.text = "0"
        self.coins_text.text = f"COINS: {self.flappy_window.save_data.coins}"

        # Khởi tạo chim với texture skin hiện tại
        texture = self.flappy_window.current_skin_texture
        self.bird = Bird(
            texture=texture,
            center_x=float(BIRD_START_X),
            center_y=float(BIRD_START_Y),
        )
        self.bird_list.clear()
        self.bird_list.append(self.bird)

        self.floor.reset()
        self.pipe_manager.reset()
        self.difficulty.reset()

        # Nạp Trail đang trang bị
        equipped_trail_id = getattr(self.flappy_window.save_data, "equipped_trail", "none")
        trail_obj = (
            self.flappy_window.trail_manager.get_trail(equipped_trail_id)
            if hasattr(self.flappy_window, "trail_manager")
            else None
        )
        self.trail_emitter.set_trail(trail_obj)

        # Cho chim vỗ cánh cú đầu tiên và phát burst vệt bay
        self.bird.flap()
        self.trail_emitter.burst(
            self.bird.center_x,
            self.bird.center_y,
            self.bird.angle,
            self.bird.texture,
            self.bird.scale,
            self.difficulty.current_speed,
        )
        self.flappy_window.audio.play_wing()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)

        # 1. Nhảy / Vỗ cánh (Space hoặc Mũi tên lên)
        if symbol in (arcade.key.SPACE, arcade.key.UP):
            if not self.is_dead and self.bird:
                self.bird.flap()
                world_speed = self.difficulty.current_speed if hasattr(self, "difficulty") else 180.0
                self.trail_emitter.burst(
                    self.bird.center_x,
                    self.bird.center_y,
                    self.bird.angle,
                    self.bird.texture,
                    self.bird.scale,
                    world_speed,
                )
                self.flappy_window.audio.play_wing()

        # 2. Phím tắt Debug Mode (DX-2)
        elif symbol == arcade.key.F1:
            # F1: +10 Coins để test
            self.flappy_window.save_data.coins += 10
            self.flappy_window.save_data.total_coins_collected += 10
            self.flappy_window.save_progress()
            self.coins_text.text = f"COINS: {self.flappy_window.save_data.coins}"
        elif symbol == arcade.key.F2:
            # F2: Bật/tắt vẽ Hitbox đỏ
            self.flappy_window.debug_hitbox = not self.flappy_window.debug_hitbox
        elif symbol == arcade.key.F3:
            # F3: +10 Score để test độ khó và kỷ lục
            self.score += 10
            self.coins_earned += 2
            self.flappy_window.save_data.coins += 2
            self.flappy_window.save_data.total_coins_collected += 2
            self.score_text.text = f"{self.score}"
            self.coins_text.text = f"COINS: {self.flappy_window.save_data.coins}"
        elif symbol == arcade.key.F4:
            # F4: Bật/tắt God Mode
            self.flappy_window.god_mode = not self.flappy_window.god_mode


    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            if not self.is_dead and self.bird:
                self.bird.flap()
                world_speed = self.difficulty.current_speed if hasattr(self, "difficulty") else 180.0
                self.trail_emitter.burst(
                    self.bird.center_x,
                    self.bird.center_y,
                    self.bird.angle,
                    self.bird.texture,
                    self.bird.scale,
                    world_speed,
                )
                self.flappy_window.audio.play_wing()

    def on_update(self, delta_time: float) -> None:
        dt = min(0.05, delta_time)
        self.accumulator += dt

        # Fixed timestep accumulator (Hardening P1)
        while self.accumulator >= FIXED_DT:
            self.physics_tick(FIXED_DT)
            self.accumulator -= FIXED_DT

    def physics_tick(self, dt: float) -> None:
        if not self.bird:
            return

        if not self.is_dead:
            # Cập nhật độ khó qua Lerp
            self.difficulty.update(dt, self.score)
            world_speed = self.difficulty.current_speed
            pipe_gap = self.difficulty.current_gap

            # Cập nhật chim
            self.bird.update_physics(dt)

            # Cập nhật vệt bay
            self.trail_emitter.update(
                dt,
                world_speed,
                self.bird.center_x,
                self.bird.center_y,
                self.bird.angle,
                self.bird.texture,
                self.bird.scale,
            )

            # Cập nhật sàn và ống
            self.floor.update_scroll(dt, world_speed)
            if self.pipe_manager.can_spawn():
                self.pipe_manager.spawn(pipe_gap)
            self.pipe_manager.update(dt, world_speed)

            # Tính điểm khi bay qua ống
            pts = self.pipe_manager.check_score(self.bird.center_x)
            if pts > 0:
                old_score = self.score
                self.score += pts
                self.score_display.set_score(self.score)
                self.score_text.text = f"{self.score}"
                self.flappy_window.audio.play_point()
                # Cứ 5 điểm nhận 1 coin (tính theo mốc vượt qua để không sót khi pts > 1)
                new_coins = (self.score // SCORE_PER_COIN) - (old_score // SCORE_PER_COIN)
                if new_coins > 0:
                    self.coins_earned += new_coins
                    self.flappy_window.save_data.coins += new_coins
                    self.flappy_window.save_data.total_coins_collected += new_coins
                    self.coins_text.text = f"COINS: {self.flappy_window.save_data.coins}"

            # Kiểm tra trần nhà
            if self.bird.top >= SCREEN_HEIGHT:
                self.bird.top = SCREEN_HEIGHT
                self.bird.velocity_y = min(0.0, self.bird.velocity_y)

            # Kiểm tra va chạm (Native Arcade check)
            if not self.flappy_window.god_mode:
                # 1. Va chạm sàn
                if arcade.check_for_collision(self.bird, self.floor) or self.bird.bottom <= FLOOR_HEIGHT:
                    self.die(crash_entity="floor")
                # 2. Va chạm ống
                elif arcade.check_for_collision_with_list(self.bird, self.pipe_manager.sprite_list):
                    self.die(crash_entity="pipe")

        else:
            # Khi đã chết, chim tiếp tục rơi cắm đầu xuống đất trước khi hiện bảng Game Over
            self.bird.update_physics(dt)
            self.trail_emitter.update(
                dt,
                0.0,
                self.bird.center_x,
                self.bird.center_y,
                self.bird.angle,
                None,
                self.bird.scale,
            )
            if self.bird.bottom <= FLOOR_HEIGHT:
                self.bird.bottom = FLOOR_HEIGHT
                self.trigger_game_over()

    def die(self, crash_entity: str) -> None:
        self.is_dead = True
        self.flappy_window.audio.play_hit()
        if crash_entity == "pipe":
            self.flappy_window.audio.play_die()

        # Lưu High Score nếu phá kỷ lục
        if self.score > self.flappy_window.save_data.high_score:
            self.flappy_window.save_data.high_score = self.score

        # Tự động kiểm tra và mở khóa thành tựu skin & trail trước khi lưu
        self.flappy_window.skin_manager.check_achievements(self.flappy_window.save_data)
        if hasattr(self.flappy_window, "trail_manager"):
            self.flappy_window.trail_manager.check_achievements(self.flappy_window.save_data)

        # Lưu toàn bộ tiến trình (coin, highscore, unlocked_skins, unlocked_trails) ngay khi chết
        self.flappy_window.save_progress()

    def trigger_game_over(self) -> None:
        """Chuyển sang màn hình GameOverView."""
        from .game_over_view import GameOverView

        view = GameOverView(score=self.score, coins_earned=self.coins_earned)
        self.window.show_view(view)

    def on_draw(self) -> None:
        super().on_draw()

        # 1. Vẽ nền (SpriteList)
        self.bg_list.draw()

        # 2. Vẽ ống nước (SpriteList)
        self.pipe_manager.sprite_list.draw()

        # 3. Vẽ vệt bay (TrailEmitter)
        self.trail_emitter.draw()

        # 4. Vẽ sàn (SpriteList)
        self.floor_list.draw()

        # 5. Vẽ chim (SpriteList)
        self.bird_list.draw()

        # 5. Vẽ UI (Điểm số retro sprite ở giữa trên, Coin ở góc phải trên)
        self.score_display.draw()
        self.coins_text.draw()

        # 6. Vẽ Debug Overlay nếu bật F2
        if self.flappy_window.debug_hitbox and self.bird:
            # Vẽ Hitbox chim
            arcade.draw_polygon_outline(
                self.bird.hit_box.get_adjusted_points(),
                color=arcade.color.RED,
                line_width=2,
            )
            # Vẽ Hitbox ống
            for pipe in self.pipe_manager.sprite_list:
                arcade.draw_polygon_outline(
                    pipe.hit_box.get_adjusted_points(),
                    color=(255, 100, 100, 200),
                    line_width=1,
                )

        # Hiển thị cờ God Mode nếu bật
        if self.flappy_window.god_mode:
            self.god_mode_text.draw()

