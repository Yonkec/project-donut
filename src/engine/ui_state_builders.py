import pygame
from typing import List, Dict, Callable, Tuple
from .ui_elements import UIElement, Button, Label, ProgressBar, draw_text, draw_health_bar
from .ui_lists import ScrollableList
from .asset_manager import AssetType

class StateUIBuilder:
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.game = ui_manager.game
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
        
    def build_main_menu_ui(self, start_new_game_callback, load_game_callback, settings_callback, exit_game_callback):
        # Use percentage-based positioning for better adaptability
        button_width = int(self.screen_width * 0.25)  # 25% of screen width
        button_height = int(self.screen_height * 0.07)  # 7% of screen height
        button_x = int(self.screen_width * 0.5 - button_width * 0.5)  # Centered horizontally
        
        # Add game title and subtitle only if no title image
        if not self.ui_manager.asset_manager.get_image(AssetType.TITLE_SCREEN):
            title_x = int(self.screen_width * 0.5)
            title_y = int(self.screen_height * 0.15)
            subtitle_y = int(self.screen_height * 0.25)
            
            title_label = Label(title_x - 150, title_y, "Project Donut", (255, 215, 0), 48)
            subtitle_label = Label(title_x - 100, subtitle_y, "Fantasy RPG", (220, 220, 220), 32)
            self.ui_manager.add_element(title_label)
            self.ui_manager.add_element(subtitle_label)
        
        # Position buttons evenly in the bottom half of the screen
        button_start_y = int(self.screen_height * 0.5)  # Start at 50% of screen height
        button_spacing = int(self.screen_height * 0.1)  # 10% of screen height between buttons
        
        # New Game button
        self.ui_manager.add_element(Button(
            button_x, 
            button_start_y, 
            button_width, 
            button_height, 
            "New Game", 
            lambda: start_new_game_callback()
        ))
        
        # Load Game button
        load_btn = Button(
            button_x, 
            button_start_y + button_spacing, 
            button_width, 
            button_height, 
            "Load Game", 
            lambda: load_game_callback()
        )
        load_btn.enabled = self.game.save_manager.save_exists()
        self.ui_manager.add_element(load_btn)
        
        # Settings button
        self.ui_manager.add_element(Button(
            button_x, 
            button_start_y + button_spacing * 2, 
            button_width, 
            button_height, 
            "Settings", 
            lambda: settings_callback()
        ))
        
        # Exit button
        self.ui_manager.add_element(Button(
            button_x, 
            button_start_y + button_spacing * 3, 
            button_width, 
            button_height, 
            "Exit", 
            lambda: exit_game_callback()
        ))
        
    def build_character_ui(self, player):
        from .game import GameState
        
        # Title - positioned at 5% from top, 5% from left
        title_y = int(self.screen_height * 0.05)
        title_x = int(self.screen_width * 0.05)
        self.ui_manager.add_element(Label(title_x, title_y, "Character", (255, 215, 0), 36))
        
        # Character info - positioned using percentage-based layout
        info_x = int(self.screen_width * 0.1)
        name_y = int(self.screen_height * 0.15)
        level_y = int(self.screen_height * 0.20)
        hp_y = int(self.screen_height * 0.25)
        gold_y = int(self.screen_height * 0.30)
        exp_y = int(self.screen_height * 0.35)
        
        self.ui_manager.add_element(Label(info_x, name_y, f"Name: {player.name}", (220, 220, 220)))
        self.ui_manager.add_element(Label(info_x, level_y, f"Level: {player.level}", (220, 220, 220)))
        self.ui_manager.add_element(Label(info_x, hp_y, f"HP: {player.current_hp}/{player.max_hp}", (220, 220, 220)))
        
        # Gold display
        gold_color = (255, 215, 0)  # Gold color
        self.ui_manager.add_element(Label(info_x, gold_y, f"Gold: {player.gold}", gold_color))
        
        # Experience bar
        exp_label_x = info_x
        exp_bar_x = int(self.screen_width * 0.1)
        exp_bar_y = exp_y + 25
        exp_bar_width = int(self.screen_width * 0.4)  # 40% of screen width
        exp_bar_height = int(self.screen_height * 0.03)  # 3% of screen height
        
        # Add experience label
        self.ui_manager.add_element(Label(exp_label_x, exp_y, f"Experience: {player.experience}/{player.experience_to_level}", (173, 216, 230)))
        
        # Calculate experience percentage
        exp_percentage = player.experience / player.experience_to_level if player.experience_to_level > 0 else 0
        
        # Add experience progress bar
        exp_bar = ProgressBar(exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height, exp_percentage, (0, 191, 255))
        self.ui_manager.add_element(exp_bar)
        
        # Navigation buttons - positioned at right side
        button_width = int(self.screen_width * 0.2)  # 20% of screen width
        button_height = int(self.screen_height * 0.07)  # 7% of screen height
        button_x = int(self.screen_width * 0.95 - button_width)  # 5% from right edge
        
        # Position buttons evenly in the right side of the screen
        button_start_y = int(self.screen_height * 0.15)  # Start at 15% of screen height
        button_spacing = int(self.screen_height * 0.09)  # 9% of screen height between buttons
        
        # Equipment button
        self.ui_manager.add_element(Button(
            button_x, 
            button_start_y, 
            button_width, 
            button_height, 
            "Equipment", 
            lambda: self.game.change_state(GameState.EQUIPMENT)
        ))
        
        # Skills button                        
        self.ui_manager.add_element(Button(
            button_x, 
            button_start_y + button_spacing, 
            button_width, 
            button_height, 
            "Skills", 
            lambda: self.game.change_state(GameState.SKILLS)
        ))
        
        # Settings button
        self.ui_manager.add_element(Button(
            button_x, 
            button_start_y + button_spacing * 2, 
            button_width, 
            button_height, 
            "Settings", 
            lambda: self.game.change_state(GameState.SETTINGS)
        ))
                                
        # Combat button                         
        self.ui_manager.add_element(Button(
            button_x, 
            button_start_y + button_spacing * 3, 
            button_width, 
            button_height, 
            "Combat", 
            lambda: self.game.change_state(GameState.COMBAT_SETUP)
        ))
    
    def build_equipment_ui(self, player):
        from .game import GameState
        
        # Title - positioned at 5% from top, 5% from left
        title_y = int(self.screen_height * 0.05)
        title_x = int(self.screen_width * 0.05)
        self.ui_manager.add_element(Label(title_x, title_y, "Equipment", (255, 215, 0), 36))
        
        # Equipment items - start at 15% from top, 10% from left
        item_x = int(self.screen_width * 0.1)
        start_y = int(self.screen_height * 0.15)
        item_spacing = int(self.screen_height * 0.07)  # 7% of screen height
        
        if player and player.equipment:
            y_pos = start_y
            for slot, item in player.equipment.items():
                item_name = item.name if item else "Empty"
                self.ui_manager.add_element(Label(item_x, y_pos, f"{slot}: {item_name}", (220, 220, 220)))
                y_pos += item_spacing
        
        # Back button - positioned at top right
        button_width = int(self.screen_width * 0.2)  # 20% of screen width
        button_height = int(self.screen_height * 0.07)  # 7% of screen height
        button_x = int(self.screen_width * 0.95 - button_width)  # 5% from right edge
        
        self.ui_manager.add_element(Button(
            button_x, 
            title_y, 
            button_width, 
            button_height, 
            "Back", 
            lambda: self.game.change_state(GameState.CHARACTER)
        ))
    
    def build_skills_ui(self, player):
        from .game import GameState
        
        # Title - positioned at 5% from top, 5% from left
        title_y = int(self.screen_height * 0.05)
        title_x = int(self.screen_width * 0.05)
        self.ui_manager.add_element(Label(title_x, title_y, "Combat Skills", (255, 215, 0), 36))
        
        # Skills list - start at 15% from top, 10% from left
        skill_x = int(self.screen_width * 0.1)
        start_y = int(self.screen_height * 0.15)
        skill_spacing = int(self.screen_height * 0.07)  # 7% of screen height
        
        if player and player.skills:
            y_pos = start_y
            for skill in player.skills:
                self.ui_manager.add_element(Label(skill_x, y_pos, f"{skill.name} - {skill.description}", (220, 220, 220)))
                y_pos += skill_spacing
        
        # Back button - positioned at top right
        button_width = int(self.screen_width * 0.2)  # 20% of screen width
        button_height = int(self.screen_height * 0.07)  # 7% of screen height
        button_x = int(self.screen_width * 0.95 - button_width)  # 5% from right edge
        
        self.ui_manager.add_element(Button(
            button_x, 
            title_y, 
            button_width, 
            button_height, 
            "Back", 
            lambda: self.game.change_state(GameState.CHARACTER)
        ))
        
    def build_combat_setup_ui(self, add_skill_callback, remove_skill_callback, start_combat_callback):
        from .game import GameState
        
        # Title - positioned at 5% from top, 5% from left
        title_y = int(self.screen_height * 0.05)
        title_x = int(self.screen_width * 0.05)
        self.ui_manager.add_element(Label(title_x, title_y, "Combat Setup", (255, 215, 0), 36))
        
        # Labels for sections
        label_y = int(self.screen_height * 0.15)
        left_label_x = int(self.screen_width * 0.1)
        right_label_x = int(self.screen_width * 0.55)
        
        self.ui_manager.add_element(Label(left_label_x, label_y, "Configure your combat sequence:", (220, 220, 220)))
        
        # Calculate dimensions for scrollable lists
        list_width = int(self.screen_width * 0.4)  # 40% of screen width
        list_height = int(self.screen_height * 0.5)  # 50% of screen height
        list_y = int(self.screen_height * 0.2)  # 20% from top
        left_list_x = int(self.screen_width * 0.05)  # 5% from left
        right_list_x = int(self.screen_width * 0.55)  # 55% from left
        item_height = int(self.screen_height * 0.07)  # 7% of screen height
        
        # Create a scrollable list for the combat sequence
        sequence_list = ScrollableList(left_list_x, list_y, list_width, list_height, item_height)
        self.ui_manager.add_element(sequence_list)
        self.ui_manager.sequence_list = sequence_list  # Store reference for drag-drop updates
        
        # Add current combat sequence to the scrollable list
        if self.game.player and self.game.player.combat_sequence:
            for i, skill in enumerate(self.game.player.combat_sequence):
                if skill:  # Skip None entries
                    # Create a container for the skill and remove button
                    class SkillListItem:
                        def __init__(self, skill, index, remove_callback):
                            self.skill = skill
                            self.index = index
                            self.remove_callback = remove_callback
                            self.name = f"{index+1}. {skill.name}"
                        
                        def render_in_list(self, surface, x, y, width, height):
                            # Draw skill name
                            font = pygame.font.SysFont(None, 24)
                            text = font.render(self.name, True, (220, 220, 220))
                            surface.blit(text, (x + 10, y + (height - text.get_height()) // 2))
                            
                            # Draw remove button
                            button_width = 80
                            button_height = 30
                            button_x = x + width - button_width - 10
                            button_y = y + (height - button_height) // 2
                            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                            
                            # Button background
                            pygame.draw.rect(surface, (100, 100, 200), button_rect)
                            
                            # Button text
                            button_font = pygame.font.SysFont(None, 20)
                            button_text = button_font.render("Remove", True, (255, 255, 255))
                            text_x = button_x + (button_width - button_text.get_width()) // 2
                            text_y = button_y + (button_height - button_text.get_height()) // 2
                            surface.blit(button_text, (text_x, text_y))
                    
                    item = SkillListItem(skill, i, lambda idx=i: remove_skill_callback(idx))
                    sequence_list.add_item(item)
        
        # Available skills section
        self.ui_manager.add_element(Label(right_label_x, label_y, "Available Skills:", (220, 220, 220)))
        
        # Create a scrollable list for available skills
        skills_list = ScrollableList(right_list_x, list_y, list_width, list_height, item_height)
        self.ui_manager.add_element(skills_list)
        
        # Add available skills to the scrollable list
        if self.game.player and self.game.player.skills:
            for i, skill in enumerate(self.game.player.skills):
                # Allow all skills to be added (remove the filter)
                class AvailableSkillItem:
                    def __init__(self, skill, add_callback):
                        self.skill = skill
                        self.add_callback = add_callback
                        self.name = skill.name
                    
                    def render_in_list(self, surface, x, y, width, height):
                        # Draw skill name
                        font = pygame.font.SysFont(None, 24)
                        text = font.render(self.name, True, (220, 220, 220))
                        surface.blit(text, (x + 10, y + (height - text.get_height()) // 2))
                        
                        # Draw add button
                        button_width = 80
                        button_height = 30
                        button_x = x + width - button_width - 10
                        button_y = y + (height - button_height) // 2
                        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                        
                        # Button background
                        pygame.draw.rect(surface, (100, 200, 100), button_rect)
                        
                        # Button text
                        button_font = pygame.font.SysFont(None, 20)
                        button_text = button_font.render("Add", True, (255, 255, 255))
                        text_x = button_x + (button_width - button_text.get_width()) // 2
                        text_y = button_y + (button_height - button_text.get_height()) // 2
                        surface.blit(button_text, (text_x, text_y))
                
                item = AvailableSkillItem(skill, add_skill_callback)
                skills_list.add_item(item)
        
        # Start Combat button - centered at bottom
        button_width = int(self.screen_width * 0.2)  # 20% of screen width
        button_height = int(self.screen_height * 0.07)  # 7% of screen height
        start_button_x = int(self.screen_width * 0.5 - button_width * 0.5)  # Centered horizontally
        start_button_y = int(self.screen_height * 0.85)  # 85% from top
        
        self.ui_manager.add_element(Button(
            start_button_x, 
            start_button_y, 
            button_width, 
            button_height, 
            "Start Combat", 
            lambda: start_combat_callback()
        ))
        
        # Back button - positioned at top right
        back_button_x = int(self.screen_width * 0.95 - button_width)  # 5% from right edge
        
        self.ui_manager.add_element(Button(
            back_button_x, 
            title_y, 
            button_width, 
            button_height, 
            "Back", 
            lambda: self.game.change_state(GameState.CHARACTER)
        ))
    
    def build_combat_ui(self):
        from .game import GameState
        
        player = self.game.player
        enemy = self.game.combat_manager.current_enemy
        action_manager = self.game.combat_manager.action_manager
        
        # Title - positioned at 5% from top, centered horizontally
        title_y = int(self.screen_height * 0.05)
        title_x = int(self.screen_width * 0.5)
        self.ui_manager.add_element(Label(title_x - 50, title_y, "Combat", (255, 0, 0), 36))
        
        # Calculate section positions and sizes using percentages
        section_width = int(self.screen_width * 0.25)  # 25% of screen width
        bar_height = int(self.screen_height * 0.03)  # 3% of screen height
        
        # Player section - left side (10% from left, 15% from top)
        player_section_x = int(self.screen_width * 0.1)
        player_section_y = int(self.screen_height * 0.15)
        label_spacing = int(self.screen_height * 0.05)  # 5% of screen height
        
        # Player info
        self.ui_manager.add_element(Label(player_section_x, player_section_y, f"{player.name}", (220, 220, 220), 28))
        self.ui_manager.add_element(Label(
            player_section_x, 
            player_section_y + label_spacing, 
            f"HP: {player.current_hp}/{player.max_hp}", 
            (220, 220, 220)
        ))
        
        # Player HP bar
        hp_bar_y = player_section_y + label_spacing * 2
        hp_ratio = max(0, min(1, player.current_hp / player.max_hp))
        player_hp_bar = self.ui_manager.add_element(ProgressBar(
            player_section_x, 
            hp_bar_y, 
            section_width, 
            bar_height, 
            hp_ratio, 
            (0, 200, 0)
        ))
        
        # Player AP bar
        player_action = 0.0
        if action_manager and hasattr(player, 'id'):
            player_action = action_manager.get_current_action(player.id)
        
        max_ap = 20.0
        ap_ratio = max(0, min(1, player_action / max_ap))
        ap_bar_y = hp_bar_y + label_spacing
        player_ap_bar = self.ui_manager.add_element(ProgressBar(
            player_section_x, 
            ap_bar_y, 
            section_width, 
            bar_height, 
            ap_ratio, 
            (100, 200, 255)
        ))
        
        self.ui_manager.add_element(Label(
            player_section_x, 
            ap_bar_y + bar_height + int(self.screen_height * 0.01), 
            f"AP: {player_action:.1f}/{max_ap}", 
            (100, 200, 255), 
            20
        ))
        
        # Enemy section - right side (65% from left, 15% from top)
        enemy_section_x = int(self.screen_width * 0.65)
        enemy_section_y = int(self.screen_height * 0.15)
        
        # Enemy info
        self.ui_manager.add_element(Label(enemy_section_x, enemy_section_y, f"{enemy.name}", (220, 100, 100), 28))
        self.ui_manager.add_element(Label(
            enemy_section_x, 
            enemy_section_y + label_spacing, 
            f"HP: {enemy.current_hp}/{enemy.max_hp}", 
            (220, 100, 100)
        ))
        
        # Enemy HP bar
        enemy_hp_bar_y = enemy_section_y + label_spacing * 2
        hp_ratio = max(0, min(1, enemy.current_hp / enemy.max_hp))
        enemy_hp_bar = self.ui_manager.add_element(ProgressBar(
            enemy_section_x, 
            enemy_hp_bar_y, 
            section_width, 
            bar_height, 
            hp_ratio, 
            (200, 0, 0)
        ))
        
        # Enemy AP bar
        enemy_action = 0.0
        if enemy and action_manager and hasattr(enemy, 'id'):
            enemy_action = action_manager.get_current_action(enemy.id)
        
        ap_ratio = max(0, min(1, enemy_action / max_ap))
        enemy_ap_bar_y = enemy_hp_bar_y + label_spacing
        enemy_ap_bar = self.ui_manager.add_element(ProgressBar(
            enemy_section_x, 
            enemy_ap_bar_y, 
            section_width, 
            bar_height, 
            ap_ratio, 
            (255, 150, 100)
        ))
        
        self.ui_manager.add_element(Label(
            enemy_section_x, 
            enemy_ap_bar_y + bar_height + int(self.screen_height * 0.01), 
            f"AP: {enemy_action:.1f}/{max_ap}", 
            (255, 150, 100), 
            20
        ))
        
        # Add enemy logo (hardcoded to goblin for now)
        enemy_image = self.ui_manager.asset_manager.get_image(AssetType.ENEMY_GOBLIN)
        if enemy_image:
            image_size = int(self.screen_height * 0.12)  # 12% of screen height
            enemy_image = pygame.transform.scale(enemy_image, (image_size, image_size))
            image_x = enemy_section_x + int(section_width * 0.3)  # 30% of section width
            image_y = enemy_ap_bar_y + label_spacing * 1.5
            self.ui_manager.enemy_image = enemy_image
            self.ui_manager.enemy_image_pos = (image_x, image_y)
        
        # Combat log section - bottom (70% from top)
        log_section_y = int(self.screen_height * 0.7)
        log_section_x = int(self.screen_width * 0.1)  # 10% from left
        self.ui_manager.add_element(Label(log_section_x, log_section_y, "Combat Log:", (180, 180, 220), 24))
        
        # Draw a semi-transparent background for the combat log
        log_width = int(self.screen_width * 0.8)  # 80% of screen width
        log_height = int(self.screen_height * 0.2)  # 20% of screen height
        log_bg = pygame.Surface((log_width, log_height))
        log_bg.set_alpha(50)
        log_bg.fill((50, 50, 70))
        log_bg_y = log_section_y + int(self.screen_height * 0.03)  # 3% of screen height
        self.game.screen.blit(log_bg, (log_section_x, log_bg_y))
        
        # Display the most recent combat log messages
        log_y = log_bg_y + int(self.screen_height * 0.02)  # 2% of screen height
        log_entry_spacing = int(self.screen_height * 0.03)  # 3% of screen height
        log_text_x = log_section_x + int(self.screen_width * 0.02)  # 2% of screen width
        
        # Show fewer messages to prevent overflow
        recent_messages = self.game.combat_manager.combat_log[-5:]
        for message in recent_messages:
            self.ui_manager.add_element(Label(log_text_x, log_y, message, (200, 200, 240)))
            log_y += log_entry_spacing
    
    def build_game_over(self):
        from .game import GameState
        
        title_y = int(self.screen_height * 0.2)  # 20% from top
        title_x = int(self.screen_width * 0.5)  # Centered horizontally
        self.ui_manager.add_element(Label(title_x - 100, title_y, "Game Over", (255, 0, 0), 48))
        
        victory = False
        if hasattr(self.game, 'combat_manager') and hasattr(self.game.combat_manager, 'victory'):
            victory = self.game.combat_manager.victory
            
        result_message = "Victory!" if victory else "Defeat..."
        result_y = int(self.screen_height * 0.35)  # 35% from top
        self.ui_manager.add_element(Label(
            title_x - 50, 
            result_y, 
            result_message, 
            (0, 255, 0) if victory else (255, 0, 0), 
            36
        ))
        
        button_width = int(self.screen_width * 0.25)  # 25% of screen width
        button_height = int(self.screen_height * 0.08)  # 8% of screen height
        button_x = int(self.screen_width * 0.5 - button_width * 0.5)  # Centered horizontally
        button_y = int(self.screen_height * 0.55)  # 55% from top
        
        self.ui_manager.add_element(Button(
            button_x, 
            button_y, 
            button_width, 
            button_height, 
            "Continue", 
            lambda: self.game.change_state(GameState.CHARACTER)
        ))
    
    def build_world_map_ui(self):
        from .game import GameState
        
        # Title - positioned at 5% from top, centered horizontally
        title_y = int(self.screen_height * 0.05)
        title_x = int(self.screen_width * 0.5)
        self.ui_manager.add_element(Label(title_x - 70, title_y, "World Map", (255, 215, 0), 36))
        
        # Map background - use percentage-based positioning and sizing
        map_margin_h = int(self.screen_width * 0.05)  # 5% horizontal margin
        map_margin_v = int(self.screen_height * 0.15)  # 15% vertical margin from top
        map_bottom_margin = int(self.screen_height * 0.1)  # 10% margin from bottom
        
        map_rect = pygame.Rect(
            map_margin_h, 
            map_margin_v, 
            self.screen_width - (map_margin_h * 2), 
            self.screen_height - map_margin_v - map_bottom_margin
        )
        
        map_surface = pygame.Surface((map_rect.width, map_rect.height))
        map_surface.fill((50, 50, 80))
        
        # Draw a grid on the map - grid size based on screen dimensions
        grid_size = int(self.screen_width * 0.05)  # 5% of screen width
        for x in range(0, map_rect.width, grid_size):
            pygame.draw.line(map_surface, (70, 70, 100), (x, 0), (x, map_rect.height))
        for y in range(0, map_rect.height, grid_size):
            pygame.draw.line(map_surface, (70, 70, 100), (0, y), (map_rect.width, y))
        
        # Store map surface for rendering in the UIManager's update method
        self.ui_manager.map_surface = map_surface
        self.ui_manager.map_rect = map_rect
        
        # Define locations with percentage-based positions
        # Positions are relative to the map surface (0-1 range)
        locations = [
            {"name": "Town", "pos": (0.15, 0.2), "color": (0, 200, 0)},
            {"name": "Forest", "pos": (0.4, 0.3), "color": (0, 150, 0)},
            {"name": "Mountain", "pos": (0.7, 0.4), "color": (150, 150, 150)},
            {"name": "Cave", "pos": (0.3, 0.6), "color": (100, 100, 100)},
            {"name": "Dungeon", "pos": (0.6, 0.7), "color": (150, 0, 0)}
        ]
        
        # Location button dimensions
        loc_button_width = int(self.screen_width * 0.1)  # 10% of screen width
        loc_button_height = int(self.screen_height * 0.06)  # 6% of screen height
        
        for location in locations:
            # Convert percentage positions to actual pixel positions on the map
            pos_x = int(map_rect.width * location["pos"][0])
            pos_y = int(map_rect.height * location["pos"][1])
            
            # Calculate button position (centered on the location point)
            loc_x = map_rect.x + pos_x - loc_button_width // 2
            loc_y = map_rect.y + pos_y - loc_button_height // 2
            
            # Add a button for the location
            self.ui_manager.add_element(Button(
                loc_x, loc_y, loc_button_width, loc_button_height, location["name"],
                lambda loc=location["name"]: self.game.travel_to(loc)
            ))
        
        # Add character button - positioned at top right
        button_width = int(self.screen_width * 0.15)  # 15% of screen width
        button_height = int(self.screen_height * 0.07)  # 7% of screen height
        button_x = int(self.screen_width * 0.95 - button_width)  # 5% from right edge
        
        self.ui_manager.add_element(Button(
            button_x, title_y, button_width, button_height, "Character",
            lambda: self.game.change_state(GameState.CHARACTER)
        ))
        
    def build_settings_ui(self):
        from .game import GameState
        from .ui_elements import Slider
        
        # Title - positioned at 5% from top, centered horizontally
        title_y = int(self.screen_height * 0.05)
        title_x = int(self.screen_width * 0.5)
        self.ui_manager.add_element(Label(title_x - 50, title_y, "Settings", (255, 215, 0), 36))
        
        # Volume sliders - use percentages for sizing and positioning
        slider_width = int(self.screen_width * 0.4)  # 40% of screen width
        slider_height = int(self.screen_height * 0.05)  # 5% of screen height
        slider_x = int(self.screen_width * 0.5 - slider_width * 0.5)  # Centered horizontally
        
        # Start at 20% from top
        start_y = int(self.screen_height * 0.2)
        # Space sliders by 10% of screen height
        spacing = int(self.screen_height * 0.1)
        
        # Master volume
        master_slider = Slider(
            slider_x, start_y, slider_width, slider_height,
            min_value=0.0, max_value=1.0, initial_value=self.game.audio_manager.master_volume,
            callback=self.game.audio_manager.set_master_volume,
            label="Master Volume"
        )
        master_slider.ui_manager = self.ui_manager
        self.ui_manager.add_element(master_slider)
        
        # Music volume
        music_slider = Slider(
            slider_x, start_y + spacing, slider_width, slider_height,
            min_value=0.0, max_value=1.0, initial_value=self.game.audio_manager.music_volume,
            callback=self.game.audio_manager.set_music_volume,
            label="Music Volume"
        )
        music_slider.ui_manager = self.ui_manager
        self.ui_manager.add_element(music_slider)
        
        # UI sounds volume
        ui_slider = Slider(
            slider_x, start_y + spacing * 2, slider_width, slider_height,
            min_value=0.0, max_value=1.0, initial_value=self.game.audio_manager.ui_volume,
            callback=self.game.audio_manager.set_ui_volume,
            label="UI Sounds Volume"
        )
        ui_slider.ui_manager = self.ui_manager
        self.ui_manager.add_element(ui_slider)
        
        # Sound effects volume
        sfx_slider = Slider(
            slider_x, start_y + spacing * 3, slider_width, slider_height,
            min_value=0.0, max_value=1.0, initial_value=self.game.audio_manager.sfx_volume,
            callback=self.game.audio_manager.set_sfx_volume,
            label="Sound Effects Volume"
        )
        sfx_slider.ui_manager = self.ui_manager
        self.ui_manager.add_element(sfx_slider)
        
        # Test sound buttons
        button_width = int(self.screen_width * 0.15)  # 15% of screen width
        button_height = int(self.screen_height * 0.05)  # 5% of screen height
        button_spacing = int(button_width * 0.2)  # 20% of button width
        
        # Position test buttons at 70% from top
        test_buttons_y = int(self.screen_height * 0.7)
        
        # Test UI sound button - positioned at left side of center
        ui_button_x = int(self.screen_width * 0.5 - button_width - button_spacing * 0.5)
        self.ui_manager.add_element(Button(
            ui_button_x, test_buttons_y, button_width, button_height,
            "Test UI Sound",
            lambda: self.game.audio_manager.play_ui_click()
        ))
        
        # Test combat sound button - positioned at right side of center
        combat_button_x = int(self.screen_width * 0.5 + button_spacing * 0.5)
        self.ui_manager.add_element(Button(
            combat_button_x, test_buttons_y, button_width, button_height,
            "Test Combat Sound",
            lambda: self.game.audio_manager.play_attack_sound()
        ))
        
        # Back button - positioned at 85% from top, centered horizontally
        back_button_y = int(self.screen_height * 0.85)
        back_button_x = int(self.screen_width * 0.5 - button_width * 0.5)
        self.ui_manager.add_element(Button(
            back_button_x, back_button_y, button_width, button_height, 
            "Back",
            lambda: self.game.change_state(self.game.previous_state)
        ))
        
    def build_end_combat_ui(self):
        from .game import GameState
        
        # Get combat manager and check if player won or lost
        combat_manager = self.game.combat_manager
        victory = combat_manager.victory if combat_manager else False
        
        # Title - positioned at top center
        title_y = int(self.screen_height * 0.1)
        title_x = int(self.screen_width * 0.5)
        
        # Set title based on victory or defeat
        if victory:
            self.ui_manager.add_element(Label(title_x - 100, title_y, "Victory!", (50, 205, 50), 48))
        else:
            # Display YOU HAVE DIED in large red letters
            self.ui_manager.add_element(Label(title_x - 200, title_y, "YOU HAVE DIED", (255, 0, 0), 72))
        
        # Display rewards if victorious
        if victory and combat_manager and hasattr(combat_manager, 'rewards'):
            rewards_y = int(self.screen_height * 0.3)
            rewards_x = int(self.screen_width * 0.5)
            
            # Experience gained
            if 'experience' in combat_manager.rewards:
                exp_text = f"Experience Gained: {combat_manager.rewards['experience']}"
                self.ui_manager.add_element(Label(rewards_x - 150, rewards_y, exp_text, (220, 220, 220), 28))
            
            # Gold gained
            if 'gold' in combat_manager.rewards:
                gold_text = f"Gold Gained: {combat_manager.rewards['gold']}"
                self.ui_manager.add_element(Label(rewards_x - 150, rewards_y + 40, gold_text, (255, 215, 0), 28))
            
            # Items gained
            if 'items' in combat_manager.rewards and combat_manager.rewards['items']:
                items_text = "Items Found: " + ", ".join(item.name for item in combat_manager.rewards['items'])
                self.ui_manager.add_element(Label(rewards_x - 150, rewards_y + 80, items_text, (173, 216, 230), 24))
            
            # Level up notification if player leveled up
            if hasattr(self.game.player, 'level') and self.game.player.level > 1:
                level_text = f"Level: {self.game.player.level}"
                self.ui_manager.add_element(Label(rewards_x - 150, rewards_y + 120, level_text, (255, 165, 0), 32))
        
        # Continue button - positioned at bottom center
        button_width = int(self.screen_width * 0.25)
        button_height = int(self.screen_height * 0.07)
        button_x = int(self.screen_width * 0.5 - button_width * 0.5)
        button_y = int(self.screen_height * 0.8)
        
        self.ui_manager.add_element(Button(
            button_x, button_y, button_width, button_height,
            "Continue",
            lambda: self.game.change_state(GameState.CHARACTER)
        ))
