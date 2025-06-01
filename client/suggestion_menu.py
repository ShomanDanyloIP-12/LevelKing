import pygame, sys
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
import pickle
from os import path

from f_read import *

script_directory = path.dirname(path.realpath(__file__))


class Suggestion_menu:
    def __init__(self, switch, apply_changes, deny_changes,get_suggestion_grid):
        self.display_surface = pygame.display.get_surface()
        self.image_background = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'background.png')).convert_alpha()
        window_size = self.display_surface.get_size()
        self.image_background = pygame.transform.scale(self.image_background, window_size)
        self.switch = switch
        self.get_suggestion_grid = get_suggestion_grid
        self.apply_changes = apply_changes
        self.deny_changes = deny_changes
        self.buttons = Buttons_snm()
        self.switch_locker = True
        self.labels = Label('', "")

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.menu_click(event)

    def run(self, dt):
        self.event_loop()
        self.display_surface.blit(self.image_background, (0, 0))
        self.buttons.display()
        self.labels.draw()





    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.b_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'suggestion_menu', 'to': 'suggestions_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.apply_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.apply_changes()
            self.switch({'from': 'suggestion_menu', 'to': 'suggestions_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.decline_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.deny_changes()
            self.switch({'from': 'suggestion_menu', 'to': 'suggestions_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.paly_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.deny_changes()
            self.switch({'from':  'suggestion_menu', 'to': 'level'}, self.get_suggestion_grid())



class Label:
    def __init__(self, level_name, description):
        self.display_surface = pygame.display.get_surface()
        self.window_size = self.display_surface.get_size()
        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720

        self.level_name = level_name
        self.description = description
        self.color_bg = pygame.Color('#c86259')
        self.color_border = pygame.Color('#33323d')
        self.font = pygame.font.Font(path.join(script_directory, 'graphics', 'ui', 'ARCADEPI.ttf'),
                                     int(18 * self.multiplayer_x))

        # wrapped lines
        def sx(value):
            return int(value * self.multiplayer_x)
        def sy(value):
            return int(value * self.multiplayer_y)

        b_size = sx(45)
        margin = sx(25)
        topleft = (margin, margin + b_size)
        self.description_rect = pygame.Rect(topleft[0] + sx(250), topleft[1] + sy(145), sx(6) + sx(360), sy(210))
        self.wrapped_lines = self.wrap_text(self.description, self.description_rect.width)
        self.level_rect = pygame.Rect(topleft[0] + sx(250), topleft[1] + sy(80), sx(6) + sx(360), sy(30))


    def wrap_text(self, description, max_width):
        lines = []
        current_line = ''
        for char in description:
            test_line = current_line + char
            width, _ = self.font.size(test_line)
            if width <= max_width - 10:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        return lines

    def set_text(self, new_text):
        self.description = new_text
        self.wrapped_lines = self.wrap_text(self.description, self.description_rect.width)

    def draw(self):
        pygame.draw.rect(self.display_surface, self.color_bg, self.description_rect)
        pygame.draw.rect(self.display_surface, self.color_border, self.description_rect, 5)

        pygame.draw.rect(self.display_surface, self.color_bg, self.level_rect)
        pygame.draw.rect(self.display_surface, self.color_border, self.level_rect, 5)
        self.display_surface.blit(self.font.render(self.level_name, True, self.color_border), (self.level_rect.x + 5, self.level_rect.y + 5))


        line_height = self.font.get_height()
        for i, line in enumerate(self.wrapped_lines):
            line_surface = self.font.render(line, True, self.color_border)
            self.display_surface.blit(line_surface, (self.description_rect.x + 5, self.description_rect.y + 5 + i * line_height))

    def update_info(self, suggestion):
        self.description = suggestion['comment']
        self.wrapped_lines = self.wrap_text(self.description, self.description_rect.width)
        print(self.description)
        self.level_name = suggestion['level_title']
        self.display_surface.blit(self.font.render(self.level_name, True, self.color_border),
                                  (self.level_rect.x + 5, self.level_rect.y + 5))
        line_height = self.font.get_height()
        for i, line in enumerate(self.wrapped_lines):
            line_surface = self.font.render(line, True, self.color_border)
            self.display_surface.blit(line_surface,
                                      (self.description_rect.x + 5, self.description_rect.y + 5 + i * line_height))


class Buttons_snm:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.window_size = self.display_surface.get_size()
        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720
        self.font = pygame.font.Font(path.join(script_directory, 'graphics', 'ui', 'ARCADEPI.ttf'),
                                     int(18 * self.multiplayer_x))
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

        # menu area

        margin = sx(25)
        width = self.window_size[0] - (margin * 2)
        height = self.window_size[1] - (margin * 2) - b_size
        topleft = (margin, margin + b_size)
        self.local_level_image = load(
            path.join(script_directory, 'graphics', 'menus', 'main_menu', 'buttons_back.png')).convert_alpha()
        self.local_level_image = pygame.transform.scale(self.local_level_image, (width, height))
        self.local_level_rect = pygame.Rect(topleft, (width, height))

        # labels area

        self.level_label_offset = topleft[0] + sx(100), topleft[1] + sy(85), sx(6) + sx(360) / 2, sy(30)
        self.description_label_offset = topleft[0] + sx(100), topleft[1] + sy(150), sx(6) + sx(360) / 2, sy(30)

        # button areas

        self.image_play_button = load(
            path.join(script_directory, 'graphics', 'menus', 'level_buttons', 'play_button.png')).convert_alpha()
        self.image_play_button = pygame.transform.scale(self.image_play_button, (sx(180), sy(70)))
        self.paly_button_rect = pygame.Rect((topleft[0] + sx(250), topleft[1] + sy(500)), (sx(180), sy(70)))
        self.image_apply_button = load(
            path.join(script_directory, 'graphics', 'menus', 'level_buttons',
                      'apply_button.png')).convert_alpha()
        self.image_apply_button = pygame.transform.scale(self.image_apply_button, (sx(180), sy(70)))
        self.apply_button_rect = pygame.Rect(
            (topleft[0] + sx(436), topleft[1] + sy(500)),
            (sx(180), sy(70)))
        self.image_decline_button = load(
            path.join(script_directory, 'graphics', 'menus', 'level_buttons',
                      'decline_button.png')).convert_alpha()
        self.image_decline_button = pygame.transform.scale(self.image_decline_button, (sx(180), sy(70)))
        self.decline_button_rect = pygame.Rect(
            (topleft[0] + sx(436), topleft[1] + sy(424)),
            (sx(180), sy(70)))

    def display(self):
        self.display_surface.blit(self.image, self.b_rect.topleft)
        self.display_surface.blit(self.local_level_image, self.local_level_rect.topleft)
        self.display_surface.blit(self.font.render('Level name:', True, '#33323d'), self.level_label_offset)
        self.display_surface.blit(self.font.render('Suggestion:', True, '#33323d'), self.description_label_offset)
        self.display_surface.blit(self.image_play_button, self.paly_button_rect.topleft)
        self.display_surface.blit(self.image_apply_button, self.apply_button_rect.topleft)
        self.display_surface.blit(self.image_decline_button, self.decline_button_rect.topleft)