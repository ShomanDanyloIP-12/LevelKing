import pygame
from pathlib import Path


def read_folder(path):
	frames = []
	for image_path in Path(path).rglob('*'):
		if image_path.is_file():
			image_surf = pygame.image.load(str(image_path)).convert_alpha()
			frames.append(image_surf)
	return frames


def read_multiple_folders(path):
	frames_dict = {}
	for image_path in Path(path).rglob('*'):
		if image_path.is_file():
			image_surf = pygame.image.load(str(image_path)).convert_alpha()
			frames_dict[image_path.stem] = image_surf
	return frames_dict
