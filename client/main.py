from f_read import *
from network import *
import pickle

from pygame.image import load
from pygame.math import Vector2 as vector
from os import walk, getcwd, path

from ui import UI
from level_builder import LevelBuilder
from game_level import GameLevel
from main_menu import Main_menu
from save_menu import Save_menu
from level_menu import Level_menu

from authorisation_menu import Authorisation_menu
from authorisation_s_menu import Authorisation_s_menu
from server_menu import Server_menu
from delete_user_menu import Delete_user_menu
from public_level_menu import Public_level_menu
from local_level_menu import Local_level_menu
from suggestions_menu import Suggestions_menu
from suggestion_menu import Suggestion_menu
from suggest_menu import Suggest_menu
from public_levels_menu import Public_levels_menu
from stranger_level_menu import Stranger_level_menu
from check_file import *

script_directory = path.dirname(path.realpath(__file__))


class Main:
    def __init__(self):
        pygame.init()
        script_directory = path.dirname(path.realpath(__file__))
        print("Current working directory:", getcwd())

        self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.time = pygame.time.Clock()
        self.import_graphics()

        self.level_from_where = ''
        self.client = APIClient()
        self.own_public_levels = []
        self.public_levels = []
        self.chosen_level = []
        self.suggestions = []
        self.chosen_level_local = []
        self.chosen_suggestion = []
        self.chosen_strlevel = []
        self.authorisation_menu = Authorisation_menu(self.switch, self.client.login, self.log_user)
        self.authorisation_s_menu = Authorisation_s_menu(self.switch, self.client.register_user, self.log_user)
        self.server_menu = Server_menu(self.switch, self.get_public_levels_by_author, self.decide_chosen_level,
                                       self.decide_chosen_level_local)
        self.delete_user_menu = Delete_user_menu(self.switch, self.delete_own)
        self.public_level_menu = Public_level_menu(self.switch, self.save_own_level, self.delete_public_level,
                                                   self.update_level_builder_grid)
        self.local_level_menu = Local_level_menu(self.switch, self.publish_level)
        self.suggestions_menu = Suggestions_menu(self.switch, self.get_suggestions, self.decide_chosen_suggestion)
        self.public_levels_menu = Public_levels_menu(self.switch, self.get_public_levels, self.decide_chosen_strlevel)
        self.suggestion_menu = Suggestion_menu(self.switch, self.apply_changes, self.deny_changes,
                                               self.get_suggestion_grid)
        self.stranger_level_menu = Stranger_level_menu(self.switch, self.get_strlevel_grid)
        self.suggest_menu = Suggest_menu(self.switch, self.suggest, self.update_level_builder_grid_str)

        self.main_menu = Main_menu(self.switch)
        self.level_menu = Level_menu(self.switch)
        self.save_menu = Save_menu(self.switch, self.save_level)

        self.max_health = 100
        self.cur_health = 100
        self.coins = 0
        self.diamonds = 0
        self.player_dead = False

        self.ui = UI(self.display_surface)

        self.replacement = {}
        self.level_builder_active = False
        self.level_active = False
        self.main_menu_active = True
        self.level_menu_active = False
        self.save_menu_active = False
        self.authorisation_menu_active = False
        self.authorisation_s_menu_active = False
        self.server_menu_active = False
        self.delete_user_menu_active = False
        self.public_level_menu_active = False
        self.local_level_menu_active = False
        self.suggestions_menu_active = False
        self.public_levels_menu_active = False
        self.suggestion_menu_active = False
        self.stranger_level_menu_active = False
        self.suggest_menu_active = False
        self.passage = Passage(self.manage_routes, self.create_level)

        self.level_builder = LevelBuilder(self.soil, self.switch)

        self.music = self.no_level_sounds['music']
        self.music.set_volume(0.2)
        self.music.play(loops=-1)

        mouse_cursor = pygame.cursors.Cursor((0, 0), load(path.join(script_directory, 'graphics', 'cursors', 'mouse.png')).convert_alpha())
        pygame.mouse.set_cursor(mouse_cursor)

    def import_graphics(self):
        script_directory = path.dirname(path.realpath(__file__))

        def gpath(*args):
            return path.join(script_directory, 'graphics', *args)

        def ipath(*args):
            return path.join(script_directory, 'graphics', 'info', *args)

        def epath(*args):
            return path.join(script_directory, 'graphics', 'enemies', *args)

        def read_static(file_path):
            return load(file_path).convert_alpha()

        script_directory = path.dirname(path.realpath(__file__))

        self.soil = read_multiple_folders(gpath('terrain', 'soil'))
        self.bot_water = read_static(gpath('terrain', 'water', 'water_bottom.png'))
        self.top_water_frames = read_folder(gpath('terrain', 'water', 'animation'))
        self.platform = read_static(gpath('terrain', 'platform', 'platform.png'))
        self.clouds = read_folder(gpath('clouds'))

        palm_dir = gpath('terrain', 'palm')
        self.palm = {folder: read_folder(path.join(palm_dir, folder))
                     for folder in next(walk(palm_dir))[1]}

        self.interract_info = read_static(ipath('interract_info', 'interract_info.png'))
        self.finish_info = read_static(ipath('finish_info', 'finish_info.png'))
        self.sign_bottom = read_static(ipath('sign_bottom', 'sign_bottom.png'))
        self.sign_top = read_static(ipath('sign_top', 'sign_top.png'))
        self.sign_left = read_static(ipath('sign_left', 'sign_left.png'))
        self.sign_right = read_static(ipath('sign_right', 'sign_right.png'))

        self.bricks_bg = read_static(gpath('terrain', 'bricks', 'bricks_bg', 'bricks_bg.png'))
        self.bricks_fg = read_static(gpath('terrain', 'bricks', 'bricks_fg', 'bricks_fg.png'))

        self.golden_coin = read_folder(gpath('items', 'golden_coin'))
        self.silver_coin = read_folder(gpath('items', 'silver_coin'))
        self.diamond = read_folder(gpath('items', 'diamond'))
        self.disappearance_particle = read_folder(gpath('items', 'particle'))
        self.heal_potion = read_folder(gpath('items', 'heal_potion'))

        self.spikes = read_static(epath('spikes', 'spikes.png'))
        pig_dir = epath('pig')
        self.pig = {folder: read_folder(path.join(pig_dir, folder)) for folder in next(walk(pig_dir))[1]}
        cannon_dir = epath('cannon_left')
        self.cannon = {folder: read_folder(path.join(cannon_dir, folder)) for folder in next(walk(cannon_dir))[1]}
        self.cannonball = read_static(epath('cannonball', 'cannonball.png'))
        self.saw = read_folder(epath('saw_bottom'))
        self.mace = read_static(epath('mace', 'mace.png'))
        self.mace_chain = read_static(epath('mace_chain', 'mace_chain.png'))

        player_dir = gpath('player')
        self.player_graphics = {folder: read_folder(path.join(player_dir, folder)) for folder in
                                next(walk(player_dir))[1]}

        audio_dir = path.join(script_directory, 'audio')
        self.no_level_sounds = {
            'music': pygame.mixer.Sound(path.join(audio_dir, 'No_level.ogg'))
        }
        self.gameplay_sounds = {
            'treasure': pygame.mixer.Sound(path.join(audio_dir, 'treasure.wav')),
            'damage': pygame.mixer.Sound(path.join(audio_dir, 'damage.wav')),
            'jump': pygame.mixer.Sound(path.join(audio_dir, 'jump.wav')),
            'music': pygame.mixer.Sound(path.join(audio_dir, 'Level.ogg')),
        }

    def log_user(self):
        self.own_public_levels = self.get_public_levels_by_author()
        self.server_menu.public_level_list.update_items(self.own_public_levels)
        self.server_menu.local_level_list.update_items_local()
        self.public_levels = self.client.get_public_levels()
        self.public_levels_menu.level_list.update_items(self.public_levels)
        self.suggestions = self.client.view_change_requests()
        self.suggestions_menu.suggestions_list.update_items(self.suggestions)

    def get_public_levels_by_author(self):
        author_username = self.client.username
        return self.client.get_public_levels_by_author(author_username)

    def decide_chosen_level(self, id):
        self.chosen_level = self.client.get_level_by_id(id)
        self.public_level_menu.input_fields.update_info(self.chosen_level)

    def decide_chosen_level_local(self, name):
        file_path = path.join(script_directory, 'saved_levels', f'{name}.json')
        with open(file_path, 'rb') as file:
            grid = pickle.load(file)
        self.level_builder.update_from_grid(grid)
        self.chosen_level_local = [self.serialize_grid(grid[0]), grid[1]]
        self.local_level_menu.input_fields.update_info(name)

    def publish_level(self):
        grid = self.level_builder.generate_grid()
        if validate_level_data(grid):
            self.client.upload_level(
                title=self.local_level_menu.input_fields.get_level(),
                description=self.local_level_menu.input_fields.get_description(),
                data=[self.serialize_grid(grid[0]), grid[1]],
                is_public=True
            )
        else:
            print('Bad data')

    def delete_public_level(self):
        level_id_to_delete = self.chosen_level.get('id')
        self.client.delete_level(level_id_to_delete)

    def update_level_builder_grid(self):
        grid = self.chosen_level.get('data')
        self.level_builder.update_from_grid([self.deserialize_grid(grid[0]), grid[1]])

    def save_own_level(self, tittle, description):
        id = self.chosen_level.get('id')
        data = self.level_builder.generate_grid()
        if validate_level_data(data):
            self.client.edit_level(
                level_id=id,
                title=tittle,
                description=description,
                data=[self.serialize_grid(data[0]), data[1]]
            )
        else:
            print('Bad data')

    def delete_own(self):
        if self.client.delete_account():
            print("Акаунт успішно видалено")
        else:
            print("Помилка при видаленні акаунта")

    def get_suggestions(self):
        return self.client.view_change_requests()

    def decide_chosen_suggestion(self, id):
        self.chosen_suggestion = self.client.get_change_request_by_id(id)
        self.suggestion_menu.labels.update_info(self.chosen_suggestion)

    def get_suggestion_grid(self):
        return self.deserialize_grid(self.chosen_suggestion.get('proposed_data')[0])

    def apply_changes(self):
        level_id = self.chosen_suggestion.get('level_id')
        change_id = self.chosen_suggestion.get('id')
        if self.client.accept_change(level_id, change_id):
            print("Зміну успішно схвалено")
        else:
            print("Не вдалося схвалити зміну")

    def deny_changes(self):
        level_id = self.chosen_suggestion.get('level_id')
        change_id = self.chosen_suggestion.get('id')
        if self.client.reject_change(level_id, change_id):
            print("Зміну відхилено")
        else:
            print("Не вдалося відхилити зміну")

    def get_public_levels(self):
        return self.client.get_public_levels()

    def decide_chosen_strlevel(self, id):
        self.chosen_strlevel = self.client.get_level_by_id(id)
        self.stranger_level_menu.labels.update_info(self.chosen_strlevel)
        self.suggest_menu.labels.update_info(self.chosen_strlevel)

    def get_strlevel_grid(self):
        return self.deserialize_grid(self.chosen_strlevel.get('data')[0])

    def update_level_builder_grid_str(self):
        grid = self.chosen_strlevel.get('data')
        self.level_builder.update_from_grid([self.deserialize_grid(grid[0]), grid[1]])

    def suggest(self):
        grid = self.level_builder.generate_grid()
        change_data = {
            "data": [self.serialize_grid(grid[0]), grid[1]],
            "comment": self.suggest_menu.input_fields.get_comment()
        }
        if validate_level_data(grid):
            self.client.propose_change(level_id=self.chosen_strlevel.get('id'), data=change_data.get('data'),
                                       comment=change_data.get('comment'))
        else:
            print('Bad data')

    def deserialize_grid(self, data_from_client: dict) -> dict:
        return {
            layer: {
                tuple(map(int, key.split(','))): value
                for key, value in layer_data.items()
            }
            for layer, layer_data in data_from_client.items()
        }

    def serialize_grid(self, grid_data: dict) -> dict:
        return {
            layer: {
                f'{key[0]},{key[1]}': value
                for key, value in layer_data.items()
            }
            for layer, layer_data in grid_data.items()
        }

    def set_level_from_where(self, from_where):
        self.level_from_where = from_where

    def get_level_from_where(self):
        return self.level_from_where

    def change_coins(self, amount, nulify=None):
        self.coins += amount
        if nulify:
            self.coins = 0

    def change_health(self, amount, nulify=None):
        if amount < 0 and self.cur_health - amount > self.max_health:
            self.cur_health = self.max_health
        else:
            self.cur_health -= amount

        if nulify:
            self.cur_health = 100

    def change_diamonds(self, amount, nulify=None):
        self.diamonds += amount
        if nulify:
            self.diamonds = 0

    def level_complete(self):
        if self.diamonds == 3:
            self.level.complete = True

    def get_score(self):
        return self.coins

    def get_diamonds(self):
        return self.diamonds

    def death(self):
        if self.cur_health <= 0:
            self.player_dead = True

    def player_dead_get(self):
        return self.player_dead

    def change_player_dead(self):
        self.player_dead = False

    def save_level(self, name):
        file_path = path.join(script_directory, 'saved_levels', f'{name}.json')
        with open(file_path, 'wb') as file:
            pickle.dump(self.level_builder.generate_grid(), file)

    def change_routes(self, routes):
        self.replacement = routes

    def manage_routes(self):
        if self.replacement['from'] == 'level_builder':
            self.level_builder_active = False
        elif self.replacement['from'] == 'level':
            self.coins = 0
            self.cur_health = 100
            self.diamonds = 0
            self.player_dead = False
            self.level.background_music.stop()
            self.music.play(loops=-1)
            self.level_active = False
        elif self.replacement['from'] == 'main_menu':
            self.main_menu_active = False
        elif self.replacement['from'] == 'level_menu':
            self.level_menu_active = False
        elif self.replacement['from'] == 'save_menu':
            self.save_menu_active = False
        elif self.replacement['from'] == 'authorisation_menu':
            self.authorisation_menu_active = False
        elif self.replacement['from'] == 'authorisation_s_menu':
            self.authorisation_s_menu_active = False
        elif self.replacement['from'] == 'server_menu':
            self.server_menu_active = False
        elif self.replacement['from'] == 'delete_user_menu':
            self.delete_user_menu_active = False
        elif self.replacement['from'] == 'public_level_menu':
            self.public_level_menu_active = False
        elif self.replacement['from'] == 'local_level_menu':
            self.local_level_menu_active = False
        elif self.replacement['from'] == 'suggestions_menu':
            self.suggestions_menu_active = False
        elif self.replacement['from'] == 'public_levels_menu':
            self.public_levels_menu_active = False
        elif self.replacement['from'] == 'suggestion_menu':
            self.suggestion_menu_active = False
        elif self.replacement['from'] == 'stranger_level_menu':
            self.stranger_level_menu_active = False
        elif self.replacement['from'] == 'suggest_menu':
            self.suggest_menu_active = False

        if self.replacement['to'] == 'level_builder':
            if self.replacement['from'] != 'level':
                self.level_builder.from_where = self.replacement['from']
            self.level_builder_active = True
        elif self.replacement['to'] == 'level':
            if self.replacement['from'] != 'level':
                self.set_level_from_where(self.replacement['from'])
            self.music.stop()
            self.level.background_music.play(loops=-1)
            self.level_active = True
        elif self.replacement['to'] == 'main_menu':
            self.main_menu_active = True
        elif self.replacement['to'] == 'level_menu':
            self.level_menu_active = True
        elif self.replacement['to'] == 'save_menu':
            self.save_menu.from_where = self.replacement['from']
            self.save_menu_active = True
        elif self.replacement['to'] == 'authorisation_menu':
            self.authorisation_menu_active = True
        elif self.replacement['to'] == 'authorisation_s_menu':
            self.authorisation_s_menu_active = True
        elif self.replacement['to'] == 'server_menu':
            self.server_menu_active = True
        elif self.replacement['to'] == 'delete_user_menu':
            self.delete_user_menu_active = True
        elif self.replacement['to'] == 'public_level_menu':
            self.public_level_menu_active = True
        elif self.replacement['to'] == 'local_level_menu':
            self.local_level_menu_active = True
        elif self.replacement['to'] == 'suggestions_menu':
            self.suggestions_menu_active = True
        elif self.replacement['to'] == 'public_levels_menu':
            self.public_levels_menu_active = True
        elif self.replacement['to'] == 'suggestion_menu':
            self.suggestion_menu_active = True
        elif self.replacement['to'] == 'stranger_level_menu':
            self.stranger_level_menu_active = True
        elif self.replacement['to'] == 'suggest_menu':
            self.suggest_menu_active = True

        if self.level_builder_active:
            self.level_builder.switch_locker = True
        if self.level_active:
            self.level.switch_locker = True
        if self.main_menu_active:
            self.main_menu.switch_locker = True
        if self.level_menu_active:
            self.level_menu.switch_locker = True
        if self.save_menu_active:
            self.save_menu.switch_locker = True
        if self.authorisation_menu_active:
            self.authorisation_menu.switch_locker = True
        if self.authorisation_s_menu_active:
            self.authorisation_s_menu.switch_locker = True
        if self.server_menu_active:
            self.server_menu.switch_locker = True
        if self.delete_user_menu_active:
            self.delete_user_menu.switch_locker = True
        if self.public_level_menu_active:
            self.public_level_menu.switch_locker = True
        if self.local_level_menu_active:
            self.local_level_menu.switch_locker = True
        if self.suggestions_menu_active:
            self.suggestions_menu.switch_locker = True
        if self.public_levels_menu_active:
            self.public_levels_menu.switch_locker = True
        if self.suggestion_menu_active:
            self.suggestion_menu.switch_locker = True
        if self.stranger_level_menu_active:
            self.stranger_level_menu.switch_locker = True
        if self.suggest_menu_active:
            self.suggest_menu.switch_locker = True

        if not self.level_active:
            self.coins = 0
            self.cur_health = 100
            self.diamonds = 0
            self.player_dead = False

    def switch(self, routes, grid=None):
        self.change_routes(routes)
        self.passage.active = True
        if grid:
            self.passage.set_grid(grid)

    def create_level(self, grid):
        self.level = GameLevel(
            grid,
            self.switch, {
                'soil': self.soil,
                'water bottom': self.bot_water,
                'water top': self.top_water_frames,
                'golden coin': self.golden_coin,
                'silver coin': self.silver_coin,
                'heal_potion': self.heal_potion,
                'diamond': self.diamond,
                'particle': self.disappearance_particle,
                'palms': self.palm,
                'spikes': self.spikes,
                'pig': self.pig,
                'cannon': self.cannon,
                'mace': self.mace,
                'mace_chain': self.mace_chain,
                'player': self.player_graphics,
                'cannonball': self.cannonball,
                'clouds': self.clouds,
                'bricks fg': self.bricks_fg,
                'bricks bg': self.bricks_bg,
                'saw': self.saw,
                'platforms': self.platform,
                'interract_info': self.interract_info,
                'finish_info': self.finish_info,
                'sign bottom': self.sign_bottom,
                'sign top': self.sign_top,
                'sign left': self.sign_left,
                'sign right': self.sign_right,
            },
            self.gameplay_sounds,
            self.change_coins,
            self.change_health,
            self.player_dead_get,
            self.change_diamonds,
            self.get_score,
            self.get_diamonds,
            self.change_player_dead,
            self.get_level_from_where
        )

    def run(self):
        while True:
            dt = self.time.tick() / 1000

            if self.level_builder_active:
                self.level_builder.run(dt)
            elif self.level_active:
                self.level.run(dt)
                self.ui.show_health(self.cur_health, self.max_health)
                self.ui.show_coins(self.coins)
                self.level_complete()
                self.death()
            elif self.main_menu_active:
                self.main_menu.run(dt)
            elif self.level_menu_active:
                self.level_menu.run(dt)
            elif self.save_menu_active:
                self.save_menu.run(dt)
            elif self.authorisation_menu_active:
                self.authorisation_menu.run(dt)
            elif self.authorisation_s_menu_active:
                self.authorisation_s_menu.run(dt)
            elif self.server_menu_active:
                self.server_menu.run(dt)
            elif self.delete_user_menu_active:
                self.delete_user_menu.run(dt)
            elif self.public_level_menu_active:
                self.public_level_menu.run(dt)
            elif self.local_level_menu_active:
                self.local_level_menu.run(dt)
            elif self.suggestions_menu_active:
                self.suggestions_menu.run(dt)
            elif self.public_levels_menu_active:
                self.public_levels_menu.run(dt)
            elif self.suggestion_menu_active:
                self.suggestion_menu.run(dt)
            elif self.stranger_level_menu_active:
                self.stranger_level_menu.run(dt)
            elif self.suggest_menu_active:
                self.suggest_menu.run(dt)
            self.passage.display(dt)
            pygame.display.update()


class Passage:
    def __init__(self, manage_routes, create_level):
        self.display_surface = pygame.display.get_surface()
        self.window_size = self.display_surface.get_size()
        self.manage_routes = manage_routes
        self.active = False
        self.grid = None
        self.create_level = create_level

        self.diaphragm = 0
        self.dir = 1
        self.center = (self.window_size[0] / 2, self.window_size[1] / 2)
        self.circle = vector(self.center).magnitude()
        self.limit = self.circle + 150

    def set_grid(self, grid):
        self.grid = grid

    def display(self, dt):
        if self.active:
            self.diaphragm += 2000 * dt * self.dir
            if self.diaphragm >= self.limit:
                self.dir = -1
                self.diaphragm += -10
                if self.grid:
                    self.create_level(self.grid)
                self.manage_routes()

            if self.diaphragm < 0:
                self.active = False
                self.diaphragm = 0
                self.dir = 1
            pygame.draw.circle(self.display_surface, 'black', self.center, self.circle, int(self.diaphragm))


if __name__ == '__main__':
    main = Main()
    main.run()
