import pygame
from settings import *
from support import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack):
        
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

        self.hitbox = self.rect.inflate(0, -26) # Custom hitbox for better visual overlap

        # Graphics setup
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites
        

        #weapons
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        
        # Simplified ability cooldowns
        self.ability_cooldowns = {
            'attack': 400,
            'magic1': 1000,
            'magic2': 1500,
            'magic3': 200,
            'magic4': 2000
        }
        self.last_ability_use = {ability: 0 for ability in self.ability_cooldowns.keys()}
        self.active_ability = None

        # Debug toggle
        self.show_debug = False

    def import_player_assets(self):
        character_path = './graphics/player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                        'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                        'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []}
        
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)
    
    def can_use_ability(self, ability_name):
        """Check if an ability is off cooldown"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_ability_use[ability_name] >= self.ability_cooldowns[ability_name]

    def use_ability(self, ability_name):
        """Use an ability and start its cooldown"""
        if self.can_use_ability(ability_name):
            self.last_ability_use[ability_name] = pygame.time.get_ticks()
            self.active_ability = ability_name
            print(f'{ability_name} used!')
            return True
        else:
            remaining = self.get_remaining_cooldown(ability_name)
            print(f'{ability_name} on cooldown for {remaining}ms more')
            return False

    def get_remaining_cooldown(self, ability_name):
        """Get remaining cooldown time for an ability"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.last_ability_use[ability_name]
        return max(0, self.ability_cooldowns[ability_name] - elapsed)

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.active_ability:
            # Movement
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0
            
                    # Ability inputs - each ability has its own cooldown
        if keys[pygame.K_SPACE]:
            if self.use_ability('attack'):
                self.create_attack()
        elif keys[pygame.K_1]:
            self.use_ability('magic1')
        elif keys[pygame.K_2]:
            self.use_ability('magic2')
        elif keys[pygame.K_3]:
            self.use_ability('magic3')
        elif keys[pygame.K_4]:
            self.use_ability('magic4')
            
    def get_status(self):
        # Get the base direction (without any suffixes)
        base_direction = self.status.split('_')[0] if '_' in self.status else self.status
        
        # Determine the current status based on movement and active ability
        if self.active_ability:
            # If using an ability, set to attack animation and stop movement
            self.direction.x = 0
            self.direction.y = 0
            self.status = f'{base_direction}_attack'
        elif self.direction.x == 0 and self.direction.y == 0:
            # If not moving and not using ability, set to idle
            self.status = f'{base_direction}_idle'
        else:
            # If moving, set to base direction (no suffix)
            self.status = base_direction

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')  
        self.rect.center = self.hitbox.center
        
    def collision(self, direction):        
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # Moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # Moving left
                        self.hitbox.left = sprite.hitbox.right
                        
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # Moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # Moving up
                        self.hitbox.top = sprite.hitbox.bottom

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

    def cooldowns(self):
        """Update ability cooldowns and clear active ability after effect duration"""
        if self.active_ability:
            current_time = pygame.time.get_ticks()
            effect_duration = 200  # 200ms effect duration
            if current_time - self.last_ability_use[self.active_ability] >= effect_duration:
                self.active_ability = None
                self.destroy_attack()

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        #set the image to the current frame
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)


    def get_attack_animation(self):
        """Get the appropriate attack animation based on current status"""
        return self.status
    
    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)