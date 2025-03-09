import pygame
from typing import List, Dict, Callable, Tuple
from enum import Enum
import os
from .ui_components import Button, draw_text, draw_health_bar
from .asset_manager import AssetType

class UIElement:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        
    def handle_event(self, event) -> bool:
        """Return True if event was consumed"""
        return False
        
    def update(self):
        pass
        
    def render(self, surface):
        pass

class Button(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Callable, color: Tuple[int, int, int] = (100, 100, 200)):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.disabled_color = (100, 100, 100)
        self.is_hovered = False
        
    def handle_event(self, event) -> bool:
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Play click sound if available
                if hasattr(self, 'ui_manager') and hasattr(self.ui_manager, 'click_sound'):
                    self.ui_manager.play_click_sound()
                self.callback()
                return True
        return False
        
    def render(self, surface):
        if not self.visible:
            return
            
        if not self.enabled:
            color = self.disabled_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
            
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)  # Border
        
        font = pygame.font.SysFont(None, 28)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class Label(UIElement):
    def __init__(self, x: int, y: int, text: str, color: Tuple[int, int, int] = (255, 255, 255),
                 font_size: int = 24):
        super().__init__(x, y, 0, 0)
        self._text = text
        self.color = color
        self.font_size = font_size
        self.font = pygame.font.SysFont(None, font_size)
        self._update_dimensions()
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, new_text):
        self._text = new_text
        self._update_dimensions()
    
    def _update_dimensions(self):
        text_surf = self.font.render(self._text, True, self.color)
        self.rect.width = text_surf.get_width()
        self.rect.height = text_surf.get_height()
        
    def render(self, surface):
        if not self.visible:
            return
        
        text_surf = self.font.render(self._text, True, self.color)
        surface.blit(text_surf, self.rect)

class ProgressBar(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, 
                 value: float = 1.0, color: Tuple[int, int, int] = (0, 200, 0)):
        super().__init__(x, y, width, height)
        self.value = max(0.0, min(1.0, value))  # Clamp between 0 and 1
        self.color = color
        
    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))
        
    def render(self, surface):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        
        # Draw filled portion
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, 
                               int(self.rect.width * self.value), self.rect.height)
        pygame.draw.rect(surface, self.color, fill_rect)
        
        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1)

class UIManager:
    def __init__(self, game):
        self.game = game
        self.elements: List[UIElement] = []
        self.audio_manager = game.audio_manager
        self.asset_manager = game.asset_manager
        
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
        from .game import GameState
        
        self.clear()
        screen_width, screen_height = self.game.screen.get_size()
        
        if state == GameState.MAIN_MENU:
            # Position buttons in the lower part of the screen to not overlap with title image
            button_width = 200
            button_height = 40
            button_x = screen_width // 2 - button_width // 2
            
            # Add game title and subtitle only if no title image
            if not self.asset_manager.get_image(AssetType.TITLE_SCREEN):
                self.add_element(Label(screen_width // 2 - 150, 100, "Project Donut", (255, 215, 0), 48))
                self.add_element(Label(screen_width // 2 - 100, 170, "Fantasy RPG", (220, 220, 220), 32))
            
            # Position buttons at the bottom third of the screen
            start_y = screen_height - 200
            
            self.add_element(Button(button_x, start_y, button_width, button_height, "New Game", 
                                   lambda: self._start_new_game()))
            
            load_btn = Button(button_x, start_y + 60, button_width, button_height, "Load Game", 
                             lambda: self._load_game())
            load_btn.enabled = self.game.save_manager.save_exists()
            self.add_element(load_btn)
            
            self.add_element(Button(button_x, start_y + 120, button_width, button_height, "Exit", 
                                   lambda: self._exit_game()))
                                   
        elif state == GameState.CHARACTER:
            self.add_element(Label(20, 20, "Character", (255, 215, 0), 36))
            
            player = self.game.player
            self.add_element(Label(50, 80, f"Name: {player.name}", (220, 220, 220)))
            self.add_element(Label(50, 120, f"Level: {player.level}", (220, 220, 220)))
            self.add_element(Label(50, 160, f"HP: {player.current_hp}/{player.max_hp}", (220, 220, 220)))
            
            self.add_element(Button(screen_width - 180, 20, 160, 40, "Equipment", 
                                   lambda: self.game.change_state(GameState.EQUIPMENT)))
                                   
            self.add_element(Button(screen_width - 180, 70, 160, 40, "Skills", 
                                   lambda: self.game.change_state(GameState.SKILLS)))
                                   
            self.add_element(Button(screen_width - 180, 120, 160, 40, "Combat", 
                                   lambda: self.game.change_state(GameState.COMBAT_SETUP)))
                                   
        elif state == GameState.EQUIPMENT:
            self.add_element(Label(20, 20, "Equipment", (255, 215, 0), 36))
            
            if self.game.player and self.game.player.equipment:
                y_pos = 80
                for slot, item in self.game.player.equipment.items():
                    item_name = item.name if item else "Empty"
                    self.add_element(Label(50, y_pos, f"{slot}: {item_name}", (220, 220, 220)))
                    y_pos += 40
            
            self.add_element(Button(screen_width - 180, 20, 160, 40, "Back", 
                                   lambda: self.game.change_state(GameState.CHARACTER)))
                                   
        elif state == GameState.SKILLS:
            self.add_element(Label(20, 20, "Combat Skills", (255, 215, 0), 36))
            
            if self.game.player and self.game.player.skills:
                y_pos = 80
                for skill in self.game.player.skills:
                    self.add_element(Label(50, y_pos, f"{skill.name} - {skill.description}", (220, 220, 220)))
                    y_pos += 40
            
            self.add_element(Button(screen_width - 180, 20, 160, 40, "Back", 
                                   lambda: self.game.change_state(GameState.CHARACTER)))
                                   
        elif state == GameState.COMBAT_SETUP:
            self.add_element(Label(20, 20, "Combat Setup", (255, 215, 0), 36))
            
            self.add_element(Label(50, 80, "Configure your combat sequence:", (220, 220, 220)))
            
            # Display current combat sequence
            if self.game.player and self.game.player.combat_sequence:
                y_pos = 120
                for i, skill in enumerate(self.game.player.combat_sequence):
                    skill_name = skill.name if skill else "No skill selected"
                    self.add_element(Label(70, y_pos, f"{i+1}. {skill_name}", (220, 220, 220)))
                    
                    # Add a "Remove" button for each skill
                    if skill:
                        self.add_element(Button(
                            280, y_pos, 80, 30, "Remove", 
                            lambda idx=i: self._remove_skill_from_sequence(idx)
                        ))
                    y_pos += 40
            
            # Available skills section
            self.add_element(Label(400, 80, "Available Skills:", (220, 220, 220)))
            
            if self.game.player and self.game.player.skills:
                y_pos = 120
                for i, skill in enumerate(self.game.player.skills):
                    # Don't show skills that are already in the sequence
                    if skill not in self.game.player.combat_sequence:
                        self.add_element(Label(420, y_pos, f"{skill.name}", (220, 220, 220)))
                        
                        # Add button to add skill to sequence
                        self.add_element(Button(
                            600, y_pos, 80, 30, "Add", 
                            lambda s=skill: self._add_skill_to_sequence(s)
                        ))
                        
                        y_pos += 40
            
            self.add_element(Button(screen_width // 2 - 80, screen_height - 120, 160, 40, "Start Combat", 
                                   lambda: self._start_combat()))
                                   
            self.add_element(Button(screen_width - 180, 20, 160, 40, "Back", 
                                   lambda: self.game.change_state(GameState.CHARACTER)))
                                   
        elif state == GameState.COMBAT:
            # Get screen dimensions for layout calculations
            screen_width, screen_height = self.game.screen.get_size()
            
            # Title
            self.add_element(Label(screen_width // 2 - 50, 20, "Combat", (255, 0, 0), 36))
            
            player = self.game.player
            enemy = self.game.combat_manager.current_enemy
            action_manager = self.game.combat_manager.action_manager
            
            # Player section - left side
            player_section_x = 50
            player_section_y = 80
            
            # Player info
            self.add_element(Label(player_section_x, player_section_y, f"{player.name}", (220, 220, 220), 28))
            self.add_element(Label(player_section_x, player_section_y + 40, f"HP: {player.current_hp}/{player.max_hp}", (220, 220, 220)))
            
            # Player HP bar
            hp_ratio = max(0, min(1, player.current_hp / player.max_hp))
            player_hp_bar = self.add_element(ProgressBar(player_section_x, player_section_y + 70, 200, 20, hp_ratio, (0, 200, 0)))
            
            # Player AP bar
            player_action = 0.0
            if action_manager and hasattr(player, 'id'):
                player_action = action_manager.get_current_action(player.id)
            
            max_ap = 20.0
            ap_ratio = max(0, min(1, player_action / max_ap))
            player_ap_bar = self.add_element(ProgressBar(player_section_x, player_section_y + 110, 200, 20, ap_ratio, (100, 200, 255)))
            self.add_element(Label(player_section_x, player_section_y + 135, f"AP: {player_action:.1f}/{max_ap}", (100, 200, 255), 20))
            
            # Enemy section - right side
            enemy_section_x = screen_width - 250
            enemy_section_y = 80
            
            # Enemy info
            self.add_element(Label(enemy_section_x, enemy_section_y, f"{enemy.name}", (220, 100, 100), 28))
            self.add_element(Label(enemy_section_x, enemy_section_y + 40, f"HP: {enemy.current_hp}/{enemy.max_hp}", (220, 100, 100)))
            
            # Enemy HP bar
            hp_ratio = max(0, min(1, enemy.current_hp / enemy.max_hp))
            enemy_hp_bar = self.add_element(ProgressBar(enemy_section_x, enemy_section_y + 70, 200, 20, hp_ratio, (200, 0, 0)))
            
            # Enemy AP bar
            enemy_action = 0.0
            if enemy and action_manager and hasattr(enemy, 'id'):
                enemy_action = action_manager.get_current_action(enemy.id)
            
            ap_ratio = max(0, min(1, enemy_action / max_ap))
            enemy_ap_bar = self.add_element(ProgressBar(enemy_section_x, enemy_section_y + 110, 200, 20, ap_ratio, (255, 150, 100)))
            self.add_element(Label(enemy_section_x, enemy_section_y + 135, f"AP: {enemy_action:.1f}/{max_ap}", (255, 150, 100), 20))
            
            # Add enemy logo (hardcoded to goblin for now)
            enemy_image = self.asset_manager.get_image(AssetType.ENEMY_GOBLIN)
            if enemy_image:
                enemy_image = pygame.transform.scale(enemy_image, (80, 80))
                # Add the enemy image as a direct render in the update method
                self.enemy_image = enemy_image
                self.enemy_image_pos = (enemy_section_x + 60, enemy_section_y + 160)
            
            # Combat log section - bottom
            log_section_y = screen_height - 220  # Move up to prevent cutoff
            self.add_element(Label(50, log_section_y, "Combat Log:", (180, 180, 220), 24))
            
            # Draw a semi-transparent background for the combat log
            log_bg = pygame.Surface((screen_width - 100, 160))  # Reduce height slightly
            log_bg.set_alpha(50)
            log_bg.fill((50, 50, 70))
            self.game.screen.blit(log_bg, (50, log_section_y + 30))
            
            # Display the most recent combat log messages
            log_y = log_section_y + 40
            # Show fewer messages to prevent overflow
            recent_messages = self.game.combat_manager.combat_log[-5:]
            for message in recent_messages:
                self.add_element(Label(70, log_y, message, (200, 200, 240)))
                log_y += 30
                
        elif state == GameState.RESULTS:
            self.add_element(Label(20, 20, "Battle Results", (255, 215, 0), 36))
            
            result = "Victory!" if self.game.combat_manager.victory else "Defeat!"
            color = (0, 255, 0) if self.game.combat_manager.victory else (255, 0, 0)
            
            self.add_element(Label(screen_width // 2 - 50, 100, result, color, 42))
            
            if self.game.combat_manager.victory:
                rewards = self.game.combat_manager.rewards
                self.add_element(Label(screen_width // 2 - 100, 180, f"Experience: {rewards['experience']}", (220, 220, 220)))
                self.add_element(Label(screen_width // 2 - 100, 220, f"Gold: {rewards['gold']}", (220, 220, 100)))
                
                if rewards.get('items'):
                    self.add_element(Label(screen_width // 2 - 100, 260, "Items:", (220, 220, 220)))
                    y_pos = 300
                    for item in rewards['items']:
                        self.add_element(Label(screen_width // 2 - 80, y_pos, f"- {item.name}", (220, 220, 220)))
                        y_pos += 40
            
            self.add_element(Button(screen_width // 2 - 80, screen_height - 120, 160, 40, "Continue", 
                                   lambda: self.game.change_state(GameState.CHARACTER)))
    
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
        """Add a skill to the combat sequence"""
        from .game import GameState
        if self.game.player:
            # Find the first empty slot or add to end
            for i in range(5):  # Max 5 skills in sequence
                if i >= len(self.game.player.combat_sequence) or self.game.player.combat_sequence[i] is None:
                    self.game.player.add_to_combat_sequence(skill, i)
                    # Play the drop sound
                    self.play_drop_sound()
                    # Rebuild the UI to show changes
                    self.build_ui_for_state(self.game.state)
                    return
                    
            # If all slots are full, replace the last one
            if len(self.game.player.combat_sequence) > 0:
                self.game.player.add_to_combat_sequence(skill, len(self.game.player.combat_sequence) - 1)
                # Play the drop sound
                self.play_drop_sound()
                # Rebuild the UI to show changes
                self.build_ui_for_state(self.game.state)
    
    def _remove_skill_from_sequence(self, index):
        """Remove a skill from the combat sequence at the given index"""
        from .game import GameState
        if self.game.player and 0 <= index < len(self.game.player.combat_sequence):
            # Set the slot to None
            self.game.player.combat_sequence[index] = None
            
            # Remove any None values at the end of the sequence
            while self.game.player.combat_sequence and self.game.player.combat_sequence[-1] is None:
                self.game.player.combat_sequence.pop()
                
            # Rebuild the UI to show changes
            self.build_ui_for_state(self.game.state)