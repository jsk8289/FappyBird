
import math

import arcade

from ..constants import (
    ASSETS_DIR,
    BIRD_START_X,
    BIRD_START_Y,
    FONT_RETRO_FAMILY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from ..entities.bird import Bird
from ..entities.floor import Floor
from .base_view import BaseView

class StartView(BaseView):
    def __init__(self) -> None:
        super().__init__()
        self.background = arcade.Sprite(ASSETS_DIR / "sprites" / "background-day.png")
        self.background.center_x = SCREEN_WIDTH / 2.0
        self.background.center_y = SCREEN_HEIGHT / 2.0

        self.floor = Floor()
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.background)
        self.bg_list.append(self.floor)

        self.bird: Bird | None = None
        self.bird_list = arcade.SpriteList()
        self.time: float = 0.0

        #nút shop
        self.shop_button_bounds = (
            SCREEN_WIDTH / 2.0 - 70.0,
            SCREEN_WIDTH / 2.0 + 70.0,
            70.0,
            105.0,
        )
        sb_bot, sb_top = self.shop_button_bounds[2], self.shop_button_bounds[3]


        self.message_sprite = arcade.Sprite(ASSETS_DIR / "sprites" / "message.png")
        self.message_sprite.center_x = SCREEN_WIDTH / 2.0
        self.message_sprite.center_y = 310.0
        self.message_list = arcade.SpriteList()
        self.message_list.append(self.message_sprite)

        # Khởi tạo các đối tượng arcade.Text cố định
        self.title_text = arcade.Text(
            "FLAPPY BIRD",
            SCREEN_WIDTH / 2.0,
            SCREEN_HEIGHT - 120.0,
            (255, 215, 0, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=12,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.best_score_text = arcade.Text(
            "BEST: 0",
            SCREEN_WIDTH / 2.0,
            SCREEN_HEIGHT - 38.0,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
        )
        self.prompt_text = arcade.Text(
            "[ SPACE ] TO PLAY",
            SCREEN_WIDTH / 2.0,
            SCREEN_HEIGHT - 260.0,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
        )
        self.shop_btn_text = arcade.Text(
            "[ S ] SHOP",
            SCREEN_WIDTH / 2.0,
            (sb_bot + sb_top) / 2.0,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
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

    def on_show_view(self) -> None:
        super().on_show_view()
        self.time = 0.0
        self.floor.reset()


        best_score = self.flappy_window.save_data.high_score
        self.best_score_text.text = f"BEST: {best_score}"
        self.coins_text.text = f"COINS: {self.flappy_window.save_data.coins}"

        #Vị trí chim
        texture = self.flappy_window.current_skin_texture
        self.bird = Bird(
            texture=texture,
            center_x=142.0,
            center_y=259.0,
        )
        self.bird_list.clear()
        self.bird_list.append(self.bird)

    def on_update(self, delta_time: float) -> None:
        self.time += delta_time

        self.floor.update_scroll(delta_time, 80.0)


        alpha = int(180 + 75 * math.sin(self.time * 6.0))
        self.prompt_text.color = (255, 255, 255, alpha)


        if self.bird:
            self.bird.center_x = 142.0
            self.bird.center_y = 259.0 + math.sin(self.time * 5.0) * 7.0
            self.bird.angle = math.sin(self.time * 5.0) * 8.0

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)

        if symbol in (arcade.key.SPACE, arcade.key.ENTER, arcade.key.UP):
            self.start_game()
        elif symbol in (arcade.key.S, arcade.key.TAB):
            self.open_shop()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Ánh xạ tọa độ chuột về thế giới ảo (Hardening P1)
            vx, vy = self.unproject_mouse(x, y)
            sb_left, sb_right, sb_bot, sb_top = self.shop_button_bounds

            #action khi click vào shop
            if sb_left <= vx <= sb_right and sb_bot <= vy <= sb_top:
                self.open_shop()
            else:
                self.start_game()

    def start_game(self) -> None:
        from .game_view import GameView

        game_view = GameView()
        self.window.show_view(game_view)

    def open_shop(self) -> None:
        from .shop_view import ShopView

        shop_view = ShopView(return_view="start", previous_view=self)
        self.window.show_view(shop_view)

    def on_draw(self) -> None:
        super().on_draw()

        # Vẽ các Sprite bằng SpriteList
        self.bg_list.draw()
        self.message_list.draw()
        self.bird_list.draw()


        self.best_score_text.draw()


        sb_left, sb_right, sb_bot, sb_top = self.shop_button_bounds
        arcade.draw_lrbt_rectangle_filled(
            sb_left,
            sb_right,
            sb_bot,
            sb_top,
            (35, 75, 120, 230),
        )
        arcade.draw_lrbt_rectangle_outline(
            sb_left,
            sb_right,
            sb_bot,
            sb_top,
            (100, 180, 255, 255),
            2,
        )
        self.shop_btn_text.draw()

        
        self.coins_text.draw()

