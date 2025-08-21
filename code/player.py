import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

        self.hitbox = self.rect.inflate(0,-26) # Custom hitbox for better visual overlap

        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites
        
        # Debug variables
        self.show_debug = False  # Toggle with 'D' key
        
        # Debug: Check if obstacle_sprites was passed correctly
        print(f"Player received obstacle_sprites with {len(self.obstacle_sprites)} sprites")

    def input(self):
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0
            
        # Debug toggle
        if keys[pygame.K_F1]:
            self.show_debug = not self.show_debug
            
    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')  
        self.rect.center = self.hitbox.center
        
    def collision(self, direction):
        collision_happened = False
        colliding_sprites = []
        
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    collision_happened = True
                    colliding_sprites.append(sprite)
                    if self.direction.x > 0: # Moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # Moving left
                        self.hitbox.left = sprite.hitbox.right
                        
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    collision_happened = True
                    colliding_sprites.append(sprite)
                    if self.direction.y > 0: # Moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # Moving up
                        self.hitbox.top = sprite.hitbox.bottom

        # Enhanced debug output
        if collision_happened and self.show_debug:
            sprite_types = [s.sprite_type for s in colliding_sprites]
            print(f"{direction.upper()} COLLISION: Player at ({self.hitbox.center}), hit {len(colliding_sprites)} obstacles: {sprite_types}")

    def debug_draw(self, surface, offset):
        """Draw debug information"""
        if self.show_debug:
            # Draw player hitbox in green
            player_rect = pygame.Rect(self.hitbox.x - offset.x, self.hitbox.y - offset.y, 
                                    self.hitbox.width, self.hitbox.height)
            pygame.draw.rect(surface, 'green', player_rect, 2)
            
            # Draw nearby obstacle hitboxes
            for sprite in self.obstacle_sprites:
                # Only draw obstacles near the player
                distance = pygame.math.Vector2(sprite.rect.center) - pygame.math.Vector2(self.rect.center)
                if distance.magnitude() < 200:  # Within 200 pixels
                    sprite.debug_draw(surface, offset)

    def update(self):
        self.input()
        self.move(self.speed)