import sys
from os import path
from f_read import *
from pygame.mouse import get_pos as mouse_pos
from pygame.math import Vector2 as vector
from pygame.image import load

from entities import EntityBase, AnimatedEntity, Treasure, FXParticle, SolidBlock, Platform, SpikeTrap, Pig, Cannon, SkyCloud, Saw, Mace, Player
from timer import Timer

from random import choice, randint

script_directory = path.dirname(path.realpath(__file__))


class GameLevel:
	def __init__(self, grid, switch, assets, audio, change_coins, change_health, player_dead, change_diamonds, get_score, get_diamonds, player_alive, get_level_from_where):
		self.display_surface = pygame.display.get_surface()

		self.get_level_from_where = get_level_from_where
		self.switch = switch
		self.switch_locker = True

		self.player_dead = player_dead
		self.player_attack = False
		self.player_alive = player_alive
		self.window_size = self.display_surface.get_size()

		self.all_entities = CameraRig()
		self.treasure_entities = pygame.sprite.Group()
		self.collision_entities = pygame.sprite.Group()
		self.semi_colidable_entities = pygame.sprite.Group()
		self.cannon_entities = pygame.sprite.Group()
		self.cannonball_destroy = pygame.sprite.Group()
		self.mortal_enemy_collisions = pygame.sprite.Group()
		self.damage_entities = pygame.sprite.Group()
		self.damage_entities_cannonball = pygame.sprite.Group()
		self.water_damage = pygame.sprite.Group()
		self.knockback_entities = pygame.sprite.Group()

		self.startup_level(grid, assets, audio['jump'])

		self.change_coins = change_coins
		self.change_health = change_health
		self.change_diamonds = change_diamonds
		self.buttons = Buttons_lvl()
		self.get_score = get_score
		self.get_diamonds = get_diamonds
		self.additional_surf = pygame.Surface(self.window_size)
		self.additional_surf.fill('green')
		self.additional_surf.set_colorkey('green')
		self.alpha = 0
		self.additional_surf.set_alpha(self.alpha)
		self.score_menu = Score_menu(self.get_score, self.additional_surf)
		self.paused = False
		self.after_pause_timer = Timer(700)

		self.level_borders = {
		'left': -self.window_size[0],
		'right': sorted(list(grid['terrain'].keys()), key = lambda pos: pos[0])[-1][0] + 1000
		}
		self.red_line = sorted(list(grid['terrain'].keys()), key=lambda pos: pos[1])[-1][1] + 100

		self.cloud_frames = assets['clouds']
		self.particle_frames = assets['particle']
		self.cloud_spam_timer = pygame.USEREVENT + 2
		pygame.time.set_timer(self.cloud_spam_timer, 2000)
		self.update_clouds()
		self.complete = False
		self.grid = grid

		self.background_music = audio['music']
		self.background_music.set_volume(0.1)

		self.treasure_sound = audio['treasure']
		self.treasure_sound.set_volume(0.1)

		self.damage_sound = audio['damage']
		self.damage_sound.set_volume(0.1)

	def startup_level(self, grid, assets, jump_sound):
		layer_entity_map = {
			'terrain': lambda pos, data: EntityBase(pos, assets['soil'][data],
													[self.all_entities, self.collision_entities, self.cannonball_destroy]),
			'water': lambda pos, data: AnimatedEntity(assets['water top'], pos,
													  [self.all_entities, self.water_damage], 4)
			if data == 'top' else EntityBase(pos, assets['water bottom'], [self.all_entities, self.water_damage], 4),
			'platforms': lambda pos, _: Platform(pos, assets['platforms'],
												 [self.all_entities, self.semi_colidable_entities]),
			'bricks fg': lambda pos, _: EntityBase(pos, assets['bricks fg'],
												   [self.all_entities, self.collision_entities, self.cannonball_destroy]),
			'bricks bg': lambda pos, _: EntityBase(pos, assets['bricks bg'], [self.all_entities]),
			'interract_info': lambda pos, _: EntityBase(pos, assets['interract_info'], [self.all_entities], 3),
			'finish_info': lambda pos, _: EntityBase(pos, assets['finish_info'], [self.all_entities], 3),
			'sign bottom': lambda pos, _: EntityBase(pos, assets['sign bottom'], [self.all_entities], 3),
			'sign top': lambda pos, _: EntityBase(pos, assets['sign top'], [self.all_entities], 3),
			'sign left': lambda pos, _: EntityBase(pos, assets['sign left'], [self.all_entities], 3),
			'sign right': lambda pos, _: EntityBase(pos, assets['sign right'], [self.all_entities], 3),
		}

		for layer_name, layer in grid.items():
			for pos, data in layer.items():
				if layer_name in layer_entity_map:
					layer_entity_map[layer_name](pos, data)

				match data:
					case 0:
						self.player = Player(pos, assets['player'], self.all_entities, self.collision_entities,
											 jump_sound, self.player_dead, self.semi_colidable_entities,
											 self.knockback_entities)
					case 1:
						self.horizon_y = pos[1]
						self.all_entities.horizon_y = pos[1]
					case 4:
						Treasure('gold', assets['golden coin'], pos, [self.all_entities, self.treasure_entities])
					case 5:
						Treasure('silver', assets['silver coin'], pos, [self.all_entities, self.treasure_entities])
					case 6:
						Treasure('diamond', assets['diamond'], pos, [self.all_entities, self.treasure_entities])
					case 7:
						SpikeTrap(assets['spikes'], pos, [self.all_entities, self.damage_entities])
					case 8:
						Pig(assets['pig'], pos,
							[self.all_entities, self.mortal_enemy_collisions, self.knockback_entities],
							self.collision_entities)
					case 9 | 10:
						Cannon(
							orientation='left' if data == 9 else 'right',
							assets=assets['cannon'],
							pos=pos,
							group=[self.all_entities, self.collision_entities, self.cannon_entities],
							cannonball_surf=assets['cannonball'],
							damage_entities=self.damage_entities_cannonball
						)
					case 11 | 12 | 13 | 14:
						key = ['small_fg', 'large_fg', 'left_fg', 'right_fg'][data - 11]
						AnimatedEntity(assets['palms'][key], pos, self.all_entities)
						offset = vector(50, 0) if data == 14 else vector()
						SolidBlock(pos + offset, (76, 50), self.collision_entities)
					case 15 | 16 | 17 | 18:
						key = ['small_bg', 'large_bg', 'left_bg', 'right_bg'][data - 15]
						AnimatedEntity(assets['palms'][key], pos, self.all_entities, 3)
					case 21 | 22 | 23 | 24:
						directions = ['bottom', 'top', 'left', 'right']
						Saw(orientation=directions[data - 21], assets=assets['saw'], pos=pos,
							group=[self.all_entities, self.damage_entities])
					case 32:
						radius = 100
						for rad in range(0, radius, 20):
							Mace(assets=assets['mace_chain'], pos=pos, group=[self.all_entities], radius=rad)
						Mace(assets=assets['mace'], pos=pos, group=[self.all_entities, self.damage_entities],
							 radius=radius)
					case 33:
						Treasure('heal_potion', assets['heal_potion'], pos, [self.all_entities, self.treasure_entities])

		for entity in self.cannon_entities:
			entity.player = self.player

	def player_under_red_line(self):
		if self.player.pos[1] >= self.red_line and not self.player.immortality_timer.is_active() and self.player.player_dead() == False:
			self.damage_sound.play()
			self.player.get_hit()
			self.change_health(100)

	def update_player_hit(self):
		collision_entities = pygame.sprite.spritecollide(self.player, self.damage_entities, False, pygame.sprite.collide_mask)
		if collision_entities and not self.player.immortality_timer.is_active() and self.player.player_dead() == False:
			self.damage_sound.play()
			self.player.get_hit()
			self.change_health(20)
			
	def update_treasures(self):
		collided_treasures = pygame.sprite.spritecollide(self.player, self.treasure_entities, True)
		for entity in collided_treasures:
			self.treasure_sound.play()
			FXParticle(self.particle_frames, entity.rect.center, self.all_entities)
			if entity.treasure_type == "gold":
				self.change_coins(50)
			elif entity.treasure_type == "silver":
				self.change_coins(10)
			elif entity.treasure_type == "diamond":
				self.change_diamonds(1)
			elif entity.treasure_type == 'heal_potion':
				self.change_health(-20)

	def update_hit_cannonball(self):
		collision_entities = pygame.sprite.spritecollide(self.player, self.damage_entities_cannonball, True, pygame.sprite.collide_mask)
		pygame.sprite.groupcollide(self.cannonball_destroy, self.damage_entities_cannonball, False, True)
		if collision_entities and not self.player.immortality_timer.is_active() and self.player.player_dead() == False and self.player.animation_name != "attack":
			self.damage_sound.play()
			self.player.get_hit()
			self.change_health(20)

	def update_water_hit(self):
		collision_entities = pygame.sprite.spritecollide(self.player, self.water_damage, False, pygame.sprite.collide_mask)
		if collision_entities and not self.player.immortality_timer.is_active() and self.player.player_dead() == False:
			self.damage_sound.play()
			self.player.set_drowning(True)
			self.change_health(20)
			self.player.immortality_timer.activate()
		elif collision_entities and self.player.player_dead() == False:
			self.player.set_drowning(True)
		else:
			self.player.set_drowning(False)

	def menu_click(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.mm_rect.collidepoint(mouse_pos()) and self.switch_locker == True:
			self.switch_locker = False
			self.switch({'from':  'level', 'to': f'{self.get_level_from_where()}'})
		if event.type == pygame.MOUSEBUTTONDOWN and self.buttons.pause_rect.collidepoint(mouse_pos()) and self.switch_locker == True and self.paused:
			self.paused = False
			self.after_pause_timer.activate()
		elif event.type == pygame.MOUSEBUTTONDOWN and self.buttons.pause_rect.collidepoint(mouse_pos()) and self.switch_locker == True and self.paused == False:
			self.paused = True

	def score_menu_click(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN and self.score_menu.restart_rect.collidepoint(mouse_pos()) and self.switch_locker == True:
			self.switch_locker = False
			self.switch({'from':  'level', 'to': 'level'}, self.grid)
		if event.type == pygame.MOUSEBUTTONDOWN and self.score_menu.levels_rect.collidepoint(mouse_pos()) and self.switch_locker == True and self.paused == False:
			self.switch_locker = False
			self.switch({'from':  'level', 'to': 'level_menu'})
		if event.type == pygame.MOUSEBUTTONDOWN and self.score_menu.levels_rect.collidepoint(mouse_pos()) and self.switch_locker == True and self.paused:
			self.paused = False
			self.after_pause_timer.activate()

	def mortal_enemy_collision(self):
		mortal_collided = pygame.sprite.spritecollide(self.player, self.mortal_enemy_collisions, False, pygame.sprite.collide_mask)
		if mortal_collided:
			for enemy in mortal_collided:
				enemy_center = enemy.rect.centery
				enemy_top = enemy.rect.top
				player_bottom = self.player.rect.bottom
				if enemy_top < player_bottom < enemy_center and self.player.animation_name == 'fall' :
					self.player.direction.y -= 3.5
					enemy.death_timer.activate()
					enemy.dead = True
				elif not enemy_top < player_bottom < enemy_center and not self.player.immortality_timer.is_active():
					self.damage_sound.play()
					self.player.get_hit()
					self.change_health(20)

	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.switch_locker == True:
				self.switch_locker = False
				self.switch({'from':  'level', 'to': f'{self.get_level_from_where()}'})
			if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
				if self.paused:
					self.paused = not self.paused
					self.after_pause_timer.activate()
				else:
					self.paused = not self.paused
			if event.type == self.cloud_spam_timer:
				cloud_surf = choice(self.cloud_frames)
				if randint(0, 5) > 3:
					cloud_surf = pygame.transform.scale2x(cloud_surf)

				spawn_x = self.level_borders['right'] + randint(200, 500)
				spawn_y = self.horizon_y - randint(-50, 800)

				SkyCloud(
					pos=(spawn_x, spawn_y),
					surf=cloud_surf,
					group=self.all_entities,
					deletion_limit=self.level_borders['left']
				)

			self.menu_click(event)
			if self.complete or self.player_dead() or self.paused:
				self.score_menu_click(event)

	def update_clouds(self):
		for _ in range(40):
			cloud_surf = choice(self.cloud_frames)
			if randint(0, 5) > 3:
				cloud_surf = pygame.transform.scale2x(cloud_surf)

			spawn_x = randint(self.level_borders['left'], self.level_borders['right'])
			spawn_y = self.horizon_y - randint(-50, 600)

			SkyCloud(
				pos=(spawn_x, spawn_y),
				surf=cloud_surf,
				group=self.all_entities,
				deletion_limit=self.level_borders['left']
			)

	def transition(self):
		self.alpha = max(0, min(self.alpha, 255))
		self.alpha += 10
		self.additional_surf.set_alpha(self.alpha)

	def transition_out(self):
		self.alpha = max(0, min(self.alpha, 255))
		self.alpha -= 10
		self.additional_surf.set_alpha(self.alpha)

	def run(self, dt):
		self.event_loop()
		if self.paused:
			self.transition()
			self.score_menu.display(False, self.get_diamonds, True)
		else:
			self.all_entities.update(dt)
			self.update_player_hit()
			self.update_hit_cannonball()
			self.update_water_hit()
		if self.after_pause_timer.is_active():
			self.transition_out()
		self.update_treasures()
		self.mortal_enemy_collision()
		self.player_under_red_line()

		self.display_surface.fill('#cce7ff')
		self.all_entities.manage_layers(self.player)
		if self.paused:
			self.buttons.display(True)
		else:
			self.buttons.display(False)
		self.display_surface.blit(self.additional_surf, (0, 0))
		self.after_pause_timer.update()
		if self.player_dead():
			self.transition()
			self.score_menu.display(False, self.get_diamonds)
		if self.complete:
			self.transition()
			self.score_menu.display(True)
			self.player.speed = 0

class CameraRig(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.window_size = self.display_surface.get_size()
		self.offset = vector()

	def render_scenery(self):
		horizon_pos = self.horizon_y - self.offset.y
		if horizon_pos < 0:
			self.display_surface.fill('#a8c9a1')
		elif horizon_pos < self.window_size[1]:
			sea_rect = pygame.Rect(0, horizon_pos, self.window_size[0], self.window_size[1] - horizon_pos)
			pygame.draw.rect(self.display_surface, '#a8c9a1', sea_rect)
			pygame.draw.rect(self.display_surface, '#f6d6bd', (0, horizon_pos - 10, self.window_size[0], 10))
			pygame.draw.rect(self.display_surface, '#f6d6bd', (0, horizon_pos - 16, self.window_size[0], 4))
			pygame.draw.rect(self.display_surface, '#f6d6bd', (0, horizon_pos - 20, self.window_size[0], 2))
			pygame.draw.line(self.display_surface, '#f5f1de', (0, horizon_pos), (self.window_size[0], horizon_pos), 3)

	def manage_layers(self, player):
		self.offset.x = player.rect.centerx - self.window_size[0] / 2
		self.offset.y = player.rect.centery - self.window_size[1] / 2

		for entity in self:
			if entity.z == 1:
				offset_rect = entity.rect.copy()
				offset_rect.center -= self.offset
				self.display_surface.blit(entity.image, offset_rect)

		self.render_scenery()

		for layer in range(2, 6):
			for entity in self:
				if entity.z == layer:
					offset_rect = entity.rect.copy()
					offset_rect.center -= self.offset
					self.display_surface.blit(entity.image, offset_rect)

class Buttons_lvl:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.window_size = self.display_surface.get_size()
		self.multiplayer_x = self.window_size[0] / 1280
		self.multiplayer_y = self.window_size[1] / 720
		self.create_buttons()


	def create_buttons(self):
		def sx(value):
			return int(value * self.multiplayer_x)
		def sy(value):
			return int(value * self.multiplayer_y)
		mm_size = sx(45)
		mm_margin = sx(6)
		mm_topleft = (self.window_size[0] - mm_size - mm_margin, mm_margin)
		self.mm_rect = pygame.Rect(mm_topleft, (mm_size, mm_size))
		self.image = load(path.join(script_directory, 'graphics', 'menus', 'main_menu_button.png')).convert_alpha()
		self.image = pygame.transform.scale(self.image, (mm_size, mm_size))
		self.pause_rect = pygame.Rect(vector(mm_topleft) - (mm_size + mm_margin, 0), (mm_size, mm_size))
		self.p_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'pause_button.png')).convert_alpha()
		self.p_image = pygame.transform.scale(self.p_image, (mm_size, mm_size))
		self.r_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'release_pause_button.png')).convert_alpha()
		self.r_image = pygame.transform.scale(self.r_image, (mm_size, mm_size))


	def display(self, paused = False):
		self.display_surface.blit(self.image, self.mm_rect.topleft)
		if paused:
			self.display_surface.blit(self.r_image, self.pause_rect.topleft)
		else:
			self.display_surface.blit(self.p_image, self.pause_rect.topleft)

class Score_menu:
	def __init__(self, get_score, surf):
		self.display_surface = surf
		self.get_score = get_score
		self.window_size = self.display_surface.get_size()
		self.multiplayer_x = self.window_size[0] / 1280
		self.multiplayer_y = self.window_size[1] / 720
		self.create_buttons()



	def create_buttons(self):
		def sx(value):
			return int(value * self.multiplayer_x)
		def sy(value):
			return int(value * self.multiplayer_y)
		topleft = (self.window_size[0] / 2 - sx(360) / 2, sy(120))
		self.tittle_rect = pygame.Rect(topleft, (sx(360), sy(100)))
		self.image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'win.png')).convert_alpha()
		self.image = pygame.transform.scale(self.image, (sx(360), sy(100)))
		self.image_go = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'game_over.png')).convert_alpha()
		self.image_go = pygame.transform.scale(self.image_go, (sx(360), sy(100)))
		self.image_paused = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'paused.png')).convert_alpha()
		self.image_paused = pygame.transform.scale(self.image_paused, (sx(360), sy(100)))
		self.score_rect = pygame.Rect(vector(topleft) + (sx(0), sy(110)), (sx(360), sy(240)))
		self.score_rect_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'score_back.png')).convert_alpha()
		self.score_rect_image = pygame.transform.scale(self.score_rect_image, (sx(360), sy(240)))
		self.diamonds0_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', '0diamond_score.png')).convert_alpha()
		self.diamonds0_image = pygame.transform.scale(self.diamonds0_image, (sx(360), sy(240)))
		self.diamonds1_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', '1diamond_score.png')).convert_alpha()
		self.diamonds1_image = pygame.transform.scale(self.diamonds1_image, (sx(360), sy(240)))
		self.diamonds2_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', '2diamond_score.png')).convert_alpha()
		self.diamonds2_image = pygame.transform.scale(self.diamonds2_image, (sx(360), sy(240)))
		self.buttons_rect = pygame.Rect(vector(topleft) + (sx(0), sy(360)), (sx(360), sy(120)))
		self.buttons_rect_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'buttons_back.png')).convert_alpha()
		self.buttons_rect_image = pygame.transform.scale(self.buttons_rect_image, (sx(360), sy(120)))
		self.restart_rect = pygame.Rect(vector(topleft) + (sx(50), sy(396)), (sx(120), sy(46)))
		self.restart_rect_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'restart.png')).convert_alpha()
		self.restart_rect_image = pygame.transform.scale(self.restart_rect_image, (sx(120), sy(46)))
		self.levels_rect = pygame.Rect(vector(topleft) + (sx(190), sy(396)), (sx(120), sy(46)))
		self.levels_rect_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'levels.png')).convert_alpha()
		self.levels_rect_image = pygame.transform.scale(self.levels_rect_image, (sx(120), sy(46)))
		self.resume_rect_image = load(path.join(script_directory, 'graphics', 'menus', 'score_menu', 'resume.png')).convert_alpha()
		self.resume_rect_image = pygame.transform.scale(self.resume_rect_image, (sx(120), sy(46)))
		self.font = pygame.font.Font(path.join(script_directory, 'graphics', 'ui', 'ARCADEPI.ttf'), sx(18))



	def display(self, level_complete, get_diamonds = None, paused = False):
		def sx(value):
			return int(value * self.multiplayer_x)
		def sy(value):
			return int(value * self.multiplayer_y)
		self.score_surf = self.font.render(f"Score: {self.get_score()}", False, '#33323d')
		self.score_surf_rect = self.score_surf.get_rect(topleft=(vector(self.window_size[0] / 2 - sx(360) / 2, sy(120)) + (sx(120), sy(255))))
		self.display_surface.blit(self.buttons_rect_image, self.buttons_rect.topleft)
		if level_complete:
			self.display_surface.blit(self.image, self.tittle_rect.topleft)
			self.display_surface.blit(self.score_rect_image, self.score_rect.topleft)
		else:
			if paused:
				self.display_surface.blit(self.image_paused, self.tittle_rect.topleft)
			else:
				self.display_surface.blit(self.image_go, self.tittle_rect.topleft)
			if get_diamonds() == 0:
				self.display_surface.blit(self.diamonds0_image, self.score_rect.topleft)
			elif get_diamonds() == 1:
				self.display_surface.blit(self.diamonds1_image, self.score_rect.topleft)
			if get_diamonds() == 2:
				self.display_surface.blit(self.diamonds2_image, self.score_rect.topleft)
		self.display_surface.blit(self.restart_rect_image, self.restart_rect.topleft)
		if paused:
			self.display_surface.blit(self.resume_rect_image, self.levels_rect.topleft)
		else:
			self.display_surface.blit(self.levels_rect_image, self.levels_rect.topleft)
		self.display_surface.blit(self.score_surf, self.score_surf_rect)
