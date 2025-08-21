import pygame
from settings import *

class UI:
    def __init__(self):
        
        # general
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        #bar setup
        self.health_bar_rect = pygame.Rect((10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT))
        self.energy_bar_rect = pygame.Rect((10, 37, ENERGY_BAR_WIDTH, BAR_HEIGHT))

        #convert weapon dictionary
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon)
    
    def show_bar(self, current, max_amount, bg_rect, color):
        #draw the bg
        pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)

        #converting stats to pixels
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        #draw the bar
        pygame.draw.rect(self.display_surface,color,current_rect)
        pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)

    def show_exp(self,exp):
        text_surf = self.font.render(str(int(exp)),False,TEXT_COLOR)
        x = self.display_surface.get_width() - 20
        y = self.display_surface.get_height() - 20
        text_rect = text_surf.get_rect(bottomright=(self.display_surface.get_width()-10,self.display_surface.get_height()-10))

        pygame.draw.rect(self.display_surface,UI_BG_COLOR,text_rect.inflate(7,7))
        pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,text_rect.inflate(7,7),3)
        self.display_surface.blit(text_surf,text_rect)

    def selection_box(self,left,top,has_switched):
        bg_rect = pygame.Rect(left,top,ITEM_BOX_SIZE,ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)
        if has_switched:
            pygame.draw.rect(self.display_surface,UI_BORDER_COLOR_ACTIVE,bg_rect,3)
        else:
            pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)
        return bg_rect


    def weapon_overlay(self, weapon_index, has_switched):
        # selection box for weapon
        bg_rect = self.selection_box(30, 630, has_switched)
        weapon_surf = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)
        # load weapon graphic from settings using index

        self.display_surface.blit(weapon_surf, weapon_rect)
    
    def magic_overlay(self, magic_index, has_switched):
        # selection box for magic (shifted right to add spacing)
        bg_rect = self.selection_box(120, 630, has_switched)
        # load magic icon from settings
        magic_name = list(magic_data.keys())[magic_index]
        magic_path = magic_data[magic_name]['graphic']
        magic_surf = pygame.image.load(magic_path).convert_alpha()
        magic_rect = magic_surf.get_rect(center=bg_rect.center)
        self.display_surface.blit(magic_surf, magic_rect)
    
    def display(self, player):
        # health and energy bars
        self.show_bar(player.health,player.stats['health'],self.health_bar_rect,HEALTH_COLOR)
        self.show_bar(player.energy,player.stats['energy'],self.energy_bar_rect,ENERGY_COLOR)
        self.show_exp(player.exp)

        self.show_exp(player.exp)
        # highlight in gold when you can't switch (cooldown active)
        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon)
        self.magic_overlay(player.magic_index, not player.can_switch_magic)