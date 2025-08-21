from csv import reader
import pygame
def import_csv_layout(path):
    """Import CSV and return all values as strings, unchanged."""
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append([cell.strip() for cell in row])
    return terrain_map

def import_csv_layout_raw(path):
    """Import CSV without any normalization - keeps original values for object pattern matching"""
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter = ',')
        for row in layout:
            terrain_map.append(list(row))  # Keep original values
        return terrain_map

def import_folder(path):
    """Import all images from a folder"""
    surface_list = []
    
    # This function should load all images from the specified folder
    # You'll need to implement this based on your file structure
    # Here's a basic version:
    import os
    for filename in os.listdir(path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            full_path = os.path.join(path, filename)
            image = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image)
    
    return surface_list