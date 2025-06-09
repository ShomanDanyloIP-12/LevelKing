import pygame
from pygame.math import Vector2 as vector
from timer import Timer
from math import sin, cos, radians
from random import choice, randint


class EntityBase(pygame.sprite.Sprite):
	def __init__(self, pos, surf, group, layer=5):
		super().__init__(group)
		self.image = surf
		self.z = layer
		self.rect = self.image.get_rect(topleft = pos)


class AnimatedEntity(EntityBase):
	def __init__(self, assets, pos, group, layer=5):
		self.current_frame = 0
		self.frame_assets = assets
		super().__init__(pos, self._get_current_frame(), group, layer)

	def update(self, dt):
		self.animate(dt)

	def animate(self, dt):
		self.current_frame += 8 * dt
		if self.current_frame >= len(self.frame_assets):
			self.current_frame = 0
		self.image = self._get_current_frame()

	def _get_current_frame(self):
		return self.frame_assets[int(self.current_frame)]


class Treasure(AnimatedEntity):
	def __init__(self, treasure_type, assets, pos, group):
		super().__init__(assets, pos, group)
		self.rect = self.image.get_rect(center = pos)
		self.treasure_type = treasure_type


class FXParticle(AnimatedEntity):
	def __init__(self, assets, pos, group):
		super().__init__(assets, pos, group)
		self.rect = self.image.get_rect(center=pos)

	def animate(self, dt):
		self._advance_frame(dt)

	def _advance_frame(self, dt):
		self.current_frame += 8 * dt
		index = int(self.current_frame)

		if index < len(self.frame_assets):
			self.image = self.frame_assets[index]
		else:
			self.kill()


class SolidBlock(EntityBase):
	def __init__(self, pos, size, group):
		surf = pygame.Surface(size)
		super().__init__(pos, surf, group)


class SkyCloud(EntityBase):
	def __init__(self, pos, surf, group, deletion_limit):
		super().__init__(pos, surf, group, 1)
		self.deletion_limit = deletion_limit
		self._init_position()
		self._init_speed()

	def _init_position(self):
		self.pos = vector(self.rect.topleft)

	def _init_speed(self):
		self.speed = randint(20, 30)

	def update(self, dt):
		self._move_left(dt)
		self._destroy_if_out_of_bounds()

	def _move_left(self, dt):
		self.pos.x -= self.speed * dt
		self.rect.x = round(self.pos.x)

	def _destroy_if_out_of_bounds(self):
		if self.rect.right < self.deletion_limit:
			self.kill()


class SpikeTrap(EntityBase):
	def __init__(self, surf, pos, group):
		super().__init__(pos, surf, group)
		self.mask = pygame.mask.from_surface(self.image)


class Mace(EntityBase):
	def __init__(self, assets, pos, group, radius):
		self.center = (pos[0] + 64 / 2,pos[1] + 64 / 2)
		self.radius = radius
		self.speed = 120
		self.angle = 0

		y = self.center[1] + sin(radians(self.angle)) * self.radius
		x = self.center[0] + cos(radians(self.angle)) * self.radius

		super().__init__((x, y), assets, group)
		self.mask = pygame.mask.from_surface(self.image)

	def update(self, dt):
		self.angle += self.speed * dt
		y = self.center[1] + sin(radians(self.angle)) * self.radius
		x = self.center[0] + cos(radians(self.angle)) * self.radius
		self.rect.center = (x, y)


class Pig(EntityBase):
	def __init__(self, assets, pos, group, collision_entities):
		self.current_frame = 0
		self.frame_assets = assets
		self.orientation = 'right'
		self.direction = vector(choice((1, -1)), 0)
		self.orientation = 'left' if self.direction.x < 0 else 'right'

		surf = self.frame_assets[f'run_{self.orientation}'][self.current_frame]
		super().__init__(pos, surf, group)

		self.rect.bottom = self.rect.top + 64
		self.mask = pygame.mask.from_surface(self.image)

		self.speed = 150
		self.collision_entities = collision_entities

		self.pos = vector(self.rect.topleft)

		self.dead = False
		self.death_timer = Timer(100)

		if not self._is_on_ground():
			self.kill()

	def _is_on_ground(self):
		check_pos = self.rect.midbottom + vector(0, 10)
		return any(entity.rect.collidepoint(check_pos) for entity in self.collision_entities)

	def update(self, dt):
		self.animate(dt)
		self.move(dt)
		self.death_timer.update()
		self._handle_death()

	def animate(self, dt):
		frames = self.frame_assets[f'run_{self.orientation}']
		self.current_frame = (self.current_frame + 8 * dt) % len(frames)
		self.image = frames[int(self.current_frame)]
		self.mask = pygame.mask.from_surface(self.image)

		if self.death_timer.is_active():
			temp = self.mask.to_surface()
			temp.set_colorkey('black')
			self.image = temp

	def _handle_death(self):
		if self.dead:
			self.speed = 0
			if not self.death_timer.is_active():
				self.kill()

	def move(self, dt):
		if self.direction.x > 0:
			if self._wall_hit("right") or not self._has_floor("right"):
				self._turn_around("left")

		if self.direction.x < 0:
			if self._wall_hit("left") or not self._has_floor("left"):
				self._turn_around("right")

		self.pos.x += self.direction.x * self.speed * dt
		self.rect.x = round(self.pos.x)

	def _wall_hit(self, side):
		offset = vector(1, 0) if side == "right" else vector(-1, 0)
		check = self.rect.midright if side == "right" else self.rect.midleft
		return any(entity.rect.collidepoint(check + offset) for entity in self.collision_entities)

	def _has_floor(self, side):
		offset = vector(1, 1) if side == "right" else vector(-1, 1)
		check = self.rect.bottomright if side == "right" else self.rect.bottomleft
		return any(entity.rect.collidepoint(check + offset) for entity in self.collision_entities)

	def _turn_around(self, new_orientation):
		self.direction.x *= -1
		self.orientation = new_orientation

class Platform(EntityBase):
	def __init__(self, pos, surf, group):
		super().__init__(pos, surf, group)
		self.mask = pygame.mask.from_surface(self.image)

		mask_rects = self.mask.get_bounding_rects()

		if mask_rects:
			mask_rect = mask_rects[0].copy()
			for r in mask_rects[1:]:
				mask_rect.union_ip(r)
		else:
			mask_rect = self.image.get_rect()  # fallback

		self.rect = mask_rect.move(self.rect.topleft)

class Cannon(EntityBase):
	def __init__(self, orientation, assets, pos, group, cannonball_surf, damage_entities):
		self.frame_index = 0
		self.orientation = orientation
		self.frame_assets = self._prepare_assets(assets)

		self.animation_name = 'idle'

		initial_frame = self.frame_assets[self.animation_name][self.frame_index]
		super().__init__(pos, initial_frame, group)

		self.rect.bottom = self.rect.top + 64

		self.made_shot = False
		self.cannonball_surf = cannonball_surf

		self.attack_cooldown = Timer(3500)

		self.all_entities = group[0]
		self.damage_entities = damage_entities

	def _prepare_assets(self, assets):
		if self.orientation == 'right':
			return {
				key: [pygame.transform.flip(surf, True, False) for surf in frames]
				for key, frames in assets.items()
			}
		return assets.copy()

	def update(self, dt):
		self._update_status()
		self._animate(dt)
		self.attack_cooldown.update()

	def _update_status(self):
		distance = vector(self.player.rect.center).distance_to(vector(self.rect.center))
		if distance < 700 and not self.attack_cooldown.is_active():
			self.animation_name = 'attack'
		else:
			self.animation_name = 'idle'

	def _animate(self, dt):
		frames = self.frame_assets[self.animation_name]
		self.frame_index += 8 * dt

		if self.frame_index >= len(frames):
			self.frame_index = 0
			if self.made_shot:
				self.attack_cooldown.activate()
				self.made_shot = False

		if int(self.frame_index) == 2 and self.animation_name == 'attack' and not self.made_shot:
			self._shoot()

		self.image = frames[int(self.frame_index)]

	def _shoot(self):
		direction = vector(1, 0) if self.orientation == 'right' else vector(-1, 0)
		offset = direction * (20 if self.orientation == 'right' else 50) + vector(0, -10)
		position = self.rect.center + offset

		Cannonball(position, direction, self.cannonball_surf, [self.all_entities, self.damage_entities])
		self.made_shot = True

class Saw(EntityBase):
	def __init__(self, orientation, assets, pos, group):
		self.orientation = orientation
		self.frame_assets = assets.copy()
		if orientation == 'top':
			flipped_frames = []
			for surf in self.frame_assets:
				flipped = pygame.transform.flip(surf, True, True)
				flipped_frames.append(flipped)
			self.frame_assets = flipped_frames

		if orientation == 'left':
			flipped_frames = []
			for surf in self.frame_assets:
				flipped = pygame.transform.rotate(surf, -90)
				flipped_frames.append(flipped)
			self.frame_assets = flipped_frames

		if orientation == 'right':
			flipped_frames = []
			for surf in self.frame_assets:
				flipped = pygame.transform.rotate(surf, 90)
				flipped_frames.append(flipped)
			self.frame_assets = flipped_frames

		self.frame_index = 0
		super().__init__(pos, self.frame_assets[self.frame_index], group)
		self.rect.bottom = self.rect.top + 64

	def animate(self, dt):
		current_animation = self.frame_assets
		self.frame_index += 8 * dt
		if self.frame_index >= len(current_animation):
			self.frame_index = 0
		self.image = current_animation[int(self.frame_index)]

	def update(self, dt):
		self.animate(dt)


class Cannonball(EntityBase):
	def __init__(self, pos, direction, surf, group):
		super().__init__(pos, surf, group)
		self.direction = direction.normalize()
		self.disappear_timer = Timer(3500)
		self.speed = 300
		self.disappear_timer.activate()

		self.mask = pygame.mask.from_surface(self.image)
		self._set_initial_position()

	def _set_initial_position(self):
		self.pos = vector(self.rect.topleft)

	def _move(self, dt):
		self.pos += self.direction * self.speed * dt
		self.rect.topleft = self.pos

	def _check_lifetime(self):
		self.disappear_timer.update()
		if not self.disappear_timer.is_active():
			self.kill()

	def update(self, dt):
		self._move(dt)
		self._check_lifetime()


class Player(EntityBase):
	def __init__(self, pos, assets, group, collision_entities, sound, player_dead, semi_colidable_entities, knockback_entities):

		# animation
		self.frames = assets
		self.frame_index = 0
		self.attack_frame_index = 0
		self.semi_colidable_entities = semi_colidable_entities
		self.knockback_entities = knockback_entities
		self.animation_name = 'idle'
		self.orientation = 'right'
		self.player_dead = player_dead
		self.player_attack = False
		surf = self.frames[f'{self.animation_name}_{self.orientation}'][self.frame_index]
		super().__init__(pos, surf, group)
		self.mask = pygame.mask.from_surface(self.image)
		self.speed = 400
		self.direction = vector()
		self.pos = vector(self.rect.center)

		self.gravity = 4
		self.wall_jump_x_impulse = 0
		self.wall_jump_decay = 5
		self.on_right_wall = False
		self.on_left_wall = False
		self.on_floor = False

		self.collision_entities = collision_entities
		self.hitbox = self.rect.inflate(-50, 0)
		self.is_drowning = False

		self.immortality_timer = Timer(500)
		self.platform_skip_timer = Timer(150)
		self.attack_cooldown_timer = Timer(1000)

		self.jmp_sound = sound
		self.jmp_sound.set_volume(0.1)

	def drown(self, flipper):
		if flipper == True:
			self.speed = 150
			self.gravity = 2
		elif flipper == False:
			self.speed = 400
			self.gravity = 4

	def set_drowning(self, flipper):
		if flipper == True:
			self.is_drowning = True
		else:
			self.is_drowning = False

	def update_animation(self):
		if self.player_dead():
			self.animation_name = 'dead'
			return

		if self.player_attack:
			self.animation_name = 'attack'
			return

		if self.direction.y < 0:
			self.animation_name = 'jump'
			return

		if not self.on_floor and self.direction.y > 0:
			if (self.on_left_wall and self.direction.x < 0) or \
					(self.on_right_wall and self.direction.x > 0):
				self.animation_name = 'wall_slide'
			else:
				self.animation_name = 'fall'
			return

		self.animation_name = 'run' if self.direction.x != 0 else 'idle'

	def get_hit(self):
		if not self.immortality_timer.is_active():
			self.immortality_timer.activate()
			self.direction.y -= 1.5

	def animate(self, dt):
		if self.animation_name == 'dead':
			current_animation = self.frames[f'{self.animation_name}_{self.orientation}']
			self.speed = 0
			self.frame_index += 8 * dt
			self.frame_index = 3 if self.frame_index >= len(current_animation) else self.frame_index
			self.image = current_animation[int(self.frame_index)]
			self.mask = pygame.mask.from_surface(self.image)
		elif self.animation_name == 'attack':
			current_animation = self.frames[f'{self.animation_name}_{self.orientation}']
			self.attack_frame_index += 8 * dt
			if self.attack_frame_index >= len(current_animation):
				self.player_attack = False
				self.attack_frame_index = 0
			else:
				self.image = current_animation[int(self.attack_frame_index)]

		else:
			current_animation = self.frames[f'{self.animation_name}_{self.orientation}']
			self.frame_index += 8 * dt
			self.frame_index = 0 if self.frame_index >= len(current_animation) else self.frame_index
			self.image = current_animation[int(self.frame_index)]
			self.mask = pygame.mask.from_surface(self.image)

		if self.immortality_timer.is_active():
			surf = self.mask.to_surface()
			surf.set_colorkey('black')
			self.image = surf
		if self.is_drowning == True and self.animation_name != 'dead':
			self.drown(True)
		if self.is_drowning == False and self.animation_name != 'dead':
			self.drown(False)

	def check_input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
			self.orientation = 'right'
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
			self.orientation = 'left'
		else:
			self.direction.x = 0

		if keys[pygame.K_a] and not self.attack_cooldown_timer.is_active():
			self.player_attack = True
			self.attack_cooldown_timer.activate()

		if keys[pygame.K_SPACE]:
			if self.on_floor:
				self.direction.y = -2
				self.jmp_sound.play()
			elif self.animation_name == 'wall_slide':
				self.direction.y = -2
				self.wall_jump_x_impulse = 2 if self.on_left_wall else -2
				self.jmp_sound.play()

		if keys[pygame.K_DOWN]:
			self.platform_skip_timer.activate()

	def decay_wall_jump(self, dt):
		if self.wall_jump_x_impulse != 0:
			decay = self.wall_jump_decay * dt
			if abs(self.wall_jump_x_impulse) <= decay:
				self.wall_jump_x_impulse = 0
			else:
				self.wall_jump_x_impulse -= decay if self.wall_jump_x_impulse > 0 else -decay

	def move(self, dt):

		# horizontal movement
		total_x = self.direction.x + self.wall_jump_x_impulse
		self.pos.x += total_x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collide('horizontal')

		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collide('vertical')
		self.semi_collide()

	def add_gravity_y(self, dt):
		self.direction.y += self.gravity * dt
		if self.animation_name == 'wall_slide':
			self.direction.y = min(self.direction.y, 0.5)
		self.rect.y += self.direction.y

	def if_collides_floor(self):
		floor_rect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 2))
		floor_entities = []
		for entity in self.collision_entities:
			if entity.rect.colliderect(floor_rect):
				floor_entities = entity
		for entity in self.semi_colidable_entities:
			if entity.rect.colliderect(floor_rect):
				floor_entities = entity
		self.on_floor = True if floor_entities else False

	def check_knockback(self):
		left_edge = pygame.Rect(self.hitbox.left - 4, self.hitbox.top, 4, self.hitbox.height)
		right_edge = pygame.Rect(self.hitbox.right, self.hitbox.top, 4, self.hitbox.height)
		for entity in self.knockback_entities:
			if entity.rect.colliderect(left_edge) and self.orientation == 'left' and self.animation_name == 'attack':
				entity.direction.x = - 1
				entity.orientation = 'left'
			elif entity.rect.colliderect(right_edge) and self.orientation == 'right' and self.animation_name == 'attack':
				entity.direction.x = 1
				entity.orientation = 'right'

	def if_collides_wall(self):
		left_rect = pygame.Rect(self.hitbox.topleft + vector(-2, self.hitbox.height / 4), (2, self.hitbox.height / 2))
		right_rect = pygame.Rect(self.hitbox.topright + vector(0, self.hitbox.height / 4), (2, self.hitbox.height / 2))
		right_wall_entities = [entity for entity in self.collision_entities if entity.rect.colliderect(right_rect)]
		left_wall_entities = [entity for entity in self.collision_entities if entity.rect.colliderect(left_rect)]
		self.on_right_wall = True if right_wall_entities else False
		self.on_left_wall = True if left_wall_entities else False

	def collide(self, direction):
		for entity in self.collision_entities:
			if entity.rect.colliderect(self.hitbox):
				if direction == 'horizontal':
					if self.direction.x > 0:
						self.hitbox.right = entity.rect.left
					elif self.direction.x < 0:
						self.hitbox.left = entity.rect.right
					self.rect.centerx = self.hitbox.centerx
					self.pos.x = self.hitbox.centerx
				else:
					if self.direction.y < 0:
						self.hitbox.top = entity.rect.bottom
					elif self.direction.y > 0:
						self.hitbox.bottom = entity.rect.top
					self.rect.centery = self.hitbox.centery
					self.pos.y = self.hitbox.centery
					self.direction.y = 0

	def semi_collide(self):
		if not self.platform_skip_timer.is_active():
			for entity in self.semi_colidable_entities:
				bottom_edge = pygame.Rect(self.hitbox.left, self.hitbox.bottom - 1, self.hitbox.width, 2)
				if entity.rect.colliderect(bottom_edge):
					if self.direction.y > 0:
						self.hitbox.bottom = entity.rect.top
						self.rect.centery, self.pos.y = self.hitbox.centery, self.hitbox.centery
						self.direction.y = 0


	def update(self, dt):
		self.check_input()
		self.add_gravity_y(dt)
		self.move(dt)
		self.if_collides_floor()
		self.if_collides_wall()
		self.immortality_timer.update()
		self.platform_skip_timer.update()
		self.attack_cooldown_timer.update()
		self.decay_wall_jump(dt)
		self.check_knockback()

		self.update_animation()
		self.animate(dt)