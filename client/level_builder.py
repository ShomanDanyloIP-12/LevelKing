import sys
from pygame.image import load
from os import path
from pygame.mouse import get_pressed as mouse_buttons
from math import floor
from pygame.math import Vector2 as vector
from pygame.mouse import get_pos as mouse_pos
from f_read import *

from items_selector import Items_selector
from timer import Timer

from random import choice, randint

tile_size = 64

class LevelBuilder:
    def __init__(self, soil_tiles, switch):
        script_directory = path.dirname(path.realpath(__file__))
        self.display_surface = pygame.display.get_surface()
        self.layout_elements = {}
        self.switch = switch
        self.from_where = ''
        self.switch_locker = True
        self.window_size = self.display_surface.get_size()

        self.import_graphics()
        self.soil_tiles = soil_tiles

        self.starting_point = vector()
        self.layout_active = False
        self.layout_offset = vector()
        self.selected_item_index = 2
        self.previously_selected_cell = None
        self.items_selector = Items_selector()

        self.layout_objects = pygame.sprite.Group()
        self.foreground_object = pygame.sprite.Group()
        self.background_object = pygame.sprite.Group()
        self.grid_lines_surface = pygame.Surface(self.window_size)
        self.grid_lines_surface.set_colorkey('green')
        self.grid_lines_surface.set_alpha(25)
        self.object_drag_active = False
        self.object_spawn_timer = Timer(300)

        self.create_player((200, self.window_size[1] / 2))
        self.create_sky((self.window_size[0] / 2, self.window_size[1] / 2))
        self.layout_clouds = []
        self.cloud_surface = read_folder(path.join(script_directory, 'graphics', 'clouds'))
        self.cloud_spawn_time = pygame.USEREVENT + 1
        pygame.time.set_timer(self.cloud_spawn_time, 2000)
        self.startup_clouds()


    def create_player(self, pos):
        self.player = LayoutMovableObject(
            pos=pos,
            frames=self.animation_assets[0]['frames'],
            tile_id=0,
            starting_point=self.starting_point,
            group=[self.layout_objects, self.foreground_object])

    def create_sky(self, pos):
        self.sky_handle = LayoutMovableObject(
            pos=pos,
            frames=[self.sky_handle_surf],
            tile_id=1,
            starting_point=self.starting_point,
            group=[self.layout_objects, self.background_object])

    def import_graphics(self):
        def gpath(*args):
            return path.join(script_directory, 'graphics', *args)

        def load_img(*args):
            return load(gpath(*args)).convert_alpha()

        def load_folder(*args):
            return read_folder(gpath(*args))

        def load_multiple(*args):
            return read_multiple_folders(gpath(*args))

        script_directory = path.dirname(path.realpath(__file__))
        graphics_dir = path.join(script_directory, 'graphics')

        self.water_bottom = load_img('terrain', 'water', 'water_bottom.png')
        self.platform = load_img('terrain', 'platform', 'platform.png')
        self.sky_handle_surf = load_img('cursors', 'handle.png')
        self.bricks_bg = load_img('terrain', 'bricks', 'bricks_bg', 'bricks_bg.png')
        self.bricks_fg = load_img('terrain', 'bricks', 'bricks_fg', 'bricks_fg.png')

        info_dir = lambda name: load_img('info', name, f'{name}.png')
        for info in ['interract_info', 'finish_info', 'sign_bottom', 'sign_top', 'sign_left', 'sign_right']:
            setattr(self, info, info_dir(info))

        self.level_builder_map = {}
        definitions = [
            (0, 'player', 'object', None, ['player', 'idle_right']),
            (1, 'sky', 'object', None, None),
            (2, 'terrain', 'tile', ['preview', 'soil.png'], None),
            (3, 'water', 'tile', ['preview', 'water.png'], ['terrain', 'water', 'animation']),
            (4, 'coin', 'tile', ['preview', 'golden_coin.png'], ['items', 'golden_coin']),
            (5, 'coin', 'tile', ['preview', 'silver_coin.png'], ['items', 'silver_coin']),
            (6, 'coin', 'tile', ['preview', 'diamond.png'], ['items', 'diamond']),
            (7, 'enemy', 'tile', ['preview', 'spikes.png'], ['enemies', 'spikes']),
            (8, 'enemy', 'tile', ['preview', 'pig.png'], ['enemies', 'pig', 'idle']),
            (9, 'enemy', 'tile', ['preview', 'cannon_left.png'], ['enemies', 'cannon_left', 'idle']),
            (10, 'enemy', 'tile', ['preview', 'cannon_right.png'], ['enemies', 'cannon_right', 'idle']),
            (11, 'palm_fg', 'object', ['preview', 'small_fg.png'], ['terrain', 'palm', 'small_fg']),
            (12, 'palm_fg', 'object', ['preview', 'large_fg.png'], ['terrain', 'palm', 'large_fg']),
            (13, 'palm_fg', 'object', ['preview', 'left_fg.png'], ['terrain', 'palm', 'left_fg']),
            (14, 'palm_fg', 'object', ['preview', 'right_fg.png'], ['terrain', 'palm', 'right_fg']),
            (15, 'palm_bg', 'object', ['preview', 'small_bg.png'], ['terrain', 'palm', 'small_bg']),
            (16, 'palm_bg', 'object', ['preview', 'large_bg.png'], ['terrain', 'palm', 'large_bg']),
            (17, 'palm_bg', 'object', ['preview', 'left_bg.png'], ['terrain', 'palm', 'left_bg']),
            (18, 'palm_bg', 'object', ['preview', 'right_bg.png'], ['terrain', 'palm', 'right_bg']),
            (19, 'bricks_fg', 'tile', ['preview', 'bricks_fg.png'], ['terrain', 'bricks', 'bricks_fg']),
            (20, 'bricks_bg', 'tile', ['preview', 'bricks_bg.png'], ['terrain', 'bricks', 'bricks_bg']),
            (21, 'enemy', 'tile', ['preview', 'saw_bottom.png'], ['enemies', 'saw_bottom']),
            (22, 'enemy', 'tile', ['preview', 'saw_top.png'], ['enemies', 'saw_top']),
            (23, 'enemy', 'tile', ['preview', 'saw_left.png'], ['enemies', 'saw_left']),
            (24, 'enemy', 'tile', ['preview', 'saw_right.png'], ['enemies', 'saw_right']),
            (25, 'platform', 'tile', ['preview', 'platform.png'], ['terrain', 'platform']),
            (26, 'interract_info', 'tile', ['preview', 'info.png'], ['info', 'interract_info', 'interract_info']),
            (27, 'finish_info', 'tile', ['preview', 'finish_info.png'], ['info', 'finish_info', 'finish_info']),
            (28, 'sign_bottom', 'tile', ['preview', 'sign_bottom.png'], ['info', 'sign_bottom', 'sign_bottom']),
            (29, 'sign_top', 'tile', ['preview', 'sign_top.png'], ['info', 'sign_top', 'sign_top']),
            (30, 'sign_left', 'tile', ['preview', 'sign_left.png'], ['info', 'sign_left', 'sign_left']),
            (31, 'sign_right', 'tile', ['preview', 'sign_right.png'], ['info', 'sign_right', 'sign_right']),
            (32, 'enemy', 'tile', ['preview', 'mace.png'], ['enemies', 'chained_mace']),
            (33, 'coin', 'tile', ['preview', 'heal_potion.png'], ['items', 'heal_potion']),
        ]

        for idx, style, type_, preview, graphics in definitions:
            self.level_builder_map[idx] = {
                'style': style,
                'type': type_,
                'preview': gpath(*preview) if preview else None,
                'graphics': gpath(*graphics) if graphics else None,
            }

        self.animation_assets = {}
        for key, value in self.level_builder_map.items():
            path_to_graphics = value.get('graphics')
            if path_to_graphics:
                frames = read_folder(path_to_graphics)
                self.animation_assets[key] = {
                    'frame_index': 0,
                    'frames': frames,
                    'length': len(frames)
                }

        self.preview_surfs = {key: load(value['preview']) for key, value in self.level_builder_map.items() if value['preview']}

    def update_frames(self, dt):
        speed = 8 * dt
        for anim in self.animation_assets.values():
            index = anim.get('frame index', 0) + speed
            anim['frame index'] = index if index < anim['length'] else 0

    def mouse_which_object(self):
        for entity in self.layout_objects:
            if entity.rect.collidepoint(mouse_pos()):
                return entity

    def clear_grid(self):
        self.layout_elements = {}
        self.layout_objects.empty()
        self.foreground_object.empty()
        self.background_object.empty()
        self.create_player((200, self.window_size[1] / 2))
        self.create_sky((self.window_size[0] / 2, self.window_size[1] / 2))

    def update_from_grid(self, coords):
        self.layout_elements = {}
        self.layout_objects.empty()
        self.foreground_object.empty()
        self.background_object.empty()
        grid = coords[0]
        topleft = coords[1]
        left = topleft[0]
        top = topleft[1]

        for layer_name, layer in grid.items():
            for pos_str, value in layer.items():
                if isinstance(pos_str, str):
                    x, y = map(int, pos_str.split(','))
                else:
                    x, y = pos_str

                abs_x = x + left * tile_size
                abs_y = y + top * tile_size
                tile_x = abs_x // tile_size
                tile_y = abs_y // tile_size
                tile_pos = (tile_x, tile_y)

                if tile_pos not in self.layout_elements:
                    self.layout_elements[tile_pos] = LayoutObject(self.level_builder_map)

                entity = self.layout_elements[tile_pos]

                if layer_name == 'terrain':
                    if value == '0':
                        entity.terrain_neighbors = []
                        entity.has_terrain = True
                    else:
                        entity.terrain_neighbors = list(value)
                        entity.has_terrain = True

                elif layer_name == 'water':
                    entity.water_on_top = (value == 'bottom')

                elif layer_name == 'platforms':
                    entity.has_platform = True

                elif layer_name == 'bricks bg':
                    entity.has_bricks_bg = True

                elif layer_name == 'bricks fg':
                    entity.has_bricks_fg = True

                elif layer_name == 'coins':
                    entity.coin = value

                elif layer_name == 'enemies':
                    entity.enemy = value

                elif layer_name == 'interract_info':
                    entity.has_interract_info = True

                elif layer_name == 'finish_info':
                    entity.has_finish_info = True

                elif layer_name == 'sign bottom':
                    entity.has_sign_bottom = True

                elif layer_name == 'sign top':
                    entity.has_sign_top = True

                elif layer_name == 'sign left':
                    entity.has_sign_left = True

                elif layer_name == 'sign right':
                    entity.has_sign_right = True

                elif layer_name in ['bg palms', 'fg objects']:
                    offset = vector(abs_x - tile_x * tile_size, abs_y - tile_y * tile_size)
                    tile_id = value
                    entity.objects.append((tile_id, offset))

        for tile_pos, entity in self.layout_elements.items():
            for tile_id, offset in entity.objects:
                screen_pos = (vector(tile_pos) * tile_size) + offset + self.layout_offset
                if tile_id != 0 and tile_id != 1:
                    groups = [self.layout_objects, self.background_object] if self.level_builder_map[tile_id]['style'] == 'palm_bg' else [
                        self.layout_objects, self.foreground_object]
                    LayoutMovableObject(
                        pos=screen_pos,
                        frames=self.animation_assets[tile_id]['frames'],
                        tile_id=tile_id,
                        starting_point=self.starting_point,
                        group=groups,
                        is_input=True
                    )
                elif tile_id == 0:
                    self.create_player(screen_pos)
                elif tile_id == 1:
                    self.create_sky(screen_pos)

    def get_cell_coordinates(self, obj=None):
        pos = vector(mouse_pos()) if obj is None else vector(obj.distance_to_starting_point)
        local_pos = pos - self.starting_point
        col = floor(local_pos.x / tile_size)
        row = floor(local_pos.y / tile_size)
        return col, row

    def generate_grid(self):
        for entity in self.layout_elements.values():
            entity.objects.clear()

        for object in self.layout_objects:
            entity = self.get_cell_coordinates(object)
            offset = vector(object.distance_to_starting_point) - vector(entity) * tile_size

            if entity in self.layout_elements:
                self.layout_elements[entity].add_object(object.tile_id, offset)
            else:
                self.layout_elements[entity] = LayoutObject(self.level_builder_map, object.tile_id, offset)

        layer_names = [
            'bricks bg', 'bg palms', 'water', 'interract_info', 'finish_info',
            'sign bottom', 'sign top', 'sign left', 'sign right',
            'terrain', 'bricks fg', 'platforms', 'enemies',
            'coins', 'fg objects'
        ]
        layers = {name: {} for name in layer_names}

        min_x = min(tile[0] for tile in self.layout_elements)
        min_y = min(tile[1] for tile in self.layout_elements)
        offset = [min_x, min_y]

        for (entity_x, entity_y), entity in self.layout_elements.items():
            rel_x = (entity_x - min_x) * tile_size
            rel_y = (entity_y - min_y) * tile_size
            base_pos = (rel_x, rel_y)

            if entity.has_water:
                layers['water'][base_pos] = entity.get_water()

            if entity.has_platform:
                layers['platforms'][base_pos] = 'platform'

            if entity.has_terrain:
                terrain = entity.get_terrain()
                layers['terrain'][base_pos] = terrain if terrain in self.soil_tiles else '0'

            if entity.coin:
                coin_pos = (rel_x + tile_size // 2, rel_y + tile_size // 2)
                layers['coins'][coin_pos] = entity.coin

            if entity.enemy:
                layers['enemies'][base_pos] = entity.enemy

            if entity.has_bricks_bg:
                layers['bricks bg'][base_pos] = 'bricks_bg'

            if entity.has_bricks_fg:
                layers['bricks fg'][base_pos] = 'bricks_fg'

            for obj_id, offset_vec in entity.objects:
                target = 'bg palms' if self.level_builder_map.get(obj_id, {}).get('style') == 'palm_bg' else 'fg objects'
                obj_pos = (int(rel_x + offset_vec.x), int(rel_y + offset_vec.y))
                layers[target][obj_pos] = obj_id

            info_flags = {
                'interract_info': entity.has_interract_info,
                'finish_info': entity.has_finish_info,
                'sign bottom': entity.has_sign_bottom,
                'sign top': entity.has_sign_top,
                'sign left': entity.has_sign_left,
                'sign right': entity.has_sign_right,
            }

            for name, flag in info_flags.items():
                if flag:
                    layers[name][base_pos] = name.replace(' ', '_')

        return [layers, offset]

    def event_loop(self):
        for event in pygame.event.get():
            if self._handle_quit(event):
                return

            if self._handle_return(event):
                return

            self.actions_input(event)
            self.buttons_click(event)
            self.update_object_drag(event)
            self.layout_add()
            self.layout_remove()
            self.selection_item_hotkeys(event)
            self.add_clouds(event)

    def _handle_quit(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        return False

    def _handle_return(self, event):
        if (
                event.type == pygame.KEYDOWN and
                event.key == pygame.K_RETURN and
                self.switch_locker
        ):
            grid_data = self.generate_grid()
            if len(grid_data[0]['terrain']) != 0:
                self.switch_locker = False
                self.switch({'from': 'level_builder', 'to': 'level'}, grid_data[0])
                return True
        return False

    def actions_input(self, event):
        self._handle_middle_mouse(event)
        self._handle_scroll(event)
        self._update_layout()

    def _handle_middle_mouse(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[1]:
            self.layout_active = True
            self.layout_offset = vector(mouse_pos()) - self.starting_point
        elif not mouse_buttons()[1]:
            self.layout_active = False

    def _handle_scroll(self, event):
        if event.type == pygame.MOUSEWHEEL:
            delta = event.y * 50
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.starting_point.y -= delta
            else:
                self.starting_point.x -= delta
            for entity in self.layout_objects:
                entity.layout_pos(self.starting_point)

    def _update_layout(self):
        if self.layout_active:
            self.starting_point = vector(mouse_pos()) - self.layout_offset
            for entity in self.layout_objects:
                entity.layout_pos(self.starting_point)

    def selection_item_hotkeys(self, event):
        if event.type != pygame.KEYDOWN:
            return

        key_delta = {
            pygame.K_RIGHT: 1,
            pygame.K_LEFT: -1
        }

        delta = key_delta.get(event.key)
        if delta:
            self.selected_item_index += delta
            self.selected_item_index = max(2, min(self.selected_item_index, 33))

    def buttons_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.items_selector.mm_rect.collidepoint(
                mouse_pos()) and self.switch_locker == True:
            self.switch_locker = False
            self.switch({'from': 'level_builder', 'to': f'{self.from_where}'})
        if event.type == pygame.MOUSEBUTTONDOWN and self.items_selector.rect.collidepoint(mouse_pos()):
            new_index = self.items_selector.on_click(mouse_pos(), mouse_buttons())
            self.selected_item_index = new_index if new_index else self.selected_item_index
        if event.type == pygame.MOUSEBUTTONDOWN and self.items_selector.sv_rect.collidepoint(
                mouse_pos()) and self.switch_locker and len(self.generate_grid()[0]['terrain']) != 0:
            self.switch_locker = False
            self.switch({'from': 'level_builder', 'to': 'save_menu'})

    def layout_add(self):
        if not self._is_layout_clickable():
            return

        chosen_cell = self.get_cell_coordinates()
        selected = self.level_builder_map[self.selected_item_index]

        if selected['type'] == 'tile':
            if chosen_cell == self.previously_selected_cell:
                return

            tile = self.layout_elements.get(chosen_cell)
            if tile:
                tile.add_object(self.selected_item_index)
            else:
                self.layout_elements[chosen_cell] = LayoutObject(self.level_builder_map, self.selected_item_index)

            self.adjust_tile_correlation(chosen_cell)
            self.previously_selected_cell = chosen_cell

        else:
            if not self.object_spawn_timer.is_active():
                groups = [self.layout_objects, self.background_object] \
                    if selected.get('style') == 'palm_bg' \
                    else [self.layout_objects, self.foreground_object]

                LayoutMovableObject(
                    pos=mouse_pos(),
                    frames=self.animation_assets[self.selected_item_index]['frames'],
                    tile_id=self.selected_item_index,
                    starting_point=self.starting_point,
                    group=groups
                )
                self.object_spawn_timer.activate()

    def adjust_tile_correlation(self, cell_pos):
        offsets_map = {
            '1': (0, -1), '2': (1, -1), '3': (1, 0), '4': (1, 1),
            '5': (0, 1), '6': (-1, 1), '7': (-1, 0), '8': (-1, -1)
        }

        offset_x, offset_y = cell_pos
        half = 1

        for dx in range(-half, half + 1):
            for dy in range(-half, half + 1):
                cell = (offset_x + dx, offset_y + dy)
                if cell not in self.layout_elements:
                    continue

                cell_data = self.layout_elements[cell]
                cell_data.terrain_neighbors = []
                cell_data.water_on_top = False

                for name, (nx, ny) in offsets_map.items():
                    neighbor = (cell[0] + nx, cell[1] + ny)
                    if neighbor not in self.layout_elements:
                        continue

                    neighbor_data = self.layout_elements[neighbor]

                    if name == '1' and cell_data.has_water and neighbor_data.has_water:
                        cell_data.water_on_top = True

                    if neighbor_data.has_terrain:
                        cell_data.terrain_neighbors.append(name)

    def _is_layout_clickable(self):
        if not mouse_buttons()[0] or self.object_drag_active:
            return False
        pos = mouse_pos()
        return not (
                self.items_selector.rect.collidepoint(pos) or
                self.items_selector.mm_rect.collidepoint(pos) or
                self.items_selector.sv_rect.collidepoint(pos)
        )

    def layout_remove(self):
        if not mouse_buttons()[2] or self.items_selector.rect.collidepoint(mouse_pos()):
            return

        obj = self.mouse_which_object()
        if obj and self.level_builder_map.get(obj.tile_id, {}).get('style') not in ('player', 'sky'):
            obj.kill()
            return

        current_cell = self.get_cell_coordinates()
        tile = self.layout_elements.get(current_cell)

        if tile:
            tile.remove_object(self.selected_item_index)
            if tile.is_empty:
                del self.layout_elements[current_cell]
            self.adjust_tile_correlation(current_cell)

    def update_object_drag(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
            self._start_object_drag(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
            self._end_object_drag()

    def _start_object_drag(self, pos):
        for entity in self.layout_objects:
            if entity.rect.collidepoint(pos):
                entity.start_drag()
                self.object_drag_active = True
                break

    def _end_object_drag(self):
        for entity in self.layout_objects:
            if entity.selected:
                entity.end_drag(self.starting_point)
                self.object_drag_active = False
                break

    def draw_grid_lines(self):
        columns = self.window_size[0] // tile_size
        rows = self.window_size[1] // tile_size

        offset_x = self.starting_point.x - floor(self.starting_point.x / tile_size) * tile_size
        offset_y = self.starting_point.y - floor(self.starting_point.y / tile_size) * tile_size

        self.grid_lines_surface.fill('green')

        for col in range(columns + 1):
            x = offset_x + col * tile_size
            pygame.draw.line(self.grid_lines_surface, 'black', (x, 0), (x, self.window_size[1]))

        for row in range(rows + 1):
            y = offset_y + row * tile_size
            pygame.draw.line(self.grid_lines_surface, 'black', (0, y), (self.window_size[0], y))

        self.display_surface.blit(self.grid_lines_surface, (0, 0))

    def draw_level_layout(self):
        self.background_object.draw(self.display_surface)

        animated_types = {
            'water': (3, self.water_bottom),
            'coin': lambda tile: tile.coin,
            'enemy': lambda tile: tile.enemy
        }

        static_tiles = {
            'terrain': lambda tile: self._get_terrain_surface(tile),
            'bricks_fg': self.bricks_fg,
            'bricks_bg': self.bricks_bg,
            'platform': self.platform,
            'interract_info': self.interract_info,
            'finish_info': self.finish_info,
            'sign_bottom': self.sign_bottom,
            'sign_top': self.sign_top,
            'sign_left': self.sign_left,
            'sign_right': self.sign_right
        }

        for cell_pos, tile in self.layout_elements.items():
            pos = self.starting_point + vector(cell_pos) * tile_size

            if tile.has_water:
                if tile.water_on_top:
                    self.display_surface.blit(self.water_bottom, pos)
                else:
                    self._draw_animated(3, pos)

            for attr, surf in static_tiles.items():
                if getattr(tile, f'has_{attr}', False):
                    surface = surf(tile) if callable(surf) else surf
                    self.display_surface.blit(surface, pos)

            if tile.coin:
                self._draw_animated(tile.coin, pos, center=True)

            if tile.enemy:
                self._draw_animated(tile.enemy, pos, midbottom=True)

        self.foreground_object.draw(self.display_surface)

    def display_scenery(self, dt):
        self.display_surface.fill('#cce7ff')
        y = self.sky_handle.rect.centery
        height = self.window_size[1]

        if y > 0:
            self._draw_horizon_lines(y)
            self.render_clouds(dt, y)

        if 0 < y < height:
            self._draw_sea(y, height)
        elif y < 0:
            self.display_surface.fill('#a8c9a1')

    def _draw_horizon_lines(self, y):
        w = self.window_size[0]
        pygame.draw.rect(self.display_surface, '#f6d6bd', pygame.Rect(0, y - 10, w, 10))
        pygame.draw.rect(self.display_surface, '#f6d6bd', pygame.Rect(0, y - 16, w, 4))
        pygame.draw.rect(self.display_surface, '#f6d6bd', pygame.Rect(0, y - 20, w, 2))

    def _draw_sea(self, y, height):
        w = self.window_size[0]
        pygame.draw.rect(self.display_surface, '#a8c9a1', pygame.Rect(0, y, w, height))
        pygame.draw.line(self.display_surface, '#f5f1de', (0, y), (w, y), 3)

    def render_clouds(self, dt, horizon_y):
        for cloud in self.layout_clouds:
            cloud_surf = cloud.get('surf')
            cloud_pos = cloud.get('pos')
            cloud_speed = cloud.get('speed', 0)

            if not cloud_surf or not cloud_pos:
                continue

            cloud_pos[0] -= cloud_speed * dt
            draw_x = cloud_pos[0]
            draw_y = horizon_y - cloud_pos[1]

            self.display_surface.blit(cloud_surf, (draw_x, draw_y))

    def add_clouds(self, event):
        if event.type != self.cloud_spawn_time:
            return

        self._spawn_cloud()
        self._cleanup_clouds()

    def _spawn_cloud(self):
        surf = choice(self.cloud_surface)
        if randint(0, 4) < 2:
            surf = pygame.transform.scale2x(surf)

        x = self.window_size[0] + randint(50, 100)
        y = randint(0, self.window_size[1])
        speed = randint(20, 50)

        self.layout_clouds.append({'surf': surf, 'pos': [x, y], 'speed': speed})

    def _cleanup_clouds(self):
        self.layout_clouds = [
            cloud for cloud in self.layout_clouds if cloud['pos'][0] > -400
        ]

    def startup_clouds(self):
        for _ in range(20):
            cloud = self._generate_cloud()
            self.layout_clouds.append(cloud)

    def _generate_cloud(self):
        surf = choice(self.cloud_surface)
        if randint(0, 4) < 2:
            surf = pygame.transform.scale2x(surf)

        x = randint(0, self.window_size[0])
        y = randint(0, self.window_size[1])
        speed = randint(20, 50)

        return {'surf': surf, 'pos': [x, y], 'speed': speed}

    def _draw_animated(self, anim_id, pos, center=False, midbottom=False):
        frames = self.animation_assets[anim_id]['frames']
        index = int(self.animation_assets[anim_id]['frame index'])
        surf = frames[index]

        if center:
            rect = surf.get_rect(center=(pos[0] + tile_size // 2, pos[1] + tile_size // 2))
        elif midbottom:
            rect = surf.get_rect(midbottom=(pos[0] + tile_size // 2, pos[1] + tile_size))
        else:
            rect = surf.get_rect(topleft=pos)

        self.display_surface.blit(surf, rect)

    def _get_terrain_surface(self, tile):
        terrain_key = ''.join(tile.terrain_neighbors)
        key = terrain_key if terrain_key in self.soil_tiles else '0'
        return self.soil_tiles[key]

    def selected_object_preview(self):
        if self._is_mouse_over_ui():
            return

        selected_object = self.mouse_which_object()

        if selected_object:
            rect = selected_object.rect.inflate(10, 10)
            self._draw_selection_outline(rect)
        else:
            tile_type = self.level_builder_map[self.selected_item_index]['type']
            surf = self.preview_surfs[self.selected_item_index].copy()
            surf.set_alpha(200)

            if tile_type == 'tile':
                cell = self.get_cell_coordinates()
                rect = surf.get_rect(topleft=self.starting_point + vector(cell) * tile_size)
            else:
                rect = surf.get_rect(center=mouse_pos())

            self.display_surface.blit(surf, rect)

    def _is_mouse_over_ui(self):
        pos = mouse_pos()
        return (
                self.items_selector.rect.collidepoint(pos) or
                self.items_selector.mm_rect.collidepoint(pos) or
                self.items_selector.sv_rect.collidepoint(pos)
        )

    def _draw_selection_outline(self, rect):
        color = 'black'
        width = 3
        size = 15

        pygame.draw.lines(self.display_surface, color, False,
                          [(rect.left, rect.top + size), rect.topleft, (rect.left + size, rect.top)], width)
        pygame.draw.lines(self.display_surface, color, False,
                          [(rect.right - size, rect.top), rect.topright, (rect.right, rect.top + size)], width)
        pygame.draw.lines(self.display_surface, color, False,
                          [(rect.right - size, rect.bottom), rect.bottomright, (rect.right, rect.bottom - size)], width)
        pygame.draw.lines(self.display_surface, color, False,
                          [(rect.left, rect.bottom - size), rect.bottomleft, (rect.left + size, rect.bottom)], width)

    def run(self, dt):
        self.event_loop()
        self.update_frames(dt)
        self.layout_objects.update(dt)
        self.object_spawn_timer.update()
        self.display_surface.fill('gray')
        self.display_scenery(dt)
        self.draw_level_layout()
        self.draw_grid_lines()
        self.selected_object_preview()
        self.items_selector.render(self.selected_item_index)


class LayoutObject:
    def __init__(self, layout_map, tile_id=None, offset=vector()):
        self.layout_map = layout_map

        self.has_terrain = False
        self.terrain_neighbors = []

        self.has_water = False
        self.water_on_top = False

        self.has_platform = False

        self.has_interract_info = False
        self.has_finish_info = False
        self.has_sign_bottom = False
        self.has_sign_top = False
        self.has_sign_left = False
        self.has_sign_right = False

        self.has_bricks_fg = False
        self.has_bricks_bg = False

        self.coin = None
        self.enemy = None
        self.objects = []
        self.is_empty = True

        if tile_id is not None:
            self.add_object(tile_id, offset)

    def add_object(self, tile_id, offset=vector()):
        style = self._get_style(tile_id)

        if style in self._style_flags():
            setattr(self, self._style_flags()[style], True)
        elif style in self._style_fields():
            setattr(self, self._style_fields()[style], tile_id)
        else:
            if (tile_id, offset) not in self.objects:
                self.objects.append((tile_id, offset))

        self.is_empty = False

    def remove_object(self, tile_id):
        style = self._get_style(tile_id)

        if style in self._style_flags():
            setattr(self, self._style_flags()[style], False)
        elif style in self._style_fields():
            setattr(self, self._style_fields()[style], None)

        self._check_content()

    def _check_content(self):
        self.is_empty = not (self.has_terrain or self.has_water or self.coin or self.enemy)

    def _get_style(self, tile_id):
        return self.layout_map[tile_id]['style']

    def _style_flags(self):
        return {
            'terrain': 'has_terrain',
            'water': 'has_water',
            'platform': 'has_platform',
            'bricks_fg': 'has_bricks_fg',
            'bricks_bg': 'has_bricks_bg',
            'interract_info': 'has_interract_info',
            'finish_info': 'has_finish_info',
            'sign_bottom': 'has_sign_bottom',
            'sign_top': 'has_sign_top',
            'sign_left': 'has_sign_left',
            'sign_right': 'has_sign_right',
        }

    def _style_fields(self):
        return {
            'coin': 'coin',
            'enemy': 'enemy'
        }

    def get_water(self):
        return 'bottom' if self.water_on_top else 'top'

    def get_terrain(self):
        return ''.join(self.terrain_neighbors)


class LayoutMovableObject(pygame.sprite.Sprite):
    def __init__(self, pos, frames, tile_id, starting_point, group, is_input=False):
        super().__init__(group)
        self.tile_id = tile_id
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[0]

        self.rect = self._init_rect(pos, is_input)

        self.distance_to_starting_point = vector(self.rect.topleft) - starting_point
        self.selected = False
        self.mouse_offset = vector()

    def _init_rect(self, pos, is_input):
        if is_input:
            return self.image.get_rect(topleft=pos)
        return self.image.get_rect(center=pos)

    def start_drag(self):
        self.selected = True
        self.mouse_offset = vector(mouse_pos()) - vector(self.rect.topleft)

    def drag(self):
        if self.selected:
            self.rect.topleft = mouse_pos() - self.mouse_offset

    def end_drag(self, starting_point):
        self.selected = False
        self.distance_to_starting_point = vector(self.rect.topleft) - starting_point

    def animate(self, dt):
        self.frame_index = (self.frame_index + 8 * dt) % len(self.frames)
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def layout_pos(self, starting_point):
        self.rect.topleft = starting_point + self.distance_to_starting_point

    def update(self, dt):
        self.animate(dt)
        self.drag()
