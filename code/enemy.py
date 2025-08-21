import pygame
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites=None):
        super().__init__(groups)
        self.sprite_type = 'enemy'
        
        # Store obstacle sprites for collision detection
        self.obstacle_sprites = obstacle_sprites or pygame.sprite.Group()

        #graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        
        # Set initial image - use black square as fallback if animations don't load
        if self.animations[self.status]:
            self.image = self.animations[self.status][self.frame_index]
        else:
            # This is the "black square" placeholder you mentioned from the tutorial
            self.image = pygame.Surface((32, 32))
            self.image.fill('black')
            print(f"Warning: No animations found for {monster_name}, using black square placeholder")
            
        self.rect = self.image.get_rect(topleft = pos)
        
        # Set up hitbox similar to player
        self.hitbox = self.rect.inflate(0, -10)
        
        # Enemy stats from settings
        self.monster_name = monster_name
        if monster_name in enemy_data:
            self.health = enemy_data[monster_name]['health']
            self.exp = enemy_data[monster_name]['exp']
            self.speed = enemy_data[monster_name]['speed']
            self.damage = enemy_data[monster_name]['damage']
            self.attack_radius = enemy_data[monster_name]['attack_radius']
            self.notice_radius = enemy_data[monster_name]['notice_radius']
        else:
            # Default stats if monster not found
            self.health = 100
            self.exp = 50
            self.speed = 2
            self.damage = 10
            self.attack_radius = 50
            self.notice_radius = 100

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main = f'./graphics/monsters/{name}/'
        for animation in self.animations.keys():
            try:
                self.animations[animation] = import_folder(main + animation)
            except FileNotFoundError:
                print(f"Warning: Animation folder {main + animation} not found")
                self.animations[animation] = []
    
    def update(self):
        # Basic enemy update - you can expand this with AI behavior later
        pass