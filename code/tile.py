import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)

        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

        # Simple hitbox adjustment based on sprite type
        if sprite_type == 'object':
            # Objects get a slightly smaller hitbox for better visual overlap
            self.hitbox = self.rect.inflate(-5, -10)
        elif sprite_type == 'grass':
            # Grass gets a small reduction so player can appear behind it
            self.hitbox = self.rect.inflate(0, -5)
        else:
            # Boundaries and default use full rect
            self.hitbox = self.rect.copy()

    def debug_draw(self, surface, offset):
        """Debug method to visualize hitboxes"""
        hitbox_rect = pygame.Rect(self.hitbox.x - offset.x, self.hitbox.y - offset.y, 
                                 self.hitbox.width, self.hitbox.height)
        pygame.draw.rect(surface, 'red', hitbox_rect, 2)