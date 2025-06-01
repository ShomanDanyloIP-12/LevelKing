import pygame, sys
from pygame.mouse import get_pos as mouse_pos
from pygame.math import Vector2 as vector
from pygame.image import load
from os import path

from f_read import *

script_directory = path.dirname(path.realpath(__file__))


class Main_menu:
    def __init__(self, switch):
        self.display_surface = pygame.display.get_surface()
        self.image_background = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'background.png')).convert_alpha()
        window_size = self.display_surface.get_size()
        self.image_background = pygame.transform.scale(self.image_background, window_size)
        self.switch = switch
        self.buttons = Buttons_mm()
        self.switch_locker = True
        self.image_tittle = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'tittle.png')).convert_alpha()
        m = window_size[0] / 1280
        self.image_tittle = pygame.transform.scale(self.image_tittle, (540 * m, 180 * m))
        self.tittle = pygame.Rect((window_size[0] / 2 - 540 * m / 2, 80), (540 * m, 180 * m))

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
        self.display_surface.blit(self.image_tittle, self.tittle)

    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.level_builder_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'main_menu', 'to': 'level_builder'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.play_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'main_menu', 'to': 'level_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.saved_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'main_menu', 'to': 'save_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.server_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'main_menu', 'to': 'authorisation_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.exit_button_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            pygame.quit()
            sys.exit()

class Buttons_mm:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.window_size = self.display_surface.get_size()
        self.multiplayer_x = self.window_size[0] / 1280
        self.multiplayer_y = self.window_size[1] / 720
        self.create_buttons()


    def create_buttons(self):
        script_directory = path.dirname(path.realpath(__file__))
        def sx(value):
            return int(value * self.multiplayer_x)
        def sy(value):
            return int(value * self.multiplayer_y)
        # menu area
        width = sx(360)
        height = sy(360)
        topleft = (self.window_size[0] / 2 - width / 2, self.window_size[1] / 2 - height / 2 + 100)
        self.image = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'buttons_back.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        # self.rect = self.image.get_rect(topleft = topleft)
        self.rect = pygame.Rect(topleft, (width, height))



        # button areas
        self.play_button_rect = pygame.Rect(vector(self.rect.topleft) + (sx(25), sy(25)), (self.rect.width - sx(50), self.rect.height / 4 - sy(20)))
        self.image_play_button = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'play_button.png')).convert_alpha()
        self.image_play_button = pygame.transform.scale(self.image_play_button, (sx(310), sy(70)))
        self.level_builder_button_rect = pygame.Rect(vector(self.rect.topleft) + (sx(25), sy(105)), (self.rect.width - sx(50), self.rect.height / 4 - sy(20)))
        self.image_level_builder_button = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'editor_button.png')).convert_alpha()
        self.image_level_builder_button = pygame.transform.scale(self.image_level_builder_button, (sx(310), sy(70)))
        self.saved_button_rect = pygame.Rect(vector(self.rect.topleft) + (sx(25), sy(185)), (self.rect.width - sx(50), self.rect.height / 4 - sy(20)))
        self.image_saved_button = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'load_button.png')).convert_alpha()
        self.image_saved_button = pygame.transform.scale(self.image_saved_button, (sx(310), sy(70)))
        self.exit_button_rect = pygame.Rect(vector(self.rect.topleft) + (sx(25), sy(265)), (self.rect.width - sx(50), self.rect.height / 4 - sy(20)))
        self.image_exit_button = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'quit_button.png')).convert_alpha()
        self.image_exit_button = pygame.transform.scale(self.image_exit_button, (sx(310), sy(70)))
        self.server_button_rect = pygame.Rect((sx(25), sy(25)), (self.window_size[0] / 8, self.window_size[0] / 8))
        self.image_server_button = load(path.join(script_directory, 'graphics', 'menus', 'main_menu', 'server_button.png')).convert_alpha()
        self.image_server_button = pygame.transform.scale(self.image_server_button, (self.window_size[0] / 8, self.window_size[0] / 8))

    def display(self):
        self.display_surface.blit(self.image, self.rect.topleft)
        self.display_surface.blit(self.image_play_button, self.play_button_rect.topleft)
        self.display_surface.blit(self.image_level_builder_button, self.level_builder_button_rect.topleft)
        self.display_surface.blit(self.image_saved_button, self.saved_button_rect.topleft)
        self.display_surface.blit(self.image_exit_button, self.exit_button_rect.topleft)
        self.display_surface.blit(self.image_server_button, self.server_button_rect.topleft)
