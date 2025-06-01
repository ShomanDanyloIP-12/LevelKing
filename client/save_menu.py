import pygame, sys
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
from pygame.mouse import get_pressed as mouse_buttons
from datetime import datetime
from os import path
import pickle
import os

script_directory = path.dirname(path.realpath(__file__))


class Save_menu:
    def __init__(self, switch, save_file):
        self.display_surface = pygame.display.get_surface()
        self.image_background = load(path.join(script_directory, 'graphics', 'menus', 'save_menu', 'background.png')).convert_alpha()
        window_size = self.display_surface.get_size()
        self.image_background = pygame.transform.scale(self.image_background, window_size)
        self.switch = switch
        self.buttons = Buttons_sm()
        self.switch_locker = True
        self.from_where = ''
        self.save_file = save_file

        self.read_button_states()

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

    def read_level(self, name):
        file_path = path.join(script_directory, 'saved_levels', f'{name}.json')
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        return data[0]

    def save_button_states(self):
        saved = {'state1': self.buttons.saved1,
                 'state2': self.buttons.saved2,
                 'state3': self.buttons.saved3,
                 'state4': self.buttons.saved4,
                 'state5': self.buttons.saved5,
                 'state6': self.buttons.saved6,
                 'name1': self.buttons.save1,
                 'name2': self.buttons.save2,
                 'name3': self.buttons.save3,
                 'name4': self.buttons.save4,
                 'name5': self.buttons.save5,
                 'name6': self.buttons.save6}
        file_path = path.join(script_directory, 'saved_levels', f'states.json')
        with open(file_path, 'wb') as file:
            pickle.dump(saved, file)

    def read_button_states(self):
        file_path = path.join(script_directory, 'saved_levels', f'states.json')
        with open(file_path, 'rb') as file:
            saves = pickle.load(file)
            self.buttons.saved1 = saves['state1']
            self.buttons.saved2 = saves['state2']
            self.buttons.saved3 = saves['state3']
            self.buttons.saved4 = saves['state4']
            self.buttons.saved5 = saves['state5']
            self.buttons.saved6 = saves['state6']
            self.buttons.save1 = saves['name1']
            self.buttons.save2 = saves['name2']
            self.buttons.save3 = saves['name3']
            self.buttons.save4 = saves['name4']
            self.buttons.save5 = saves['name5']
            self.buttons.save6 = saves['name6']



    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.mm_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.save_button_states()
            self.switch({'from': 'save_menu', 'to': 'main_menu'})
        if event.type == pygame.MOUSEBUTTONDOWN and (self.buttons.level1_save_button_rect.collidepoint(
                mouse_pos()) or self.buttons.level2_save_button_rect.collidepoint(
                mouse_pos()) or self.buttons.level3_save_button_rect.collidepoint(
                mouse_pos()) or self.buttons.level4_save_button_rect.collidepoint(
                mouse_pos()) or self.buttons.level5_save_button_rect.collidepoint(
                mouse_pos()) or self.buttons.level6_save_button_rect.collidepoint(
                mouse_pos())) and self.switch_locker == True:
            self.click(mouse_pos(), mouse_buttons())


    def click(self, mouse_pos, mouse_button):
        if self.from_where == 'level_builder':
            if self.buttons.level1_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0]:  # left mouse on_click
                    self.buttons.save1 = datetime.now().strftime("%y-%m-%d %H_%M_%S")
                    self.buttons.saved1 = True
                    self.save_file(self.buttons.save1)
                if mouse_button[2]:  # right on_click
                    self.buttons.saved1 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save1 + '.json'))
            elif self.buttons.level2_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0]:  # left mouse on_click
                    self.buttons.save2 = datetime.now().strftime("%y-%m-%d %H_%M_%S")
                    self.buttons.saved2 = True
                    self.save_file(self.buttons.save2)
                if mouse_button[2]:  # right on_click
                    self.buttons.saved2 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save2 + '.json'))
            elif self.buttons.level3_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0]:  # left mouse on_click
                    self.buttons.save3 = datetime.now().strftime("%y-%m-%d %H_%M_%S")
                    self.buttons.saved3 = True
                    self.save_file(self.buttons.save3)
                if mouse_button[2]:  # right on_click
                    self.buttons.saved3 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save3 + '.json'))
            elif self.buttons.level4_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0]:  # left mouse on_click
                    self.buttons.save4 = datetime.now().strftime("%y-%m-%d %H_%M_%S")
                    self.buttons.saved4 = True
                    self.save_file(self.buttons.save4)
                if mouse_button[2]:  # right on_click
                    self.buttons.saved4 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save4 + '.json'))
            elif self.buttons.level5_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0]:  # left mouse on_click
                    self.buttons.save5 = datetime.now().strftime("%y-%m-%d %H_%M_%S")
                    self.buttons.saved5 = True
                    self.save_file(self.buttons.save5)
                if mouse_button[2]:  # right on_click
                    self.buttons.saved5 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save5 + '.json'))
            elif self.buttons.level6_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0]:  # left mouse on_click
                    self.buttons.save6 = datetime.now().strftime("%y-%m-%d %H_%M_%S")
                    self.buttons.saved6 = True
                    self.save_file(self.buttons.save6)
                if mouse_button[2]:  # right on_click
                    self.buttons.saved6 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save6 + '.json'))
        if self.from_where == 'main_menu':
            if self.buttons.level1_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0] and self.buttons.saved1:  # left mouse on_click
                    self.switch_locker = False
                    self.switch({'from': 'save_menu', 'to': 'level'}, self.read_level(self.buttons.save1))
                if mouse_button[2]:  # right on_click
                    self.buttons.saved1 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save1 + '.json'))
            elif self.buttons.level2_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0] and self.buttons.saved2:  # left mouse on_click
                    self.switch_locker = False
                    self.switch({'from': 'save_menu', 'to': 'level'}, self.read_level(self.buttons.save2))
                if mouse_button[2]:  # right on_click
                    self.buttons.saved2 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save2 + '.json'))
            elif self.buttons.level3_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0] and self.buttons.saved3:  # left mouse on_click
                    self.switch_locker = False
                    self.switch({'from': 'save_menu', 'to': 'level'}, self.read_level(self.buttons.save3))
                if mouse_button[2]:  # right on_click
                    self.buttons.saved3 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save3 + '.json'))
            elif self.buttons.level4_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0] and self.buttons.saved4:  # left mouse on_click
                    self.switch_locker = False
                    self.switch({'from': 'save_menu', 'to': 'level'}, self.read_level(self.buttons.save4))
                if mouse_button[2]:  # right on_click
                    self.buttons.saved4 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save4 + '.json'))
            elif self.buttons.level5_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0] and self.buttons.saved5:  # left mouse on_click
                    self.switch_locker = False
                    self.switch({'from': 'save_menu', 'to': 'level'}, self.read_level(self.buttons.save5))
                if mouse_button[2]:  # right on_click
                    self.buttons.saved5 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save5 + '.json'))
            elif self.buttons.level6_save_button_rect.collidepoint(mouse_pos):
                if mouse_button[0] and self.buttons.saved6:  # left mouse on_click
                    self.switch_locker = False
                    self.switch({'from': 'save_menu', 'to': 'level'}, self.read_level(self.buttons.save6))
                if mouse_button[2]:  # right on_click
                    self.buttons.saved6 = False
                    os.remove(path.join(script_directory, 'saved_levels', self.buttons.save6 + '.json'))
        self.save_button_states()



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
        mm_size = sx(45)
        mm_margin = sx(6)
        mm_topleft = (self.window_size[0] - mm_size - mm_margin, mm_margin)
        self.mm_rect = pygame.Rect(mm_topleft, (mm_size, mm_size))
        self.image = load(path.join(script_directory, 'graphics', 'menus', 'main_menu_button.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (mm_size, mm_size))

        # button areas
        width = sx(300)
        height = sy(200)
        self.level1_save_button_rect = pygame.Rect((sx(150), sy(135)), (width, height))
        self.level2_save_button_rect = pygame.Rect((width + sx(190), sy(135)), (width, height))
        self.level3_save_button_rect = pygame.Rect((width * 2 + sx(230), sy(135)), (width, height))

        self.level4_save_button_rect = pygame.Rect((sx(150), height + sy(175)), (width, height))
        self.level5_save_button_rect = pygame.Rect((width + sx(190), height + sy(175)), (width, height))
        self.level6_save_button_rect = pygame.Rect((width * 2 + sx(230), height + sy(175)), (width, height))

        self.image_save_button = load(path.join(script_directory, 'graphics', 'menus', 'save_menu', 'save_button.png')).convert_alpha()
        self.image_save_button = pygame.transform.scale(self.image_save_button, (sx(300), sy(200)))

        # saves
        self.font = pygame.font.Font(path.join(script_directory, 'graphics', 'ui', 'ARCADEPI.ttf'), sx(18))
        self.save1 = None
        self.save2 = None
        self.save3 = None
        self.save4 = None
        self.save5 = None
        self.save6 = None

        self.saved1 = False
        self.saved2 = False
        self.saved3 = False
        self.saved4 = False
        self.saved5 = False
        self.saved6 = False


    def display(self):
        self.display_surface.blit(self.image, self.mm_rect.topleft)
        self.display_surface.blit(self.image_save_button, self.level1_save_button_rect.topleft)
        self.display_surface.blit(self.image_save_button, self.level2_save_button_rect.topleft)
        self.display_surface.blit(self.image_save_button, self.level3_save_button_rect.topleft)
        self.display_surface.blit(self.image_save_button, self.level4_save_button_rect.topleft)
        self.display_surface.blit(self.image_save_button, self.level5_save_button_rect.topleft)
        self.display_surface.blit(self.image_save_button, self.level6_save_button_rect.topleft)

        if self.saved1:
            save1_text_surf = self.font.render(str(self.save1), False, '#33323d')
            save1_text_rect = save1_text_surf.get_rect(center=(self.level1_save_button_rect.centerx, self.level1_save_button_rect.centery))
            self.display_surface.blit(save1_text_surf, save1_text_rect)
        if self.saved2:
            save2_text_surf = self.font.render(str(self.save2), False, '#33323d')
            save2_text_rect = save2_text_surf.get_rect(center=(self.level2_save_button_rect.centerx, self.level2_save_button_rect.centery))
            self.display_surface.blit(save2_text_surf, save2_text_rect)
        if self.saved3:
            save3_text_surf = self.font.render(str(self.save3), False, '#33323d')
            save3_text_rect = save3_text_surf.get_rect(center=(self.level3_save_button_rect.centerx, self.level3_save_button_rect.centery))
            self.display_surface.blit(save3_text_surf, save3_text_rect)
        if self.saved4:
            save4_text_surf = self.font.render(str(self.save4), False, '#33323d')
            save4_text_rect = save4_text_surf.get_rect(center=(self.level4_save_button_rect.centerx, self.level4_save_button_rect.centery))
            self.display_surface.blit(save4_text_surf, save4_text_rect)
        if self.saved5:
            save5_text_surf = self.font.render(str(self.save5), False, '#33323d')
            save5_text_rect = save5_text_surf.get_rect(center=(self.level5_save_button_rect.centerx, self.level5_save_button_rect.centery))
            self.display_surface.blit(save5_text_surf, save5_text_rect)
        if self.saved6:
            save6_text_surf = self.font.render(str(self.save6), False, '#33323d')
            save6_text_rect = save6_text_surf.get_rect(center=(self.level6_save_button_rect.centerx, self.level6_save_button_rect.centery))
            self.display_surface.blit(save6_text_surf, save6_text_rect)


        # pygame.draw.rect(self.display_surface, 'red', self.level1_save_button_rect)
        # pygame.draw.rect(self.display_surface, 'red', self.level2_save_button_rect)
        # pygame.draw.rect(self.display_surface, 'red', self.level3_save_button_rect)
        # pygame.draw.rect(self.display_surface, 'red', self.level4_save_button_rect)
        # pygame.draw.rect(self.display_surface, 'red', self.level5_save_button_rect)
        # pygame.draw.rect(self.display_surface, 'red', self.level6_save_button_rect)