import pygame
import sys
from enum import Enum, auto
from typing import Dict, List, Optional
from .ui import UIManager
from .audio_manager import AudioManager
from .asset_manager import AssetManager
from .save_manager import SaveManager
from ..game.player import Player
from ..game.combat import CombatManager
from ..game.action_manager import ActionManager

class GameState(Enum):
    MAIN_MENU = auto()
    CHARACTER = auto()
    EQUIPMENT = auto()
    SKILLS = auto()
    COMBAT_SETUP = auto()
    COMBAT = auto()
    RESULTS = auto()
    SETTINGS = auto()
    END_COMBAT = auto()

class Game:
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Project Donut - Fantasy RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        self.width = width
        self.height = height
        self.state = GameState.MAIN_MENU
        self.previous_state = GameState.MAIN_MENU  # Track previous state for returning from settings
        self.action_manager = ActionManager()
        self.audio_manager = AudioManager()
        self.asset_manager = AssetManager(width, height)
        self.save_manager = SaveManager()
        self.player = None
        self.combat_manager = None
        self.ui_manager = UIManager(self)
        self.ui_manager.build_ui_for_state(self.state)
        self.audio_manager.play_menu_music()
        

        
    def create_new_player(self):
        self.player = Player("Hero", self.action_manager)
        self.combat_manager = CombatManager(self.player)
        self.audio_manager.play_town_music()
        
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
                
                # Rebuild the UI to reflect the updated combat state
                self.ui_manager.clear()
                self.ui_manager.build_ui_for_state(self.state)
                
                if combat_finished:
                    self.change_state(GameState.END_COMBAT)
        
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
        old_state = self.state
        
        # Store previous state when entering settings, but don't track settings as previous state
        if new_state == GameState.SETTINGS:
            self.previous_state = old_state
        elif old_state != GameState.SETTINGS:
            self.previous_state = old_state
            
        self.state = new_state
        self.ui_manager.build_ui_for_state(new_state)
        
        # Play appropriate music based on the new state
        if new_state == GameState.MAIN_MENU:
            self.audio_manager.play_menu_music()
        elif new_state in [GameState.CHARACTER, GameState.EQUIPMENT, GameState.SKILLS, GameState.COMBAT_SETUP]:
            self.audio_manager.play_town_music()
        elif new_state == GameState.COMBAT:
            self.audio_manager.play_battle_music()
        elif new_state in [GameState.RESULTS, GameState.END_COMBAT]:
            self.audio_manager.play_after_combat_music()
            
    def save_game(self):
        if not self.player:
            return False, "No player data to save"
            
        try:
            player_data = self.player.to_dict()
            
            # We don't need to pass combat_sequence separately since it's included in player_data
            success, message = self.save_manager.save_game(player_data, None)
            
            if success:
                self.ui_manager.show_notification("Game saved successfully!")
            else:
                self.ui_manager.show_notification(f"Save failed: {message}")
                
            return success, message
        except Exception as e:
            error_msg = f"Error saving game: {str(e)}"
            self.ui_manager.show_notification(error_msg)
            return False, error_msg
    
    def load_game(self):
        success, player_data = self.save_manager.load_game()
        
        if not success:
            self.ui_manager.show_notification("No save file found or load failed")
            return False
            
        try:
            self.player = Player.from_dict(player_data, self.action_manager)
            self.combat_manager = CombatManager(self.player)
            self.change_state(GameState.CHARACTER)
            self.ui_manager.show_notification("Game loaded successfully!")
            return True
        except Exception as e:
            error_msg = f"Error loading game: {str(e)}"
            self.ui_manager.show_notification(error_msg)
            return False