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
            # For objects, use a slightly smaller hitbox but not too small
            # This allows for better visual overlap while maintaining collision
            self.hitbox = self.rect.inflate(-5, -10)  # Less aggressive reduction
        elif sprite_type == 'grass':
            # Grass should have a smaller hitbox so player can appear slightly behind it
            self.hitbox = self.rect.inflate(0, -5)  # Smaller reduction
        elif sprite_type == 'invisible':
            # Boundary tiles use the full rect for collision - these should be solid
            self.hitbox = self.rect.copy()  # Full collision for boundaries
        else:
            # Default hitbox
            self.hitbox = self.rect.copy()

    def debug_draw(self, surface, offset):
        """Debug method to visualize hitboxes"""
        hitbox_rect = pygame.Rect(self.hitbox.x - offset.x, self.hitbox.y - offset.y, 
                                 self.hitbox.width, self.hitbox.height)
        pygame.draw.rect(surface, 'red', hitbox_rect, 2)