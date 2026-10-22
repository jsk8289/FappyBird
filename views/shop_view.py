"""ShopView: Màn hình Shop duyệt skin và trail, xem trước hình ảnh, mua và trang bị."""
import math
from typing import Literal, Optional

import arcade

from ..constants import ASSETS_DIR, FONT_RETRO_FAMILY, SCREEN_HEIGHT, SCREEN_WIDTH
from ..entities.floor import Floor
from ..entities.trail import TrailEmitter
from ..models.skin import DEFAULT_SKINS, Skin
from ..models.trail import DEFAULT_TRAILS, Trail
from ..services.skin_manager import SkinManager
from ..services.trail_manager import TrailManager
from .base_view import BaseView


class ShopView(BaseView):
    def __init__(self, return_view: str = "start", previous_view: Optional[BaseView] = None) -> None:
        super().__init__()
        self.return_view = return_view
        self.previous_view: Optional[BaseView] = previous_view

        # Tabs & Managers
        self.current_tab: Literal["skins", "trails"] = "skins"
        self.skin_manager = SkinManager(DEFAULT_SKINS)
        self.skins: list[Skin] = self.skin_manager.get_all_skins()
        self.trail_manager = TrailManager(DEFAULT_TRAILS)
        self.trails: list[Trail] = self.trail_manager.get_all_trails()

        self.selected_skin_index: int = 0
        self.selected_trail_index: int = 0

        # Background & Floor SpriteList
        self.background = arcade.Sprite(ASSETS_DIR / "sprites" / "background-night.png")
        self.background.center_x = SCREEN_WIDTH / 2.0
        self.background.center_y = SCREEN_HEIGHT / 2.0
        self.floor = Floor()

        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.background)
        self.bg_list.append(self.floor)

        # Cache các texture sprite của skins
        self.skin_textures: dict[str, arcade.Texture] = {}
        for s in self.skins:
            try:
                self.skin_textures[s.id] = arcade.load_texture(s.sprite_path)
            except Exception:
                self.skin_textures[s.id] = arcade.load_texture(ASSETS_DIR / "skins" / "yellow.png")

        # Sprite xem trước trong Shop
        self.preview_sprite = arcade.Sprite()
        self.preview_sprite.scale = 1.5
        self.preview_sprite.center_x = SCREEN_WIDTH / 2.0
        self.preview_sprite.center_y = 300.0

        self.preview_list = arcade.SpriteList()
        self.preview_list.append(self.preview_sprite)

        # Trail Emitter xem trước hiệu ứng vệt bay (chế độ preview: sinh hạt dày và sống lâu)
        self.trail_emitter = TrailEmitter(active_trail_id="none", is_active=False, preview_mode=True)

        self.time: float = 0.0

        # Vùng click các nút UI (unprojected mouse bounds: x_min, x_max, y_min, y_max)
        self.tab_skins_bounds = (15.0, 135.0, 452.0, 482.0)
        self.tab_trails_bounds = (153.0, 273.0, 452.0, 482.0)
        self.btn_prev = (25.0, 65.0, 275.0, 325.0)    # Nút [<]
        self.btn_next = (223.0, 263.0, 275.0, 325.0)  # Nút [>]
        self.btn_action = (SCREEN_WIDTH / 2.0 - 75.0, SCREEN_WIDTH / 2.0 + 75.0, 135.0, 175.0) # Nút Mua/Trang bị (rộng 150px)
        self.btn_back = (SCREEN_WIDTH / 2.0 - 70.0, SCREEN_WIDTH / 2.0 + 70.0, 45.0, 80.0)      # Nút Trở về (rộng 140px chứa gọn "[ ESC ] BACK")

        tab_s_cx = (self.tab_skins_bounds[0] + self.tab_skins_bounds[1]) / 2.0
        tab_t_cx = (self.tab_trails_bounds[0] + self.tab_trails_bounds[1]) / 2.0
        tab_cy = (self.tab_skins_bounds[2] + self.tab_skins_bounds[3]) / 2.0
        act_cy = (self.btn_action[2] + self.btn_action[3]) / 2.0
        b_cy = (self.btn_back[2] + self.btn_back[3]) / 2.0

        # Khởi tạo các đối tượng arcade.Text với font pixel retro
        self.tab_skins_text = arcade.Text(
            "[ 1: SKINS ]",
            tab_s_cx,
            tab_cy,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.tab_trails_text = arcade.Text(
            "[ 2: TRAILS ]",
            tab_t_cx,
            tab_cy,
            (140, 155, 175, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.title_text = self.tab_skins_text  # Backward compatibility

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
        self.prev_btn_text = arcade.Text(
            "<",
            45.0,
            300.0,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=12,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.next_btn_text = arcade.Text(
            ">",
            SCREEN_WIDTH - 45.0,
            300.0,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=12,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.item_name_text = arcade.Text(
            "",
            SCREEN_WIDTH / 2.0,
            218.0,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.skin_name_text = self.item_name_text  # Backward compatibility

        self.item_desc_text = arcade.Text(
            "",
            SCREEN_WIDTH / 2.0,
            195.0,
            (200, 215, 230, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=240,
            align="center",
        )
        self.skin_desc_text = self.item_desc_text  # Backward compatibility

        self.action_btn_text = arcade.Text(
            "",
            SCREEN_WIDTH / 2.0,
            act_cy,
            arcade.color.WHITE,
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.back_btn_text = arcade.Text(
            "[ ESC ] BACK",
            SCREEN_WIDTH / 2.0,
            b_cy,
            (210, 220, 230, 255),
            font_name=FONT_RETRO_FAMILY,
            font_size=6,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        try:
            self.update_preview_texture()
        except Exception:
            pass

    @property
    def selected_index(self) -> int:
        return self.selected_skin_index if self.current_tab == "skins" else self.selected_trail_index

    @selected_index.setter
    def selected_index(self, val: int) -> None:
        if self.current_tab == "skins":
            self.selected_skin_index = val
        else:
            self.selected_trail_index = val

    def switch_tab(self, tab: Literal["skins", "trails"]) -> None:
        """Chuyển đổi giữa 2 tab SKINS và TRAILS."""
        if tab in ("skins", "trails") and self.current_tab != tab:
            self.current_tab = tab
            self.update_preview_texture()
            self.update_ui_texts()
            if hasattr(self, "window") and self.window and hasattr(self.flappy_window, "audio"):
                self.flappy_window.audio.play_swoosh()

    def update_ui_texts(self) -> None:
        """Cập nhật nội dung các text động khi chuyển đổi hoặc mua skin/trail."""
        save_data = self.flappy_window.save_data
        self.coins_text.text = f"COINS: {save_data.coins}"

        # Cập nhật màu tab
        if self.current_tab == "skins":
            self.tab_skins_text.color = arcade.color.WHITE
            self.tab_trails_text.color = (140, 155, 175, 255)
            current_item = self.skins[self.selected_skin_index]
            is_equipped = (current_item.id == save_data.equipped_skin)
            is_unlocked = self.skin_manager.is_unlocked(current_item, save_data)
            can_buy = self.skin_manager.can_buy(current_item, save_data)
            idx = self.selected_skin_index
            total = len(self.skins)
        else:
            self.tab_skins_text.color = (140, 155, 175, 255)
            self.tab_trails_text.color = arcade.color.WHITE
            current_item = self.trails[self.selected_trail_index]
            is_equipped = (current_item.id == getattr(save_data, "equipped_trail", "none"))
            is_unlocked = self.trail_manager.is_unlocked(current_item, save_data)
            can_buy = self.trail_manager.can_buy(current_item, save_data)
            idx = self.selected_trail_index
            total = len(self.trails)

        self.item_name_text.text = f"{current_item.name} ({idx + 1}/{total})"
        self.item_desc_text.text = current_item.description

        if is_equipped:
            self.action_btn_text.text = "[ EQUIPPED ]"
            self.action_btn_text.color = arcade.color.WHITE
            self.action_btn_text.font_size = 6
        elif is_unlocked:
            self.action_btn_text.text = "[ EQUIP ]"
            self.action_btn_text.color = arcade.color.WHITE
            self.action_btn_text.font_size = 6
        else:
            if current_item.unlock_type == "coin":
                if can_buy:
                    self.action_btn_text.text = f"[ BUY {current_item.price} ]"
                    self.action_btn_text.color = arcade.color.WHITE
                    self.action_btn_text.font_size = 6
                else:
                    self.action_btn_text.text = f"NEED {current_item.price} COINS"
                    self.action_btn_text.color = (180, 180, 190, 255)
                    self.action_btn_text.font_size = 6
            else:
                self.action_btn_text.text = "[ LOCKED ]"
                self.action_btn_text.color = (230, 180, 180, 255)
                self.action_btn_text.font_size = 6

    def on_show_view(self) -> None:
        super().on_show_view()
        self.time = 0.0
        if self.window and hasattr(self.window, "skin_manager"):
            self.skin_manager = self.flappy_window.skin_manager
            self.skins = self.skin_manager.get_all_skins()
        if self.window and hasattr(self.window, "trail_manager"):
            self.trail_manager = self.flappy_window.trail_manager
            self.trails = self.trail_manager.get_all_trails()

        save_data = self.flappy_window.save_data
        equipped_skin_id = save_data.equipped_skin
        for idx, s in enumerate(self.skins):
            if s.id == equipped_skin_id:
                self.selected_skin_index = idx
                break

        equipped_trail_id = getattr(save_data, "equipped_trail", "none")
        for idx, t in enumerate(self.trails):
            if t.id == equipped_trail_id:
                self.selected_trail_index = idx
                break

        # Tự động kiểm tra thành tựu mở khóa nếu đủ điều kiện
        self.skin_manager.check_achievements(save_data)
        self.trail_manager.check_achievements(save_data)
        self.flappy_window.save_progress()
        self.update_preview_texture()
        self.update_ui_texts()

    def update_preview_texture(self) -> None:
        save_data = getattr(self.flappy_window, "save_data", None) if hasattr(self, "window") and self.window else None

        if self.current_tab == "skins":
            current_skin = self.skins[self.selected_skin_index]
            skin_id = current_skin.id
            trail_id = getattr(save_data, "equipped_trail", "none") if save_data else "none"
        else:
            skin_id = getattr(save_data, "equipped_skin", "yellow") if save_data else "yellow"
            current_trail = self.trails[self.selected_trail_index]
            trail_id = current_trail.id

        tex = self.skin_textures.get(skin_id)
        if tex:
            self.preview_sprite.texture = tex
            if getattr(tex, "height", 0) > 0:
                self.preview_sprite.scale = (24.0 / float(tex.height)) * 1.5
            else:
                self.preview_sprite.scale = 1.5

        # Cập nhật trail emitter cho khung xem trước
        self.trail_emitter.set_trail(trail_id)
        self.trail_emitter.is_active = (trail_id != "none")

    def on_update(self, delta_time: float) -> None:
        self.time += delta_time
        # Chim xem trước lắc lư sinh động
        self.preview_sprite.center_y = 300.0 + math.sin(self.time * 4.0) * 5.0
        self.preview_sprite.angle = math.sin(self.time * 4.0) * 6.0

        # Cập nhật vệt bay xem trước với vận tốc trôi nhẹ sang trái tạo dải dài
        if self.trail_emitter.is_active:
            dt = min(0.05, delta_time)
            self.trail_emitter.update(
                dt,
                bird_sprite=self.preview_sprite,
                world_speed=80.0,
            )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)

        if symbol == arcade.key.TAB:
            self.switch_tab("trails" if self.current_tab == "skins" else "skins")
        elif symbol in (arcade.key.KEY_1, arcade.key.NUM_1, arcade.key.Q):
            self.switch_tab("skins")
        elif symbol in (arcade.key.KEY_2, arcade.key.NUM_2, arcade.key.E):
            self.switch_tab("trails")
        elif symbol in (arcade.key.LEFT, arcade.key.A):
            self.prev_item()
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.next_item()
        elif symbol in (arcade.key.ENTER, arcade.key.SPACE):
            self.perform_action()
        elif symbol in (arcade.key.ESCAPE, arcade.key.B, arcade.key.BACKSPACE):
            self.go_back()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            vx, vy = self.unproject_mouse(x, y)

            # 0. Chuyển Tab
            if self.tab_skins_bounds[0] <= vx <= self.tab_skins_bounds[1] and self.tab_skins_bounds[2] <= vy <= self.tab_skins_bounds[3]:
                self.switch_tab("skins")
                return
            if self.tab_trails_bounds[0] <= vx <= self.tab_trails_bounds[1] and self.tab_trails_bounds[2] <= vy <= self.tab_trails_bounds[3]:
                self.switch_tab("trails")
                return

            # 1. Nút Prev [<]
            if self.btn_prev[0] <= vx <= self.btn_prev[1] and self.btn_prev[2] <= vy <= self.btn_prev[3]:
                self.prev_item()
                return

            # 2. Nút Next [>]
            if self.btn_next[0] <= vx <= self.btn_next[1] and self.btn_next[2] <= vy <= self.btn_next[3]:
                self.next_item()
                return

            # 3. Nút Mua / Trang bị
            if self.btn_action[0] <= vx <= self.btn_action[1] and self.btn_action[2] <= vy <= self.btn_action[3]:
                self.perform_action()
                return

            # 4. Nút Back
            if self.btn_back[0] <= vx <= self.btn_back[1] and self.btn_back[2] <= vy <= self.btn_back[3]:
                self.go_back()
                return

    def prev_item(self) -> None:
        if self.current_tab == "skins":
            self.selected_skin_index = (self.selected_skin_index - 1) % len(self.skins)
        else:
            self.selected_trail_index = (self.selected_trail_index - 1) % len(self.trails)
        self.update_preview_texture()
        self.update_ui_texts()
        self.flappy_window.audio.play_swoosh()

    def next_item(self) -> None:
        if self.current_tab == "skins":
            self.selected_skin_index = (self.selected_skin_index + 1) % len(self.skins)
        else:
            self.selected_trail_index = (self.selected_trail_index + 1) % len(self.trails)
        self.update_preview_texture()
        self.update_ui_texts()
        self.flappy_window.audio.play_swoosh()

    def prev_skin(self) -> None:
        self.prev_item()

    def next_skin(self) -> None:
        self.next_item()

    def perform_action(self) -> None:
        """Thực hiện mua hoặc trang bị skin/trail đang chọn."""
        save_data = self.flappy_window.save_data

        if self.current_tab == "skins":
            current_skin = self.skins[self.selected_skin_index]
            if current_skin.id == save_data.equipped_skin:
                return
            if self.skin_manager.is_unlocked(current_skin, save_data):
                self.skin_manager.equip_skin(current_skin.id, save_data)
                self.flappy_window.reload_skin_texture()
                self.flappy_window.save_progress()
                self.flappy_window.audio.play_point()
                self.update_ui_texts()
            elif self.skin_manager.can_buy(current_skin, save_data):
                bought = self.skin_manager.buy_skin(current_skin.id, save_data)
                if bought:
                    self.skin_manager.equip_skin(current_skin.id, save_data)
                    self.flappy_window.reload_skin_texture()
                    self.flappy_window.save_progress()
                    self.flappy_window.audio.play_point()
                    self.update_ui_texts()
        else:
            current_trail = self.trails[self.selected_trail_index]
            if current_trail.id == getattr(save_data, "equipped_trail", "none"):
                return
            if self.trail_manager.is_unlocked(current_trail, save_data):
                self.trail_manager.equip_trail(current_trail.id, save_data)
                self.flappy_window.save_progress()
                self.flappy_window.audio.play_point()
                self.update_preview_texture()
                self.update_ui_texts()
            elif self.trail_manager.can_buy(current_trail, save_data):
                bought = self.trail_manager.buy_trail(current_trail.id, save_data)
                if bought:
                    self.trail_manager.equip_trail(current_trail.id, save_data)
                    self.flappy_window.save_progress()
                    self.flappy_window.audio.play_point()
                    self.update_preview_texture()
                    self.update_ui_texts()

    def go_back(self) -> None:
        """Quay về màn hình trước."""
        if self.previous_view is not None:
            self.window.show_view(self.previous_view)
            return
        if self.return_view == "game_over":
            from .game_over_view import GameOverView

            self.window.show_view(GameOverView(score=0, coins_earned=0))
        else:
            from .start_view import StartView

            self.window.show_view(StartView())

    def on_draw(self) -> None:
        super().on_draw()

        self.bg_list.draw()

        save_data = self.flappy_window.save_data
        if self.current_tab == "skins":
            current_item = self.skins[self.selected_skin_index]
            is_equipped = (current_item.id == save_data.equipped_skin)
            is_unlocked = self.skin_manager.is_unlocked(current_item, save_data)
            can_buy = self.skin_manager.can_buy(current_item, save_data)
        else:
            current_item = self.trails[self.selected_trail_index]
            is_equipped = (current_item.id == getattr(save_data, "equipped_trail", "none"))
            is_unlocked = self.trail_manager.is_unlocked(current_item, save_data)
            can_buy = self.trail_manager.can_buy(current_item, save_data)

        # Tab Headers
        ts_l, ts_r, ts_b, ts_t = self.tab_skins_bounds
        tt_l, tt_r, tt_b, tt_t = self.tab_trails_bounds

        if self.current_tab == "skins":
            arcade.draw_lrbt_rectangle_filled(ts_l, ts_r, ts_b, ts_t, (35, 60, 95, 240))
            arcade.draw_lrbt_rectangle_outline(ts_l, ts_r, ts_b, ts_t, (100, 200, 255, 255), 2)
            arcade.draw_lrbt_rectangle_filled(tt_l, tt_r, tt_b, tt_t, (20, 25, 35, 200))
            arcade.draw_lrbt_rectangle_outline(tt_l, tt_r, tt_b, tt_t, (60, 75, 95, 200), 1)
        else:
            arcade.draw_lrbt_rectangle_filled(ts_l, ts_r, ts_b, ts_t, (20, 25, 35, 200))
            arcade.draw_lrbt_rectangle_outline(ts_l, ts_r, ts_b, ts_t, (60, 75, 95, 200), 1)
            arcade.draw_lrbt_rectangle_filled(tt_l, tt_r, tt_b, tt_t, (35, 60, 95, 240))
            arcade.draw_lrbt_rectangle_outline(tt_l, tt_r, tt_b, tt_t, (100, 200, 255, 255), 2)

        self.tab_skins_text.draw()
        self.tab_trails_text.draw()

        # Số Coin góc phải
        self.coins_text.draw()

        # Khung Xem Trước (Preview Card)
        preview_box_cx = SCREEN_WIDTH / 2.0
        preview_box_cy = 300.0
        p_w, p_h = 180.0, 130.0
        arcade.draw_lbwh_rectangle_filled(preview_box_cx - p_w / 2.0, preview_box_cy - p_h / 2.0, p_w, p_h, (20, 30, 45, 230))
        arcade.draw_lbwh_rectangle_outline(preview_box_cx - p_w / 2.0, preview_box_cy - p_h / 2.0, p_w, p_h, (80, 140, 200, 255), 2)

        # Nút chuyển trái [<] và phải [>]
        arcade.draw_lrbt_rectangle_filled(self.btn_prev[0], self.btn_prev[1], self.btn_prev[2], self.btn_prev[3], (40, 60, 90, 240))
        self.prev_btn_text.draw()

        arcade.draw_lrbt_rectangle_filled(self.btn_next[0], self.btn_next[1], self.btn_next[2], self.btn_next[3], (40, 60, 90, 240))
        self.next_btn_text.draw()

        # Vẽ Trail Emitter xem trước hiệu ứng (phía sau chim)
        if self.trail_emitter.is_active:
            self.trail_emitter.draw()

        # Vẽ Sprite chim xem trước bằng SpriteList
        self.preview_list.draw()

        # Tên Item & Vị trí
        self.item_name_text.draw()

        # Mô tả / Điều kiện
        self.item_desc_text.draw()

        # Nút Hành Động (Mua / Trang bị / Đã dùng)
        act_l, act_r, act_b, act_t = self.btn_action

        if is_equipped:
            arcade.draw_lrbt_rectangle_filled(act_l, act_r, act_b, act_t, (50, 130, 90, 240))
            arcade.draw_lrbt_rectangle_outline(act_l, act_r, act_b, act_t, (100, 220, 160, 255), 2)
        elif is_unlocked:
            arcade.draw_lrbt_rectangle_filled(act_l, act_r, act_b, act_t, (35, 100, 170, 240))
            arcade.draw_lrbt_rectangle_outline(act_l, act_r, act_b, act_t, (100, 180, 255, 255), 2)
        else:
            if current_item.unlock_type == "coin":
                if can_buy:
                    arcade.draw_lrbt_rectangle_filled(act_l, act_r, act_b, act_t, (200, 140, 20, 240))
                    arcade.draw_lrbt_rectangle_outline(act_l, act_r, act_b, act_t, (255, 215, 50, 255), 2)
                else:
                    arcade.draw_lrbt_rectangle_filled(act_l, act_r, act_b, act_t, (70, 70, 80, 240))
                    arcade.draw_lrbt_rectangle_outline(act_l, act_r, act_b, act_t, (120, 120, 130, 255), 1)
            else:
                arcade.draw_lrbt_rectangle_filled(act_l, act_r, act_b, act_t, (70, 50, 50, 240))
                arcade.draw_lrbt_rectangle_outline(act_l, act_r, act_b, act_t, (140, 80, 80, 255), 1)

        self.action_btn_text.draw()

        # Nút Trở về [ ESC / BACK ]
        b_l, b_r, b_b, b_t = self.btn_back
        arcade.draw_lrbt_rectangle_filled(b_l, b_r, b_b, b_t, (50, 55, 65, 230))
        arcade.draw_lrbt_rectangle_outline(b_l, b_r, b_b, b_t, (120, 130, 150, 255), 1)
        self.back_btn_text.draw()
