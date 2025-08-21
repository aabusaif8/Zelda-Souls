import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from object_identifier import ObjectIdentifier

class Level:
    def __init__(self):
        #get the display surface
        self.display_surface = pygame.display.get_surface()

        #sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # Initialize object mapper
        self.object_mapper = ObjectIdentifier()

        #sprite creation
        self.create_map()
    
    def create_map(self):
         
         layouts = {
             'boundary' : import_csv_layout('./graphics/TileMap/_boundary_blocks.csv'),  # Normalized
             'grass' : import_csv_layout('./graphics/TileMap/_details.csv'),           # Normalized
             'object' : import_csv_layout_raw('./graphics/TileMap/_objects.csv')       # Raw values
         }
         graphics = {
             'grass' : import_folder('./graphics/Grass'),
             'objects' : import_folder('./graphics/Objects')
         }
         print(graphics)

         # Reset the object mapper for this new map
         self.object_mapper.reset()

         # Reset offsets for the smaller 2048x2048 map
         map_width_pixels = 2048
         map_height_pixels = 2048
         map_offset_x = -(map_width_pixels // 2)
         map_offset_y = -(map_height_pixels // 2)
         
         for style,layout in layouts.items():
            for row_index,row in enumerate(layout):
                for col_index,col in enumerate(row):
                    x = col_index * TILESIZE + map_offset_x
                    y = row_index * TILESIZE + map_offset_y
                    
                    if style in ['boundary', 'grass'] and col == '395':  # Only boundary and grass use normalized values
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites],'invisible')
                            print(f"Created boundary at ({x}, {y})")
                        elif style == 'grass':
                            random_grass_img = choice(graphics['grass'])
                            Tile((x,y),[self.visible_sprites, self.obstacle_sprites],'grass',random_grass_img)
                            print(f"Created grass at ({x}, {y})")
                    
                    elif style == 'object' and col != '-1':  # Objects use raw CSV values
                        # Use the object mapper to check for patterns
                        object_index, positions_to_mark = self.object_mapper.get_object_at_position(
                            layout, row_index, col_index
                        )
                        
                        print(f"Checking object at row {row_index}, col {col_index}, value: '{col}', found pattern: {object_index}")
                        
                        if object_index is not None and object_index < len(graphics['objects']):
                            # Place the complete object
                            surf = graphics['objects'][object_index]
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)
                            print(f"CREATED OBJECT {object_index} at ({x}, {y}) - Total obstacles now: {len(self.obstacle_sprites)}")
                            
                            # Mark positions as processed
                            self.object_mapper.mark_positions_processed(positions_to_mark)

         print(f"Final obstacle count: {len(self.obstacle_sprites)}")
         # Start player near the center of the map
         self.player = Player((0, 0), [self.visible_sprites], self.obstacle_sprites)
    
    def run(self):
       #update and draw the game
       self.visible_sprites.custom_draw(self.player)
       self.visible_sprites.update()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        self.floor_surf = pygame.image.load('./graphics/map.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (-1024, -1024))
    
    def custom_draw(self,player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf,floor_offset_pos)

        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_pos)