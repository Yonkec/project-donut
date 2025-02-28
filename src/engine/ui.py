import pygame
from typing import List, Dict, Callable, Tuple
from enum import Enum
import os

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
        super().__init__(x, y, 0, 0)  # Width and height will be set when rendering
        self.text = text
        self.color = color
        self.font_size = font_size
        self.font = pygame.font.SysFont(None, font_size)
        text_surf = self.font.render(text, True, color)
        self.rect.width = text_surf.get_width()
        self.rect.height = text_surf.get_height()
        
    def render(self, surface):
        if not self.visible:
            return
            
        text_surf = self.font.render(self.text, True, self.color)
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
        self.click_sound = None
        self.drop_sound = None
        self.load_sounds()
        
    def load_sounds(self):
        """Load UI sound effects"""
        try:
            audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'audio')
            click_path = os.path.join(audio_dir, 'ui_click.wav')
            drop_path = os.path.join(audio_dir, 'ui_click2.mp3')
            
            if os.path.exists(click_path):
                self.click_sound = pygame.mixer.Sound(click_path)
            if os.path.exists(drop_path):
                self.drop_sound = pygame.mixer.Sound(drop_path)
        except Exception as e:
            print(f"Error loading UI sounds: {e}")
            
    def play_click_sound(self):
        """Play the UI click sound effect"""
        if self.click_sound:
            self.click_sound.play()
            
    def play_drop_sound(self):
        """Play the UI drop sound effect"""
        if self.drop_sound:
            self.drop_sound.play()
        
    def clear(self):
        self.elements = []
        
    def add_element(self, element: UIElement):
        # Add reference to UI manager for sounds
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
        for element in self.elements:
            element.render(self.game.screen)
            
    def build_ui_for_state(self, state):
        from .game import GameState
        
        self.clear()
        screen_width, screen_height = self.game.screen.get_size()
        
        if state == GameState.MAIN_MENU:
            self.add_element(Label(screen_width // 2 - 150, 100, "Project Donut", (255, 215, 0), 48))
            self.add_element(Label(screen_width // 2 - 100, 170, "Fantasy RPG", (220, 220, 220), 32))
            
            self.add_element(Button(screen_width // 2 - 100, 250, 200, 40, "New Game", 
                                   lambda: self._start_new_game()))
            
            self.add_element(Button(screen_width // 2 - 100, 310, 200, 40, "Exit", 
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
            self.add_element(Label(20, 20, "Combat", (255, 0, 0), 36))
            
            player = self.game.player
            enemy = self.game.combat_manager.current_enemy
            
            # Player info
            self.add_element(Label(50, 80, f"{player.name}", (220, 220, 220)))
            self.add_element(Label(50, 110, f"HP: {player.current_hp}/{player.max_hp}", (220, 220, 220)))
            
            player_hp_bar = self.add_element(ProgressBar(50, 140, 200, 20, player.current_hp / player.max_hp, (0, 200, 0)))
            
            # Enemy info
            self.add_element(Label(screen_width - 250, 80, f"{enemy.name}", (220, 100, 100)))
            self.add_element(Label(screen_width - 250, 110, f"HP: {enemy.current_hp}/{enemy.max_hp}", (220, 100, 100)))
            
            enemy_hp_bar = self.add_element(ProgressBar(screen_width - 250, 140, 200, 20, enemy.current_hp / enemy.max_hp, (200, 0, 0)))
            
            # Combat log
            self.add_element(Label(50, 200, "Combat Log:", (180, 180, 220)))
            
            log_y = 240
            for message in self.game.combat_manager.combat_log[-5:]:
                self.add_element(Label(70, log_y, message, (180, 180, 220)))
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
        self.game.create_new_player()
        self.game.change_state(GameState.CHARACTER)
        
    def _exit_game(self):
        self.game.running = False
        
    def _start_combat(self):
        if self.game.combat_manager:
            self.game.combat_manager.start_new_battle()
            self.game.change_state(GameState.COMBAT)
            
    def _add_skill_to_sequence(self, skill):
        """Add a skill to the combat sequence"""
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
        if self.game.player and 0 <= index < len(self.game.player.combat_sequence):
            # Set the slot to None
            self.game.player.combat_sequence[index] = None
            
            # Remove any None values at the end of the sequence
            while self.game.player.combat_sequence and self.game.player.combat_sequence[-1] is None:
                self.game.player.combat_sequence.pop()
                
            # Rebuild the UI to show changes
            self.build_ui_for_state(self.game.state)