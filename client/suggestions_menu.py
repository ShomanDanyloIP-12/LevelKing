import pygame, sys
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
import pickle
from os import path
from f_read import *

script_directory = path.dirname(path.realpath(__file__))


class Suggestions_menu:
    def __init__(self, switch, get_suggestions, decide_chosen_suggestion):
        self.display_surface = pygame.display.get_surface()
        self.image_background = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'background.png')).convert_alpha()
        window_size = self.display_surface.get_size()
        self.image_background = pygame.transform.scale(self.image_background, window_size)
        self.switch = switch
        self.get_suggestions = get_suggestions
        self.decide_chosen_suggestion = decide_chosen_suggestion
        self.buttons = Buttons_snsm()
        self.switch_locker = True
        self.image_tittle = load(
            path.join(script_directory, 'graphics', 'menus', 'suggestions_menu', 'tittle.png')).convert_alpha()
        m = window_size[0] / 1280
        l = window_size[1] / 720
        self.image_tittle = pygame.transform.scale(self.image_tittle, (540 * m, 180 * m))
        self.tittle = pygame.Rect((window_size[0] / 2 - 540 * m / 2, 0), (540 * m, 180 * m))
        self.suggestions_list = ScrollableList(
            rect=(120 * m, 140 * l, window_size[0] - (120 * m * 2), window_size[1] - (140 * l) - 75 * l),
            items=[],
        )

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.menu_click(event)
            clicked_suggestion = self.suggestions_list.handle_event(event)
            if clicked_suggestion:
                print("User clicked on:", clicked_suggestion)
                self.decide_chosen_suggestion(clicked_suggestion.get('id'))
                self.switch_locker = False
                self.switch({'from': 'suggestions_menu', 'to': 'suggestion_menu'})

    def run(self, dt):
        self.event_loop()
        self.display_surface.blit(self.image_background, (0, 0))
        self.buttons.display()
        self.display_surface.blit(self.image_tittle, self.tittle)
        self.suggestions_list.draw()


    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.b_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'suggestions_menu', 'to': 'server_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.r_rect.collidepoint(
                mouse_pos()) and self.switch_locker:
            suggestions = self.get_suggestions()

            if isinstance(suggestions, list):
                self.suggestions_list.update_items(suggestions)
            else:
                print("Помилка: список пропозицій не отримано або має неправильний формат")



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

            title = self.items[i].get('level_title', 'Без назви')
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

    def update_items(self, new_items):
        self.items = new_items
        self.scroll_offset = 0
        self.selected_index = None
        self.max_scroll = max(0, len(new_items) * self.item_height - self.rect.height)


class Buttons_snsm:
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

        r_topleft = (self.window_size[0] - b_size * 2 - b_margin * 2, b_margin)
        self.r_rect = pygame.Rect(r_topleft, (b_size, b_size))
        self.r_image = load(path.join(script_directory, 'graphics', 'menus', 'reload_button.png')).convert_alpha()
        self.r_image = pygame.transform.scale(self.r_image, (b_size, b_size))


        # menu area
        margin = sx(25)
        width = self.window_size[0] - (margin * 2)
        height = self.window_size[1] - (margin * 2) - b_size
        topleft = (margin, margin + b_size)
        self.suggestions_image = load(
            path.join(script_directory, 'graphics', 'menus', 'main_menu', 'buttons_back.png')).convert_alpha()
        self.suggestions_image = pygame.transform.scale(self.suggestions_image, (width, height))
        self.suggestions_rect = pygame.Rect(topleft, (width, height))


        # button areas
        # size = sx(240)
        # self.level1_button_rect = pygame.Rect((sx(64), sy(320)), (size, size))
        # self.image_level1_button = load(path.join(script_directory, 'graphics', 'menus', 'level_menu', 'level1_button.png')).convert_alpha()
        # self.image_level1_button = pygame.transform.scale(self.image_level1_button, (size, size))



    def display(self):
        self.display_surface.blit(self.image, self.b_rect.topleft)
        self.display_surface.blit(self.r_image, self.r_rect.topleft)
        self.display_surface.blit(self.suggestions_image, self.suggestions_rect.topleft)
        # self.display_surface.blit(self.image_level1_button, self.level1_button_rect.topleft)