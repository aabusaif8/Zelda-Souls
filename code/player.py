import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

        self.hitbox = self.rect.inflate(0,-26) #custom hitbox. the sprite visually doesn't change, but the height of the hitbox is smaller so the player can appear "slightly" behind the obstacles.

        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites
        
        # Debug: Check if obstacle_sprites was passed correctly
        print(f"Player received obstacle_sprites with {len(self.obstacle_sprites)} sprites")

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0
            
    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')  
        self.rect.center = self.hitbox.center
        
    def collision(self,direction):
        collision_happened = False
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    collision_happened = True
                    print(f"HORIZONTAL COLLISION at player pos ({self.hitbox.x}, {self.hitbox.y}) with obstacle at ({sprite.hitbox.x}, {sprite.hitbox.y})")
                    if self.direction.x > 0: #player is moving to the right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: #player is moving to the left
                        self.hitbox.left = sprite.hitbox.right
                        
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    collision_happened = True
                    print(f"VERTICAL COLLISION at player pos ({self.hitbox.x}, {self.hitbox.y}) with obstacle at ({sprite.hitbox.x}, {sprite.hitbox.y})")
                    if self.direction.y > 0: #player is moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: #player is moving up
                        self.hitbox.top = sprite.hitbox.bottom

        # Debug: Show when we're checking collision but not finding any
        if len(self.obstacle_sprites) > 0 and not collision_happened and self.direction.magnitude() > 0:
            if direction == 'horizontal' and self.direction.x != 0:
                print(f"No horizontal collision found. Player at ({self.hitbox.x}, {self.hitbox.y}), checking against {len(self.obstacle_sprites)} obstacles")
            elif direction == 'vertical' and self.direction.y != 0:
                print(f"No vertical collision found. Player at ({self.hitbox.x}, {self.hitbox.y}), checking against {len(self.obstacle_sprites)} obstacles")

    def update(self):
        self.input()
        self.move(self.speed)