import pygame
import sys
from enum import Enum, auto
from typing import Dict, List, Optional
from .ui import UIManager
from ..game.player import Player
from ..game.combat import CombatManager

class GameState(Enum):
    MAIN_MENU = auto()
    CHARACTER = auto()
    EQUIPMENT = auto()
    SKILLS = auto()
    COMBAT_SETUP = auto()
    COMBAT = auto()
    RESULTS = auto()

class Game:
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Project Donut - Fantasy RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MAIN_MENU
        self.player = None
        self.combat_manager = None
        self.assets = {}
        self.load_assets()
        # Create the UI manager after the assets are loaded
        self.ui_manager = UIManager(self)
        # Initialize the UI for the main menu
        self.ui_manager.build_ui_for_state(self.state)
        
    def load_assets(self):
        # Placeholder for asset loading
        self.assets['font'] = pygame.font.SysFont(None, 32)
        
    def create_new_player(self):
        self.player = Player("Hero")
        self.combat_manager = CombatManager(self.player)
        
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.ui_manager.handle_event(event)
                
    def update(self):
        self.ui_manager.update()
        
        if self.state == GameState.COMBAT:
            if self.combat_manager:
                combat_finished = self.combat_manager.update()
                if combat_finished:
                    self.state = GameState.RESULTS
        
    def render(self):
        self.screen.fill((30, 30, 40))  # Dark background
        self.ui_manager.render()
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.process_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()
        
    def change_state(self, new_state: GameState):
        self.state = new_state
        self.ui_manager.build_ui_for_state(new_state)