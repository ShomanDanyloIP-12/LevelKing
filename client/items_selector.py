import pygame
from os import path
from pygame.image import load
from pygame.math import Vector2 as vector
from collections import defaultdict

script_directory = path.dirname(path.realpath(__file__))
graphics_directory = path.join(script_directory, 'graphics')


class Items_selector:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.fill_items_selector_data()
        self.form_data()
        self.window_size = self.display_surface.get_size()
        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720
        self.create_selector_buttons()

    def fill_items_selector_data(self):
        def menu_path(filename):
            return path.join(graphics_directory, 'menu', filename)

        items = [
            (0, None, None),
            (1, None, None),

            (2, 'terrain', 'soil.png'),
            (25, 'terrain', 'platform.png'),
            (3, 'terrain', 'water.png'),

            (4, 'treasure', 'golden_coin.png'),
            (5, 'treasure', 'silver_coin.png'),
            (6, 'treasure', 'diamond.png'),
            (33, 'treasure', 'heal_potion.png'),

            (7, 'enemy', 'spikes.png'),
            (8, 'enemy', 'pig.png'),
            (9, 'enemy', 'cannon_left.png'),
            (10, 'enemy', 'cannon_right.png'),
            (21, 'enemy', 'saw_bottom.png'),
            (22, 'enemy', 'saw_top.png'),
            (23, 'enemy', 'saw_left.png'),
            (24, 'enemy', 'saw_right.png'),
            (32, 'enemy', 'mace.png'),

            (11, 'palms fg', 'palm_small_fg.png'),
            (12, 'palms fg', 'palm_large_fg.png'),
            (13, 'palms fg', 'palm_left_fg.png'),
            (14, 'palms fg', 'palm_right_fg.png'),
            (19, 'bricks fg', 'bricks_fg.png'),

            (15, 'palms bg', 'palm_small_bg.png'),
            (16, 'palms bg', 'palm_large_bg.png'),
            (17, 'palms bg', 'palm_left_bg.png'),
            (18, 'palms bg', 'palm_right_bg.png'),
            (20, 'bricks bg', 'bricks_bg.png'),

            (26, 'info', 'info.png'),
            (27, 'info', 'finish_info.png'),
            (28, 'info', 'sign_bottom.png'),
            (29, 'info', 'sign_top.png'),
            (30, 'info', 'sign_left.png'),
            (31, 'info', 'sign_right.png'),
        ]

        self.items_selector_data = {
            idx: {
                'type': item_type,
                'preview': menu_path(preview) if preview else None
            } for idx, item_type, preview in items
        }

    def form_data(self):
        grouped = defaultdict(list)
        for key, data in self.items_selector_data.items():
            type_ = data.get('type')
            if type_ is not None:
                grouped[type_].append((key, load(data['preview'])))
        self.menu_surfs = dict(grouped)

    def create_selector_buttons(self):
        def sx(value): return int(value * self.multiplayer_x)
        def sy(value): return int(value * self.multiplayer_y)

        mm_size, mm_margin = sx(45), sx(6)
        mm_topleft = (self.window_size[0] - mm_size - mm_margin, mm_margin)

        self.mm_rect = pygame.Rect(mm_topleft, (mm_size, mm_size))
        self.image = load(path.join(script_directory, 'graphics', 'menus', 'main_menu_button.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (mm_size, mm_size))

        sv_topleft = vector(mm_topleft) - (mm_size + mm_margin, 0)
        self.sv_rect = pygame.Rect(sv_topleft, (mm_size, mm_size))
        self.sv_image = load(path.join(script_directory, 'graphics', 'menus', 'save_button.png')).convert_alpha()
        self.sv_image = pygame.transform.scale(self.sv_image, (mm_size, mm_size))

        panel_size = (270, 180)
        margin = 6
        panel_topleft = (self.window_size[0] - panel_size[0] - margin, self.window_size[1] - panel_size[1] - margin)
        self.rect = pygame.Rect(panel_topleft, panel_size)

        button_size = (self.rect.width / 3, self.rect.height / 2)
        button_margin = 5

        def button_rect(col, row):
            rect = pygame.Rect(self.rect.topleft, button_size)
            rect = rect.move(col * button_size[0], row * button_size[1])
            return rect.inflate(-button_margin, -button_margin)

        self.items_selector = pygame.sprite.Group()
        button_defs = [
            (button_rect(0, 0), 'terrain'),
            (button_rect(1, 0), 'treasure'),
            (button_rect(1, 1), 'enemy'),
            (button_rect(0, 1), 'palms fg', 'palms bg'),
            (button_rect(2, 0), 'bricks fg', 'bricks bg'),
            (button_rect(2, 1), 'info'),
        ]

        for rect, main_key, *alt_key in button_defs:
            main_items = self.menu_surfs[main_key]
            alt_items = self.menu_surfs[alt_key[0]] if alt_key else None
            Items_selector_button(rect, self.items_selector, main_items, alt_items, button_type=main_key)

    def selected_illumination(self, index):
        tile_type = self.items_selector_data[index].get('type')
        for button in self.items_selector:
            if button.button_type == tile_type or button.button_type == 'palms fg' and tile_type == 'palms bg' \
                    or button.button_type == 'bricks fg' and tile_type == 'bricks bg':
                pygame.draw.rect(self.display_surface, '#f5f1de', button.rect.inflate(4, 4), 5, 4)
                break

    def on_click(self, mouse_pos, mouse_button):
        clicked_sprite = next((sprite for sprite in self.items_selector if sprite.rect.collidepoint(mouse_pos)), None)
        if clicked_sprite:
            if mouse_button[1]:
                if clicked_sprite.items_alt:
                    clicked_sprite.main_active = not clicked_sprite.main_active
            if mouse_button[2]:
                clicked_sprite.toggle()
            return clicked_sprite.get_item_id()
        if self.mm_rect.collidepoint(mouse_pos) and mouse_button[0]:
            pass



    def render(self, index):
        self.items_selector.update()
        self.items_selector.draw(self.display_surface)
        self.display_surface.blit(self.image, self.mm_rect.topleft)
        self.display_surface.blit(self.sv_image, self.sv_rect.topleft)
        self.selected_illumination(index)


class Items_selector_button(pygame.sprite.Sprite):
    def __init__(self, rect, group, items, items_alt=None, button_type=None):
        super().__init__(group)
        self.image = pygame.Surface(rect.size)
        self.rect = rect

        self.items_main = items
        self.items_alt = items_alt or []
        self.index = 0
        self.main_active = True

        self.button_type = button_type

    def _current_items(self):
        return self.items_main if self.main_active else self.items_alt

    def get_item_id(self):
        current = self._current_items()
        if current:
            return current[self.index][0]
        return None

    def update(self):
        self.image.fill('#33323d')
        current = self._current_items()
        if current:
            surf = current[self.index][1]
            rect = surf.get_rect(center=self.image.get_rect().center)
            self.image.blit(surf, rect)

    def toggle(self):
        current = self._current_items()
        if current:
            self.index = (self.index + 1) % len(current)
