import os
import pygame
from enum import Enum, auto

class AssetType(Enum):
    TITLE_SCREEN = auto()
    ENEMY_GOBLIN = auto()
    ENEMY_ORC = auto()
    ENEMY_SKELETON = auto()

class AssetManager:
    def __init__(self, screen_width=800, screen_height=600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.images = {}
        self.load_images()
    
    def load_images(self):
        images_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "images")
        
        image_paths = {
            AssetType.TITLE_SCREEN: os.path.join(images_folder, "title_screen.png"),
            AssetType.ENEMY_GOBLIN: os.path.join(images_folder, "goblin.png"),
            AssetType.ENEMY_ORC: os.path.join(images_folder, "orc.png"),
            AssetType.ENEMY_SKELETON: os.path.join(images_folder, "skeleton.png")
        }
        
        try:
            for asset_type, path in image_paths.items():
                if os.path.exists(path):
                    image = pygame.image.load(path)
                    
                    if asset_type == AssetType.TITLE_SCREEN:
                        image = pygame.transform.scale(image, (self.screen_width, self.screen_height))
                        
                    self.images[asset_type] = image
                else:
                    print(f"Image not found: {path}")
        except Exception as e:
            print(f"Error loading images: {e}")
    
    def get_image(self, asset_type):
        return self.images.get(asset_type)
    
    def get_enemy_image(self, enemy_name):
        enemy_type_map = {
            "Goblin": AssetType.ENEMY_GOBLIN,
            "Orc": AssetType.ENEMY_ORC,
            "Skeleton": AssetType.ENEMY_SKELETON
        }
        
        asset_type = enemy_type_map.get(enemy_name)
        if asset_type:
            return self.get_image(asset_type)
        return None
