import pygame
from typing import List, Dict, Callable, Tuple
from enum import Enum
import os
from .ui_elements import UIElement, Button, Label, ProgressBar, draw_text, draw_health_bar
from .ui_lists import ScrollableList
from .ui_state_builders import StateUIBuilder
from .asset_manager import AssetType

class UIManager:
    def __init__(self, game):
        self.game = game
        self.elements: List[UIElement] = []
        self.audio_manager = game.audio_manager
        self.asset_manager = game.asset_manager
        self.state_builder = StateUIBuilder(self)
        
    def clear(self):
        self.elements = []
        
    def add_element(self, element: UIElement):
        if isinstance(element, Button):
            element.ui_manager = self
        self.elements.append(element)
        return element
        
    def handle_event(self, event):
        for element in reversed(self.elements):  # Process top elements first
            if element.handle_event(event):
                return
                
    def update(self):
        for element in self.elements:
            element.update()
            
    def render(self):
        # Check if we're on the main menu and should display the title image first
        from .game import GameState
        if self.game.state == GameState.MAIN_MENU:
            title_image = self.asset_manager.get_image(AssetType.TITLE_SCREEN)
            if title_image:
                self.game.screen.blit(title_image, (0, 0))
        
        # Display enemy image if in combat
        if self.game.state == GameState.COMBAT and hasattr(self, 'enemy_image') and hasattr(self, 'enemy_image_pos'):
            self.game.screen.blit(self.enemy_image, self.enemy_image_pos)
                
        # Render all UI elements
        for element in self.elements:
            element.render(self.game.screen)
            
    def build_ui_for_state(self, state):
        self.clear()
        from .game import GameState
        
        if state == GameState.MAIN_MENU:
            self.state_builder.build_main_menu_ui(
                start_new_game_callback=self._start_new_game,
                load_game_callback=self._load_game,
                exit_game_callback=self._exit_game
            )
                                   
        elif state == GameState.CHARACTER:
            self.state_builder.build_character_ui(self.game.player)
                                   
        elif state == GameState.EQUIPMENT:
            self.state_builder.build_equipment_ui(self.game.player)
                                   
        elif state == GameState.SKILLS:
            self.state_builder.build_skills_ui(self.game.player)
                                   
        elif state == GameState.COMBAT_SETUP:
            self.state_builder.build_combat_setup_ui(
                add_skill_callback=self._add_skill_to_sequence,
                remove_skill_callback=self._remove_skill_from_sequence,
                start_combat_callback=self._start_combat
            )
                                   
        elif state == GameState.COMBAT:
            self.state_builder.build_combat_ui()
                
        elif state == GameState.RESULTS:
            victory = self.game.combat_manager.victory if hasattr(self.game, 'combat_manager') else False
            self.state_builder.build_game_over()
    
    def _start_new_game(self):
        from .game import GameState
        self.game.create_new_player()
        self.game.change_state(GameState.CHARACTER)
        
    def _load_game(self):
        if self.game.load_game():
            self.game.audio_manager.play_ui_click()
        
    def _exit_game(self):
        self.game.running = False
        
    def play_drop_sound(self):
        self.audio_manager.play_ui_drop()
        
    def _start_combat(self):
        from .game import GameState
        if self.game.combat_manager:
            self.game.combat_manager.start_new_battle()
            self.game.change_state(GameState.COMBAT)
            
    def _add_skill_to_sequence(self, skill):
        from .game import GameState
        if self.game.player:
            # Add the skill to the end of the combat sequence (unlimited skills allowed)
            next_index = len(self.game.player.combat_sequence)
            self.game.player.add_to_combat_sequence(skill, next_index)
            
            # Play the drop sound
            self.play_drop_sound()
            
            # Rebuild the UI to show changes
            self.build_ui_for_state(self.game.state)
    
    def _remove_skill_from_sequence(self, index):
        from .game import GameState
        if self.game.player and 0 <= index < len(self.game.player.combat_sequence):
            # Remove the skill at the specified index
            self.game.player.combat_sequence.pop(index)
            
            # Rebuild the UI to show changes
            self.build_ui_for_state(self.game.state)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle clicks on combat sequence list
            if hasattr(self, 'sequence_list'):
                item_idx = self.sequence_list.get_item_at_position(event.pos)
                if item_idx is not None:
                    item = self.sequence_list.items[item_idx]
                    
                    button_width = 80
                    button_x = self.sequence_list.rect.x + self.sequence_list.rect.width - button_width - 10
                    button_y = self.sequence_list.rect.y + ((item_idx - self.sequence_list.scroll_offset) * self.sequence_list.item_height) + 5
                    button_rect = pygame.Rect(button_x, button_y, button_width, 30)
                    
                    if button_rect.collidepoint(event.pos):
                        self._remove_skill_from_sequence(item.index)
                        return True
            
            # Handle clicks on available skills list
            for element in self.elements:
                if isinstance(element, ScrollableList) and element != getattr(self, 'sequence_list', None):
                    item_idx = element.get_item_at_position(event.pos)
                    if item_idx is not None:
                        item = element.items[item_idx]
                        
                        button_width = 80
                        button_x = element.rect.x + element.rect.width - button_width - 10
                        button_y = element.rect.y + ((item_idx - element.scroll_offset) * element.item_height) + 5
                        button_rect = pygame.Rect(button_x, button_y, button_width, 30)
                        
                        if button_rect.collidepoint(event.pos):
                            self._add_skill_to_sequence(item.skill)
                            return True
        
        for element in reversed(self.elements):
            if element.handle_event(event):
                if isinstance(element, ScrollableList) and element == getattr(self, 'sequence_list', None) and self.game.player:
                    new_sequence = []
                    for i, item in enumerate(element.items):
                        new_sequence.append(item.skill)
                        item.index = i
                        item.name = f"{i+1}. {item.skill.name}"
                    
                    self.game.player.combat_sequence = new_sequence
                return True