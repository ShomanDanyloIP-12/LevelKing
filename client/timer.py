import pygame

class Timer:
	def __init__(self, duration):
		self.duration = duration
		self.start_time = None

	def activate(self):
		self.start_time = pygame.time.get_ticks()

	def deactivate(self):
		self.start_time = None

	def is_active(self):
		return self.start_time is not None

	def is_expired(self):
		if not self.is_active():
			return False
		return pygame.time.get_ticks() - self.start_time >= self.duration

	def update(self):
		if self.is_expired():
			self.deactivate()