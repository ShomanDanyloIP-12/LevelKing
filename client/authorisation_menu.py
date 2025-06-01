import pygame, sys
from os import path
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
from pygame.math import Vector2 as vector


script_directory = path.dirname(path.realpath(__file__))

class Authorisation_menu:
    def __init__(self, switch, login, log_user):
        self.display_surface = pygame.display.get_surface()
        self.image_background = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'background.png')).convert_alpha()
        window_size = self.display_surface.get_size()
        self.image_background = pygame.transform.scale(self.image_background, window_size)
        self.switch = switch
        self.login = login
        self.log_user = log_user
        self.buttons = Buttons_am()
        self.input_fields = InputField()
        self.switch_locker = True
        self.image_tittle = load(path.join(script_directory, 'graphics', 'menus', 'authorisation_menu', 'tittle.png')).convert_alpha()
        m = window_size[0] / 1280
        self.image_tittle = pygame.transform.scale(self.image_tittle, (540 * m, 180 * m))
        self.tittle = pygame.Rect((window_size[0] / 2 - 540 * m / 2, 80), (540 * m, 180 * m))

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
        self.display_surface.blit(self.image_tittle, self.tittle)


    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.mm_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'authorisation_menu', 'to': 'main_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.sign_up_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'authorisation_menu', 'to': 'authorisation_s_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.log_in_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            if self.login(self.input_fields.get_login(), self.input_fields.get_password()):
                self.switch_locker = False
                self.log_user()
                self.switch({'from': 'authorisation_menu', 'to': 'server_menu'})
            else:
                self.input_fields.login_text = 'Invalid 401'
                self.input_fields.login_txt_surface = self.input_fields.font.render(self.input_fields.login_text, True, '#33323d')



class InputField:
    def __init__(self):
        max_length = 13
        self.display_surface = pygame.display.get_surface()
        self.window_size = self.display_surface.get_size()

        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720

        self.color_inactive = pygame.Color('#c86259')
        self.color_active = pygame.Color('#de9970')
        self.color_login = self.color_inactive
        self.color_password = self.color_inactive
        self.login_text = ''
        self.password_text = ''
        self.font = pygame.font.Font(path.join(script_directory, 'graphics', 'ui', 'ARCADEPI.ttf'), int(18 * self.multiplayer_x))
        self.login_txt_surface = self.font.render(self.login_text, True, self.color_login)
        self.password_txt_surface = self.font.render(self.password_text, True, self.color_password)
        self.login_active = False
        self.password_active = False
        self.max_length = max_length
        self.create_fields()

    def create_fields(self):
        def sx(value):
            return int(value * self.multiplayer_x)
        def sy(value):
            return int(value * self.multiplayer_y)

        topleft = (self.window_size[0] / 2 - sx(360) / 2, self.window_size[1] / 2 - sy(360) / 2 + 100)

        #fields
        self.login_rect = pygame.Rect(topleft[0] + sx(280) / 2, topleft[1] + sy(80), sx(6) + sx(360) / 2, sy(30))

        self.password_rect = pygame.Rect(topleft[0] + sx(280) / 2, topleft[1] + sy(120), sx(6) + sx(360) / 2, sy(30))

        self.login_label_offset = topleft[0] + sx(55) / 2, topleft[1] + sy(85), sx(6) + sx(360) / 2, sy(30)
        self.password_label_offset = topleft[0] + sx(55) / 2, topleft[1] + sy(125), sx(6) + sx(360) / 2, sy(30)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.login_rect.collidepoint(event.pos) and not self.password_active:
                self.login_active = not self.login_active
            elif self.password_rect.collidepoint(event.pos) and not self.login_active:
                self.password_active = not self.password_active
            elif self.password_rect.collidepoint(event.pos) and self.login_active:
                self.login_active = not self.login_active
                self.password_active = not self.password_active
            elif self.login_rect.collidepoint(event.pos) and self.password_active:
                self.login_active = not self.login_active
                self.password_active = not self.password_active
            else:
                self.login_active = False
                self.password_active = False
            self.color_login = self.color_active if self.login_active else self.color_inactive
            self.color_password = self.color_active if self.password_active else self.color_inactive

        elif event.type == pygame.KEYDOWN:
            if self.login_active:
                if event.key == pygame.K_BACKSPACE:
                    self.login_text = self.login_text[:-1]
                elif len(self.login_text) < self.max_length:
                    self.login_text += event.unicode
                self.login_txt_surface = self.font.render(self.login_text, True, '#33323d')
            elif self.password_active:
                if event.key == pygame.K_BACKSPACE:
                    self.password_text = self.password_text[:-1]
                elif len(self.password_text) < self.max_length:
                    self.password_text += event.unicode
                self.password_txt_surface = self.font.render('*' * len(self.password_text), True, '#33323d')


    def draw(self):
        pygame.draw.rect(self.display_surface, self.color_login, self.login_rect)
        pygame.draw.rect(self.display_surface, '#33323d', self.login_rect, 5)
        self.display_surface.blit(self.login_txt_surface, (self.login_rect.x+5, self.login_rect.y+5))
        pygame.draw.rect(self.display_surface, self.color_password, self.password_rect)
        pygame.draw.rect(self.display_surface, '#33323d', self.password_rect, 5)
        self.display_surface.blit(self.password_txt_surface, (self.password_rect.x + 5, self.password_rect.y + 5))
        self.display_surface.blit(self.font.render('Username', True, '#33323d'), self.login_label_offset)
        self.display_surface.blit(self.font.render('Password', True, '#33323d'), self.password_label_offset)

    def get_login(self):
        return self.login_text

    def get_password(self):
        return self.password_text


class Buttons_am:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.window_size = self.display_surface.get_size()
        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720
        self.font = pygame.font.Font(path.join(script_directory, 'graphics', 'ui', 'ARCADEPI.ttf'),
                                     int(18 * self.multiplayer_x))
        self.create_buttons()


    def create_buttons(self):
        script_directory = path.dirname(path.realpath(__file__))
        self.display_surface = pygame.display.get_surface()
        def sx(value):
            return int(value * self.multiplayer_x)
        def sy(value):
            return int(value * self.multiplayer_y)

        # back to main menu
        mm_size = sx(45)
        mm_margin = sx(6)
        mm_topleft = (self.window_size[0] - mm_size - mm_margin, mm_margin)
        self.mm_rect = pygame.Rect(mm_topleft, (mm_size, mm_size))
        self.image = load(path.join(script_directory, 'graphics', 'menus', 'main_menu_button.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (mm_size, mm_size))

        # menu area
        width = sx(360)
        height = sy(360)
        topleft = (self.window_size[0] / 2 - width / 2, self.window_size[1] / 2 - height / 2 + 100)
        self.menu_image = load(
            path.join(script_directory, 'graphics', 'menus', 'main_menu', 'buttons_back.png')).convert_alpha()
        self.menu_image = pygame.transform.scale(self.menu_image, (width, height))
        self.menu_rect = pygame.Rect(topleft, (width, height))

        # button areas
        self.image_log_in_button = load(
            path.join(script_directory, 'graphics', 'menus', 'authorisation_menu', 'log_in_button.png')).convert_alpha()
        self.image_log_in_button = pygame.transform.scale(self.image_log_in_button, (sx(150), sy(70)))
        self.log_in_button_rect = pygame.Rect(vector(self.menu_rect.topleft) + (sx(25), sy(265)), (self.menu_rect.width / 2 - sx(50), self.menu_rect.height / 4 - sy(20)))
        self.image_sign_up_button = load(
            path.join(script_directory, 'graphics', 'menus', 'authorisation_menu',
                      'sign_up_button.png')).convert_alpha()
        self.image_sign_up_button = pygame.transform.scale(self.image_sign_up_button, (sx(150), sy(70)))
        self.sign_up_button_rect = pygame.Rect(
            vector(self.menu_rect.topleft) + (sx(6) + self.menu_rect.width / 2, sy(265)),
            (self.menu_rect.width / 2 - sx(50), self.menu_rect.height / 4 - sy(20)))







    def display(self):
        self.display_surface.blit(self.image, self.mm_rect.topleft)
        self.display_surface.blit(self.menu_image, self.menu_rect.topleft)
        self.display_surface.blit(self.image_log_in_button, self.log_in_button_rect.topleft)
        self.display_surface.blit(self.image_sign_up_button, self.sign_up_button_rect.topleft)
