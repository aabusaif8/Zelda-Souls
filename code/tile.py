import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)

        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

        # Adjust hitbox based on sprite type
        if sprite_type == 'object':
            # For objects, use a more conservative hitbox that accounts for the actual image size
            # and provides better collision detection
            self.hitbox = self.rect.inflate(-10, -20)  # Slightly smaller than the full object
        elif sprite_type == 'grass':
            # Grass should have a smaller hitbox so player can appear slightly behind it
            self.hitbox = self.rect.inflate(0, -10)
        elif sprite_type == 'invisible':
            # Boundary tiles use the full rect for collision
            self.hitbox = self.rect
        else:
            # Default hitbox
            self.hitbox = self.rect.inflate(0, -10)