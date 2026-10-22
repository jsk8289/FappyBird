
import arcade

from ..constants import (
    ASSETS_DIR,
    FONT_RETRO_FAMILY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from ..entities.floor import Floor
from .base_view import BaseVi
class GameOverView(BaseView):
    def __init__(self, score: int, coins_earned: int) -> None:
        super().__init__()
        self.score = score
        self.coins_earned = coins_earned

        self.background = arcade.Sprite(ASSETS_DIR / "sprites" / "background-day.png")
        self.background.center_x = SCREEN_WIDTH / 2.0
        self.background.center_y = SCREEN_HEIGHT / 2.0
        self.floor = Floor()

        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.background)
        self.bg_list.append(self.floor)

        #vùng bấm nút replay
        self.btn_replay = (
            SCREEN_WIDTH / 2.0 - 80.0,  # left
            SCREEN_WIDTH / 2.0 + 80.0,  # right
            135.0,                       # bottom
            170.0,                       # top
        )

        #vùng bấm nút shop
        self.btn_shop = (
            SCREEN_WIDTH / 2.0 - 80.0,
            SCREEN_WIDTH / 2.0 + 80.0,
            85.0,
            120.0,
        )

        card_cx = SCREEN_WIDTH / 2.0
        card_cy = SCREEN_HEIGHT - 210.0
        r_bot, r_top = self.btn_replay[2], self.btn_replay[3]
        s_bot, s_top = self.btn_shop[2], self.btn_shop[3]

        # Sprite tiêu đề "GAME OVER" retro
        self.gameover_sprite = arcade.Sprite(ASSETS_DIR / "sprites" / "gameover.png")
        self.gameover_sprite.center_x = SCREEN_WIDTH / 2.0
        self.gameover_sprite.center_y = SCREEN_HEIGHT - 110.0
        self.gameover_list = arcade.SpriteList()
        self.gameover_list.append(self.gameover_sprite)

        # Khởi tạo các đối tượng arcade.Text
        self.game_over_text = arcade.Text(
            "GAME OVER",
            SCREEN_WIDTH / 2.0,
            SCREEN_HEIGHT - 100.0,
            (230, 45, 45, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=12,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.score_text = arcade.Text(
            f"SCORE: {self.score}",
            card_cx,
            card_cy + 35.0,
            (50, 40, 20, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.best_text = arcade.Text(
            "BEST: 0",
            card_cx,
            card_cy + 12.0,
            (180, 60, 20, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.coins_earned_text = arcade.Text(
            f"+{self.coins_earned} COINS EARNED",
            card_cx,
            card_cy - 12.0,
            (140, 110, 0, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
        )
        self.total_coins_text = arcade.Text(
            "TOTAL COINS: 0",
            card_cx,
            card_cy - 35.0,
            (70, 60, 50, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
        )
        self.replay_btn_text = arcade.Text(
            "[ SPACE ] REPLAY",
            card_cx,
            (r_bot + r_top) / 2.0,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
        )
        self.shop_btn_text = arcade.Text(
            "[ S ] SHOP",
            card_cx,
            (s_bot + s_top) / 2.0,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
        )

    def on_show_view(self) -> None:
        super().on_show_view()
        best_score = self.flappy_window.save_data.high_score
        self.best_text.text = f"BEST: {best_score}"
        self.coins_earned_text.text = f"+{self.coins_earned} COINS EARNED"
        self.total_coins_text.text = f"TOTAL COINS: {self.flappy_window.save_data.coins}"

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)

        if symbol in (arcade.key.SPACE, arcade.key.ENTER, arcade.key.R):
            self.restart_game()
        elif symbol in (arcade.key.S, arcade.key.TAB):
            self.open_shop()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            vx, vy = self.unproject_mouse(x, y)

            #Nút Replay
            r_left, r_right, r_bot, r_top = self.btn_replay
            if r_left <= vx <= r_right and r_bot <= vy <= r_top:
                self.restart_game()
                return

            #Nút Shop
            s_left, s_right, s_bot, s_top = self.btn_shop
            if s_left <= vx <= s_right and s_bot <= vy <= s_top:
                self.open_shop()
                return

            #click ra ngoài để chơi lại
            self.restart_game()

    def restart_game(self) -> None:
        from .game_view import GameView

        self.window.show_view(GameView())

    def open_shop(self) -> None:
        from .shop_view import ShopView

        self.window.show_view(ShopView(return_view="game_over", previous_view=self))

    def on_draw(self) -> None:
        super().on_draw()

        self.bg_list.draw()

        #Tiêu đề "GAME OVER" bằng sprite retro
        self.gameover_list.draw()

        #Bảng điểm
        card_cx = SCREEN_WIDTH / 2.0
        card_cy = SCREEN_HEIGHT - 210.0
        card_w = 210.0
        card_h = 135.0

        arcade.draw_lbwh_rectangle_filled(card_cx - card_w / 2.0, card_cy - card_h / 2.0, card_w, card_h, (222, 216, 149, 250))
        arcade.draw_lbwh_rectangle_outline(card_cx - card_w / 2.0, card_cy - card_h / 2.0, card_w, card_h, (180, 150, 70, 255), 3)

        #Chi tiết điểm số
        self.score_text.draw()
        self.best_text.draw()
        self.coins_earned_text.draw()
        self.total_coins_text.draw()

        #bấm phím space để chơi lại
        r_left, r_right, r_bot, r_top = self.btn_replay
        arcade.draw_lrbt_rectangle_filled(r_left, r_right, r_bot, r_top, (40, 160, 70, 240))
        arcade.draw_lrbt_rectangle_outline(r_left, r_right, r_bot, r_top, (100, 220, 120, 255), 2)
        self.replay_btn_text.draw()

        #bấm phím s để mở shop
        s_left, s_right, s_bot, s_top = self.btn_shop
        arcade.draw_lrbt_rectangle_filled(s_left, s_right, s_bot, s_top, (35, 75, 120, 240))
        arcade.draw_lrbt_rectangle_outline(s_left, s_right, s_bot, s_top, (100, 180, 255, 255), 2)
        self.shop_btn_text.draw()

