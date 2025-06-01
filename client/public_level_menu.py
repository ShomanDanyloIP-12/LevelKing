import pygame, sys
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
import pickle
from os import path
from f_read import *

script_directory = path.dirname(path.realpath(__file__))


class Public_level_menu:
    def __init__(self, switch, save_own_level, delete_public_level, update_level_builder_grid):
        self.display_surface = pygame.display.get_surface()
        self.image_background = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'background.png')).convert_alpha()
        window_size = self.display_surface.get_size()
        self.image_background = pygame.transform.scale(self.image_background, window_size)
        self.switch = switch
        self.update_level_builder_grid = update_level_builder_grid
        self.from_where = 'server_menu'
        self.save_own_level = save_own_level
        self.delete_public_level = delete_public_level
        self.buttons = Buttons_plm()
        self.switch_locker = True
        self.input_fields = InputField()


    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.menu_click(event)
            self.input_fields.handle_event(event)

    def run(self, dt):
        self.event_loop()
        self.display_surface.blit(self.image_background, (0, 0))
        self.buttons.display()
        self.input_fields.draw()
        # print('1')


    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.b_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'public_level_menu', 'to': 'server_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.save_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True and self.from_where == 'level_builder':
            self.save_own_level(self.input_fields.get_level(), self.input_fields.get_description())
            self.switch_locker = False
            self.from_where = 'server_menu'
            self.switch({'from': 'public_level_menu', 'to': 'server_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.button_delete_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.delete_public_level()
            self.switch_locker = False
            self.switch({'from': 'public_level_menu', 'to': 'server_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.public_redact_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.update_level_builder_grid()
            self.from_where = 'level_builder'
            self.switch_locker = False
            self.switch({'from': 'public_level_menu', 'to': 'level_builder'})


class InputField:
    def __init__(self):
        max_length = 25
        self.display_surface = pygame.display.get_surface()
        self.window_size = self.display_surface.get_size()
        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720

        self.color_inactive = pygame.Color('#c86259')
        self.color_active = pygame.Color('#de9970')
        self.color_description = self.color_inactive
        self.color_level = self.color_inactive
        self.description_text = ''
        self.description_wrapped_lines = []
        self.level_text = ''
        self.font = pygame.font.Font(path.join(script_directory, 'graphics', 'ui', 'ARCADEPI.ttf'), int(18 * self.multiplayer_x))
        self.description_txt_surface = self.font.render(self.description_text, True, self.color_description)
        self.level_txt_surface = self.font.render(self.level_text, True, self.color_level)
        self.description_active = False
        self.level_active = False
        self.max_length = max_length
        self.create_fields()

    def create_fields(self):
        def sx(value):
            return int(value * self.multiplayer_x)
        def sy(value):
            return int(value * self.multiplayer_y)

        b_size = sx(45)
        margin = sx(25)
        topleft = (margin, margin + b_size)

        #fields
        self.level_rect = pygame.Rect(topleft[0] + sx(250), topleft[1] + sy(80), sx(6) + sx(360), sy(30))

        self.description_rect = pygame.Rect(topleft[0] + sx(250), topleft[1] + sy(145), sx(6) + sx(360), sy(210))


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.description_rect.collidepoint(event.pos) and not self.level_active:
                self.description_active = not self.description_active
            elif self.level_rect.collidepoint(event.pos) and not self.description_active:
                self.level_active = not self.level_active
            elif self.level_rect.collidepoint(event.pos) and self.description_active:
                self.description_active = not self.description_active
                self.level_active = not self.level_active
            elif self.description_rect.collidepoint(event.pos) and self.level_active:
                self.description_active = not self.description_active
                self.level_active = not self.level_active
            else:
                self.description_active = False
                self.level_active = False
            self.color_description = self.color_active if self.description_active else self.color_inactive
            self.color_level = self.color_active if self.level_active else self.color_inactive

        elif event.type == pygame.KEYDOWN:
            if self.description_active:
                if event.key == pygame.K_BACKSPACE:
                    self.description_text = self.description_text[:-1]
                elif len(self.description_text) < self.max_length * 10:
                    self.description_text += event.unicode
                self.description_txt_surface = self.font.render(self.description_text, True, '#33323d')
                self.description_wrapped_lines = self.wrap_text(self.description_text, self.description_rect.width)
            elif self.level_active:
                if event.key == pygame.K_BACKSPACE:
                    self.level_text = self.level_text[:-1]
                elif len(self.level_text) < self.max_length:
                    self.level_text += event.unicode
                self.level_txt_surface = self.font.render(self.level_text, True, '#33323d')

    def wrap_text(self, text, max_width):
        lines = []
        current_line = ''

        for char in text:
            test_line = current_line + char
            width, _ = self.font.size(test_line)
            if width <= max_width - 10:  # -10 — для внутрішнього відступу
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        return lines

    def draw(self):
        pygame.draw.rect(self.display_surface, self.color_description, self.description_rect)
        pygame.draw.rect(self.display_surface, '#33323d', self.description_rect, 5)
        line_height = self.font.get_height()
        for i, line in enumerate(self.description_wrapped_lines):
            line_surface = self.font.render(line, True, '#33323d')
            self.display_surface.blit(line_surface,
                                      (self.description_rect.x + 5, self.description_rect.y + 5 + i * line_height))
        pygame.draw.rect(self.display_surface, self.color_level, self.level_rect)
        pygame.draw.rect(self.display_surface, '#33323d', self.level_rect, 5)
        self.display_surface.blit(self.level_txt_surface, (self.level_rect.x + 5, self.level_rect.y + 5))

    def get_description(self):
        return self.description_text

    def get_level(self):
        return self.level_text

    def update_info(self, level):
        self.description_text = level['description']
        print(self.description_text)
        self.level_text = level['title']
        self.level_txt_surface = self.font.render(self.level_text, True, '#33323d')
        self.description_txt_surface = self.font.render(self.description_text, True, '#33323d')
        self.description_wrapped_lines = self.wrap_text(self.description_text, self.description_rect.width)




class Buttons_plm:
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

        self.image_redact_button = load(
            path.join(script_directory, 'graphics', 'menus', 'level_buttons', 'redact_button.png')).convert_alpha()
        self.image_redact_button = pygame.transform.scale(self.image_redact_button, (sx(180), sy(70)))
        self.public_redact_rect = pygame.Rect((topleft[0] + sx(250), topleft[1] + sy(500)), (sx(180), sy(70)))
        self.image_save_button = load(
            path.join(script_directory, 'graphics', 'menus', 'level_buttons',
                      'save_button.png')).convert_alpha()
        self.image_save_button = pygame.transform.scale(self.image_save_button, (sx(180), sy(70)))
        self.save_button_rect = pygame.Rect(
            (topleft[0] + sx(436), topleft[1] + sy(500)),
            (sx(180), sy(70)))
        self.image_delete_button = load(
            path.join(script_directory, 'graphics', 'menus', 'delete_button.png')).convert_alpha()
        self.image_delete_button = pygame.transform.scale(self.image_delete_button, (sx(45), sy(45)))
        self.button_delete_rect = pygame.Rect((topleft[0] + sx(622), topleft[1] + sy(500)), (sx(45), sy(45)))



    def display(self):
        self.display_surface.blit(self.image, self.b_rect.topleft)
        self.display_surface.blit(self.local_level_image, self.local_level_rect.topleft)
        self.display_surface.blit(self.font.render('Level name:', True, '#33323d'), self.level_label_offset)
        self.display_surface.blit(self.font.render('Description:', True, '#33323d'), self.description_label_offset)
        self.display_surface.blit(self.image_redact_button, self.public_redact_rect.topleft)
        self.display_surface.blit(self.image_save_button, self.save_button_rect.topleft)
        self.display_surface.blit(self.image_delete_button, self.button_delete_rect.topleft)
        # self.display_surface.blit(self.image_level1_button, self.level1_button_rect.topleft)