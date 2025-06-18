import pygame, sys
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
import pickle
from os import path
from pygame.math import Vector2 as vector

from f_read import *

script_directory = path.dirname(path.realpath(__file__))


class Server_menu:
    def __init__(self, switch, get_public_levels_by_author, decide_chosen_level, decide_chosen_level_local, clear_level_builder):
        self.display_surface = pygame.display.get_surface()
        self.image_background = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'background.png')).convert_alpha()
        window_size = self.display_surface.get_size()
        self.image_background = pygame.transform.scale(self.image_background, window_size)
        self.switch = switch
        self.clear_level_builder = clear_level_builder
        self.get_public_levels_by_author = get_public_levels_by_author
        self.decide_chosen_level = decide_chosen_level
        self.decide_chosen_level_local = decide_chosen_level_local
        self.buttons = Buttons_sm()
        self.switch_locker = True
        self.image_tittle_l = load(
            path.join(script_directory, 'graphics', 'menus', 'server_menu', 'tittle_l.png')).convert_alpha()
        m = window_size[0] / 1280
        l = window_size[1] / 720
        self.image_tittle_l = pygame.transform.scale(self.image_tittle_l, (290 * m, 180 * m))
        self.tittle_l = pygame.Rect((window_size[0] / 4 - 290 * m / 2, 0), (290 * m, 180 * m))
        self.image_tittle_p = load(
            path.join(script_directory, 'graphics', 'menus', 'server_menu', 'tittle_p.png')).convert_alpha()
        self.image_tittle_p = pygame.transform.scale(self.image_tittle_p, (290 * m, 180 * m))
        self.tittle_p = pygame.Rect((window_size[0] / 4 * 3 - 290 * m / 2 - 20 * m, 0), (290 * m, 180 * m))
        self.local_level_list = ScrollableList(
            rect=(75 * m, 140 * l, window_size[0] / 2 - (75 * m * 2), window_size[1] - (140 * l) - 75 * l),
            items=[],
        )
        self.public_level_list = ScrollableList(
            rect=(window_size[0] / 2 + 50 * m, 200 * l, window_size[0] / 2 - (75 * m * 2), window_size[1] - (140 * l) - 135 * l),
            items=[],
        )

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.menu_click(event)
            clicked_level_local = self.local_level_list.handle_event(event)
            clicked_level_public = self.public_level_list.handle_event(event)
            # print(clicked_level_public)
            if clicked_level_local:
                print("User clicked on:", clicked_level_local.get('title'))
                self.decide_chosen_level_local(clicked_level_local.get('title'))
                self.switch_locker = False
                self.switch({'from': 'server_menu', 'to': 'local_level_menu'})
            elif clicked_level_public:
                print("(Public) User clicked on:", clicked_level_public.get('id'))
                self.decide_chosen_level(clicked_level_public.get('id'))
                self.switch_locker = False
                self.switch({'from': 'server_menu', 'to': 'public_level_menu'})


    def run(self, dt):
        self.event_loop()
        self.display_surface.blit(self.image_background, (0, 0))
        self.buttons.display()
        self.display_surface.blit(self.image_tittle_l, self.tittle_l)
        self.display_surface.blit(self.image_tittle_p, self.tittle_p)
        self.local_level_list.draw()
        self.public_level_list.draw()





    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.b_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.clear_level_builder()
            self.switch({'from': 'server_menu', 'to': 'main_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.d_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'server_menu', 'to': 'delete_user_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.r_rect.collidepoint(
                mouse_pos()) and self.switch_locker:
            levels = self.get_public_levels_by_author()

            if isinstance(levels, list):
                self.public_level_list.update_items(levels)
            else:
                print("Помилка: список рівнів не отримано або має неправильний формат")
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.public_levels_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'server_menu', 'to': 'public_levels_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.suggestions_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'server_menu', 'to': 'suggestions_menu'})



class ScrollableList:
    def __init__(self, rect, items, item_height=40):
        self.display_surface = pygame.display.get_surface()
        self.rect = pygame.Rect(rect)
        self.window_size = self.display_surface.get_size()
        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720
        self.font = pygame.font.Font(path.join(script_directory, 'graphics', 'ui', 'ARCADEPI.ttf'), int(self.sx(20)))
        self.items = items
        self.item_height = item_height
        self.scroll_offset = 0
        self.max_scroll = max(0, len(items) * item_height - self.rect.height + item_height)
        self.bg_color = pygame.Color('#c86259')
        self.text_color = pygame.Color('#33323d')
        self.border_color = pygame.Color('#33323d')
        self.selected_index = None

    def draw(self):
        pygame.draw.rect(self.display_surface, self.bg_color, self.rect)
        pygame.draw.rect(self.display_surface, self.border_color, self.rect, 4)

        start_index = self.scroll_offset // self.item_height
        end_index = min(start_index + self.rect.height // self.item_height + 1, len(self.items))

        for i in range(start_index, end_index):
            item_y = self.rect.y + (i - start_index) * self.item_height
            item_rect = pygame.Rect(self.rect.x, item_y, self.rect.width, self.item_height)

            if item_rect.bottom > self.rect.bottom:
                break

            if i == self.selected_index:
                pygame.draw.rect(self.display_surface, pygame.Color('#de9970'), item_rect)

            title = self.items[i].get('title', 'Без назви')
            text_surf = self.font.render(title, True, self.text_color)
            self.display_surface.blit(text_surf, (item_rect.x + 10, item_rect.y + 5))

    def handle_event(self, event):
        mouse_pos_now = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(mouse_pos_now):
                self.scroll_offset -= event.y * self.item_height
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                relative_y = event.pos[1] - self.rect.y + self.scroll_offset
                index = relative_y // self.item_height
                if 0 <= index < len(self.items):
                    self.selected_index = index
                    return self.items[index]

        return None


    def sx(self, value):
        return int(value * self.multiplayer_x)

    def sy(self, value):
        return int(value * self.multiplayer_y)

    def update_items_local(self):
        self.items = self.read_button_states()
        self.scroll_offset = 0
        self.selected_index = None
        self.max_scroll = max(0, len(self.items) * self.item_height - self.rect.height)

    def read_button_states(self):
        file_path = path.join(script_directory, 'saved_levels', f'states.json')
        with open(file_path, 'rb') as file:
            saves = pickle.load(file)
            local_levels = [{'title': saves[f'name{i}']} for i in range(1, 7) if saves.get(f'state{i}', False)]
            return local_levels

    def update_items(self, new_items):
        self.items = new_items
        # print(self.items)
        self.scroll_offset = 0
        self.selected_index = None
        self.max_scroll = max(0, len(new_items) * self.item_height - self.rect.height)


class Buttons_sm:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.window_size = self.display_surface.get_size()
        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720
        self.create_buttons()


    def create_buttons(self):
        self.display_surface = pygame.display.get_surface()
        def sx(value):
            return int(value * self.multiplayer_x)
        def sy(value):
            return int(value * self.multiplayer_y)

        # back to main menu
        b_size = sx(45)
        b_margin = sx(6)
        b_topleft = (self.window_size[0] - b_size - b_margin, b_margin)
        self.b_rect = pygame.Rect(b_topleft, (b_size, b_size))
        self.image = load(path.join(script_directory, 'graphics', 'menus', 'back_button.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (b_size, b_size))

        self.d_rect = pygame.Rect((b_margin, b_margin), (b_size, b_size))
        self.d_image = load(path.join(script_directory, 'graphics', 'menus', 'server_menu', 'delete.png')).convert_alpha()
        self.d_image = pygame.transform.scale(self.d_image, (b_size, b_size))

        r_topleft = (self.window_size[0] - b_size * 2 - b_margin * 2, b_margin)
        self.r_rect = pygame.Rect(r_topleft, (b_size, b_size))
        self.r_image = load(path.join(script_directory, 'graphics', 'menus', 'reload_button.png')).convert_alpha()
        self.r_image = pygame.transform.scale(self.r_image, (b_size, b_size))


        # menu areas
        margin = sx(25)
        width = self.window_size[0] / 2 - (margin * 2)
        height = self.window_size[1] - (margin * 2) - b_size
        topleft = (margin, margin + b_size)
        self.local_levels_image = load(
            path.join(script_directory, 'graphics', 'menus', 'main_menu', 'buttons_back.png')).convert_alpha()
        self.local_levels_image = pygame.transform.scale(self.local_levels_image, (width, height))
        self.local_levels_rect = pygame.Rect(topleft, (width, height))
        self.public_levels_image = load(
            path.join(script_directory, 'graphics', 'menus', 'main_menu', 'buttons_back.png')).convert_alpha()
        self.public_levels_image = pygame.transform.scale(self.public_levels_image, (width, height))
        self.public_levels_rect = pygame.Rect((topleft[0] + self.window_size[0] / 2 - margin, topleft[1]), (width, height))


        # button areas
        self.image_public_levels_button = load(
            path.join(script_directory, 'graphics', 'menus', 'server_menu', 'public_levels_button.png')).convert_alpha()
        self.image_public_levels_button = pygame.transform.scale(self.image_public_levels_button, (sx(250), sy(70)))
        self.public_levels_button_rect = pygame.Rect((self.public_levels_rect.topleft[0] + sx(35), self.public_levels_rect.topleft[1] + sy(50)),
                                              (sx(250), sy(70)))
        self.image_suggestions_button = load(
            path.join(script_directory, 'graphics', 'menus', 'server_menu',
                      'suggestions_button.png')).convert_alpha()
        self.image_suggestions_button = pygame.transform.scale(self.image_suggestions_button, vector(sx(250), sy(70)))
        self.suggestions_button_rect = pygame.Rect((self.public_levels_rect.topleft[0] + sx(300), self.public_levels_rect.topleft[1] + sy(50)),
                                              (sx(250), sy(70)))


    def display(self):
        self.display_surface.blit(self.image, self.b_rect.topleft)
        self.display_surface.blit(self.r_image, self.r_rect.topleft)
        self.display_surface.blit(self.d_image, self.d_rect.topleft)
        self.display_surface.blit(self.local_levels_image, self.local_levels_rect.topleft)
        self.display_surface.blit(self.public_levels_image, self.public_levels_rect.topleft)
        self.display_surface.blit(self.image_public_levels_button, self.public_levels_button_rect.topleft)
        self.display_surface.blit(self.image_suggestions_button, self.suggestions_button_rect.topleft)
        # self.display_surface.blit(self.image_level1_button, self.level1_button_rect.topleft)