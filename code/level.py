import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from weapon import Weapon
from ui import UI
from enemy import Enemy

class Level:
    def __init__(self):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        #attack sprites
        self.current_attack = None

        # Initialize player as None
        self.player = None

        # Sprite creation
        self.create_map()

        #user interface
        self.ui = UI()
    
    def create_map(self):
         
         layouts = {
             'boundary' : import_csv_layout('./graphics/TileMap/mappington_boundary_blocks.csv'),
             'grass' : import_csv_layout('./graphics/TileMap/mappington_details.csv'),
             'object' : import_csv_layout_raw('./graphics/TileMap/mappington_objects.csv'),
             'enemy' : import_csv_layout_raw('./graphics/TileMap/mappington_entities.csv')
         }
         graphics = {
             'grass' : import_folder('./graphics/Grass'),
             'objects' : import_folder('./graphics/Objects'),
             'enemies' : import_folder('./graphics/Monsters')
         }

         # Map offset for centering
         map_width_pixels = 2048
         map_height_pixels = 2048
         map_offset_x = -(map_width_pixels // 2)
         map_offset_y = -(map_height_pixels // 2)
         
         # Build the object_surfaces dictionary at the start of create_map
         tiled_id_to_filename = {
             0: '01.png',
             1: '03.png',
             2: '17.png',
             3: '02.png',
             4: '04.png',
             5: '07.png',
             6: '06.png',
             7: '05.png',
             8: '10.png',
             9: '08.png',
             10: '19.png',
             11: '18.png',
         }
         self.object_surfaces = {}
         for tiled_id, filename in tiled_id_to_filename.items():
             full_path = f'./graphics/objects/{filename}'
             surf = pygame.image.load(full_path).convert_alpha()
             self.object_surfaces[tiled_id] = surf

         for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    x = col_index * TILESIZE + map_offset_x
                    y = row_index * TILESIZE + map_offset_y
                    
                    if style == 'boundary' and col == '395':
                        Tile((x, y), [self.obstacle_sprites], 'invisible')
                    elif style == 'grass' and col.strip() == '32':
                        random_grass_img = choice(graphics['grass'])
                        Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'grass', random_grass_img)
                    elif style == 'object' and col != '-1':
                        try:
                            object_id = int(col)
                            surf = self.object_surfaces.get(object_id)
                            if surf:
                                Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)
                        except ValueError:
                            pass  # Ignore invalid values
                    # Fixed: Changed 'entities' to 'enemy' to match the layout dictionary
                    elif style == 'enemy':
                        if col.strip() == '394':
                            # Only create player if one doesn't exist yet
                            if self.player is None:
                                self.player = Player((x,y), [self.visible_sprites], self.obstacle_sprites, self.create_attack, self.destroy_attack, self.create_magic)
                        elif col != '-1' and col.strip() != '':
                            # Create enemy - you may need to map different col values to different monster types
                            try:
                                enemy_id = int(col)
                                # Map enemy IDs to monster types
                                enemy_types = {
                                    390: 'bamboo',
                                    391: 'spirit', 
                                    392: 'raccoon',
                                    393: 'squid'
                                }
                                monster_type = enemy_types.get(enemy_id, 'squid')  # Default to squid
                                Enemy(monster_type, (x,y), [self.visible_sprites], self.obstacle_sprites)
                                print(f"Created {monster_type} enemy at ({x}, {y})")  # Debug output
                            except ValueError:
                                # If it's not a number, might be a monster name directly
                                if col.strip() in ['squid', 'raccoon', 'spirit', 'bamboo']:
                                    Enemy(col.strip(), (x,y), [self.visible_sprites], self.obstacle_sprites)
                                    print(f"Created {col.strip()} enemy at ({x}, {y})")  # Debug output

         # Only create fallback player if none was found in the map
         if self.player is None:
             print("No player found in map, creating fallback player at (0, 0)")
             self.player = Player(
                (0, 0),
                [self.visible_sprites],
                self.obstacle_sprites,
                self.create_attack,
                self.destroy_attack,
                self.create_magic)

    def create_attack(self):
        self.current_attack = Weapon(self.player,[self.visible_sprites])
    
    def create_magic(self,style,strength,cost):
        print(style,strength,cost)    
    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def run(self):
       # Update and draw the game
       self.visible_sprites.custom_draw(self.player)
       self.visible_sprites.update()
       self.ui.display(self.player)
       # Basic debug info
       #debug(f"Player pos: ({int(self.player.rect.centerx)}, {int(self.player.rect.centery)})")
       #debug(f"Obstacles: {len(self.obstacle_sprites)}", 10, 40)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        self.floor_surf = pygame.image.load('./graphics/mappington.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (-1024, -1024))
    
    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
            
        # Draw debug info if enabled