import pygame
from os import path

class UI:
    def __init__(self, surface):
        script_dir = path.dirname(path.realpath(__file__))
        self.display_surface = surface


        self._base_width, self._base_height = 1280, 720
        self._update_scale()


        self.health_bar = pygame.image.load(path.join(script_dir, 'graphics', 'ui', 'health_bar.png')).convert_alpha()
        self.health_bar = pygame.transform.scale(self.health_bar, self._scale(192, 64))
        self.health_bar_pos = self._scale_pos(54, 39)
        self.bar_max_width = self._scale_value(152, axis='x')
        self.bar_height = self._scale_value(4, axis='y')


        self.coin = pygame.image.load(path.join(script_dir, 'graphics', 'ui', 'coin.png')).convert_alpha()
        self.coin = pygame.transform.scale(self.coin, self._scale(32, 32))
        self.coin_rect = self.coin.get_rect(topleft=self._scale_pos(50, 61))

        self.font = pygame.font.Font(path.join(script_dir, 'graphics', 'ui', 'ARCADEPI.ttf'), self._scale_value(30, axis='x'))

    def _update_scale(self):
        width, height = self.display_surface.get_size()
        self._mx = width / self._base_width
        self._my = height / self._base_height

    def _scale_value(self, val, axis='x'):
        return int(val * (self._mx if axis == 'x' else self._my))

    def _scale(self, w, h):
        return (self._scale_value(w, 'x'), self._scale_value(h, 'y'))

    def _scale_pos(self, x, y):
        return self._scale_value(x, 'x'), self._scale_value(y, 'y')

    def show_health(self, current, full):
        self._update_scale()
        self.display_surface.blit(self.health_bar, self._scale_pos(20, 10))
        ratio = current / full
        current_width = self.bar_max_width * ratio
        bar_rect = pygame.Rect(self.health_bar_pos, (current_width, self.bar_height))
        pygame.draw.rect(self.display_surface, '#dc4949', bar_rect)

    def show_coins(self, amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        text_surf = self.font.render(str(amount), False, '#33323d')
        text_rect = text_surf.get_rect(midleft=(self.coin_rect.right + 4, self.coin_rect.centery))
        self.display_surface.blit(text_surf, text_rect)