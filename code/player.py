import pygame
from settings import *
from support import import_folder
from enemy import Enemy
from entity import Entity

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

        self.hitbox = self.rect.inflate(0, -26) # Custom hitbox for better visual overlap

        # Graphics setup
        self.import_player_assets()
        self.status = 'down'


        # Movement
        self.obstacle_sprites = obstacle_sprites
        

        #weapons
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_delay = 200

        #magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic_list = list(magic_data.keys())        
        self.magic = self.magic_list[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None
        self.switch_delay = 200
        # magic cast cooldowns (ms): make heal ~4x longer
        self.magic_cooldowns = {
            'flame': 10000,
            'heal': 20000,
        }
        self.last_magic_cast = {name: 0 for name in self.magic_list}

        #stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic_multiplier': 3, 'speed': 5}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 123
        self.speed = self.stats['speed']

        
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
    
    def get_remaining_cooldown(self, ability_name):
        """Get remaining cooldown time for an ability or magic"""
        current_time = pygame.time.get_ticks()

        # check ability cooldowns
        if ability_name in self.ability_cooldowns:
            elapsed = current_time - self.last_ability_use[ability_name]
            return max(0, self.ability_cooldowns[ability_name] - elapsed)

        # check magic cooldowns
        if ability_name in self.magic_cooldowns:
            elapsed = current_time - self.last_magic_cast[ability_name]
            return max(0, self.magic_cooldowns[ability_name] - elapsed)

        return 0

    
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
        elif keys[pygame.K_1] or keys[pygame.K_2] or keys[pygame.K_3] or keys[pygame.K_4]:
            # map number keys to magic index 0..3
            target_index = None
            if keys[pygame.K_1]:
                target_index = 0
            elif keys[pygame.K_2]:
                target_index = 1
            elif keys[pygame.K_3]:
                target_index = 2
            elif keys[pygame.K_4]:
                target_index = 3

            if target_index is not None and target_index < len(self.magic_list):
                # switch selection only if allowed
                if self.can_switch_magic and self.magic_index != target_index:
                    self.can_switch_magic = False
                    self.magic_switch_time = pygame.time.get_ticks()
                    self.magic_index = target_index
                    self.magic = self.magic_list[self.magic_index]

                # cast currently selected magic respecting per-spell cooldowns
                now = pygame.time.get_ticks()
                spell = self.magic
                cooldown = self.magic_cooldowns.get(spell, 1000)
                if now - self.last_magic_cast[spell] >= cooldown:
                    cfg = magic_data[spell]
                    self.create_magic(spell, cfg['strength'] * self.stats['magic_multiplier'], cfg['cost'])
                    self.last_magic_cast[spell] = now

        # weapon switching (throttled)
        weapon_list = list(weapon_data.keys())
        if keys[pygame.K_q] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.weapon_switch_time = pygame.time.get_ticks()
            self.weapon_index = (self.weapon_index + 1) % len(weapon_list)
            self.weapon = weapon_list[self.weapon_index]


        if keys[pygame.K_e] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.weapon_switch_time = pygame.time.get_ticks()
            self.weapon_index = (self.weapon_index - 1) % len(weapon_list)
            self.weapon = weapon_list[self.weapon_index]

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
        current_time = pygame.time.get_ticks()

        if self.active_ability:
            effect_duration = 200  # 200ms effect duration
            if current_time - self.last_ability_use[self.active_ability] >= effect_duration:
                self.active_ability = None
                self.destroy_attack()
        
        if not self.can_switch_weapon and self.weapon_switch_time is not None:
            if current_time - self.weapon_switch_time >= self.switch_delay:
                self.can_switch_weapon = True
        if not self.can_switch_magic and self.magic_switch_time is not None:
            if current_time - self.magic_switch_time >= self.switch_delay:
                self.can_switch_magic = True
    
    def animate(self):
        """Update player animation"""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        # Set the image to the current frame
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
    
    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)