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
        # Position buttons in the lower part of the screen to not overlap with title image
        button_width = 200
        button_height = 40
        button_x = self.screen_width // 2 - button_width // 2
        
        # Add game title and subtitle only if no title image
        if not self.ui_manager.asset_manager.get_image(AssetType.TITLE_SCREEN):
            self.ui_manager.add_element(Label(self.screen_width // 2 - 150, 100, "Project Donut", (255, 215, 0), 48))
            self.ui_manager.add_element(Label(self.screen_width // 2 - 100, 170, "Fantasy RPG", (220, 220, 220), 32))
        
        # Position buttons at the bottom third of the screen
        start_y = self.screen_height - 200
        
        self.ui_manager.add_element(Button(button_x, start_y, button_width, button_height, "New Game", 
                                lambda: start_new_game_callback()))
        
        load_btn = Button(button_x, start_y + 60, button_width, button_height, "Load Game", 
                          lambda: load_game_callback())
        load_btn.enabled = self.game.save_manager.save_exists()
        self.ui_manager.add_element(load_btn)
        
        self.ui_manager.add_element(Button(button_x, start_y + 120, button_width, button_height, "Settings", 
                                lambda: settings_callback()))
        
        self.ui_manager.add_element(Button(button_x, start_y + 180, button_width, button_height, "Exit", 
                                lambda: exit_game_callback()))
        
    def build_character_ui(self, player):
        self.ui_manager.add_element(Label(20, 20, "Character", (255, 215, 0), 36))
        
        self.ui_manager.add_element(Label(50, 80, f"Name: {player.name}", (220, 220, 220)))
        self.ui_manager.add_element(Label(50, 120, f"Level: {player.level}", (220, 220, 220)))
        self.ui_manager.add_element(Label(50, 160, f"HP: {player.current_hp}/{player.max_hp}", (220, 220, 220)))
        
        from .game import GameState
        self.ui_manager.add_element(Button(self.screen_width - 180, 20, 160, 40, "Equipment", 
                                lambda: self.game.change_state(GameState.EQUIPMENT)))
                                
        self.ui_manager.add_element(Button(self.screen_width - 180, 70, 160, 40, "Skills", 
                                lambda: self.game.change_state(GameState.SKILLS)))
                                
        self.ui_manager.add_element(Button(self.screen_width - 180, 120, 160, 40, "Combat", 
                                lambda: self.game.change_state(GameState.COMBAT_SETUP)))
    
    def build_equipment_ui(self, player):
        self.ui_manager.add_element(Label(20, 20, "Equipment", (255, 215, 0), 36))
        
        if player and player.equipment:
            y_pos = 80
            for slot, item in player.equipment.items():
                item_name = item.name if item else "Empty"
                self.ui_manager.add_element(Label(50, y_pos, f"{slot}: {item_name}", (220, 220, 220)))
                y_pos += 40
        
        from .game import GameState
        self.ui_manager.add_element(Button(self.screen_width - 180, 20, 160, 40, "Back", 
                                lambda: self.game.change_state(GameState.CHARACTER)))
    
    def build_skills_ui(self, player):
        self.ui_manager.add_element(Label(20, 20, "Combat Skills", (255, 215, 0), 36))
        
        if player and player.skills:
            y_pos = 80
            for skill in player.skills:
                self.ui_manager.add_element(Label(50, y_pos, f"{skill.name} - {skill.description}", (220, 220, 220)))
                y_pos += 40
        
        from .game import GameState
        self.ui_manager.add_element(Button(self.screen_width - 180, 20, 160, 40, "Back", 
                                lambda: self.game.change_state(GameState.CHARACTER)))
        
    def build_combat_setup_ui(self, add_skill_callback, remove_skill_callback, start_combat_callback):
        self.ui_manager.add_element(Label(20, 20, "Combat Setup", (255, 215, 0), 36))
        
        self.ui_manager.add_element(Label(50, 80, "Configure your combat sequence:", (220, 220, 220)))
        
        # Create a scrollable list for the combat sequence
        sequence_list = ScrollableList(50, 120, 330, 300, 40)
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
        self.ui_manager.add_element(Label(400, 80, "Available Skills:", (220, 220, 220)))
        
        # Create a scrollable list for available skills
        skills_list = ScrollableList(400, 120, 330, 300, 40)
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
        
        self.ui_manager.add_element(Button(self.screen_width // 2 - 80, self.screen_height - 120, 160, 40, "Start Combat", 
                                lambda: start_combat_callback()))
                                
        from .game import GameState
        self.ui_manager.add_element(Button(self.screen_width - 180, 20, 160, 40, "Back", 
                                lambda: self.game.change_state(GameState.CHARACTER)))
    
    def build_combat_ui(self):
        from .game import GameState
        
        # Get screen dimensions for layout calculations
        screen_width, screen_height = self.screen_width, self.screen_height
        
        # Title
        self.ui_manager.add_element(Label(screen_width // 2 - 50, 20, "Combat", (255, 0, 0), 36))
        
        player = self.game.player
        enemy = self.game.combat_manager.current_enemy
        action_manager = self.game.combat_manager.action_manager
        
        # Player section - left side
        player_section_x = 50
        player_section_y = 80
        
        # Player info
        self.ui_manager.add_element(Label(player_section_x, player_section_y, f"{player.name}", (220, 220, 220), 28))
        self.ui_manager.add_element(Label(player_section_x, player_section_y + 40, f"HP: {player.current_hp}/{player.max_hp}", (220, 220, 220)))
        
        # Player HP bar
        hp_ratio = max(0, min(1, player.current_hp / player.max_hp))
        player_hp_bar = self.ui_manager.add_element(ProgressBar(player_section_x, player_section_y + 70, 200, 20, hp_ratio, (0, 200, 0)))
        
        # Player AP bar
        player_action = 0.0
        if action_manager and hasattr(player, 'id'):
            player_action = action_manager.get_current_action(player.id)
        
        max_ap = 20.0
        ap_ratio = max(0, min(1, player_action / max_ap))
        player_ap_bar = self.ui_manager.add_element(ProgressBar(player_section_x, player_section_y + 110, 200, 20, ap_ratio, (100, 200, 255)))
        self.ui_manager.add_element(Label(player_section_x, player_section_y + 135, f"AP: {player_action:.1f}/{max_ap}", (100, 200, 255), 20))
        
        # Enemy section - right side
        enemy_section_x = screen_width - 250
        enemy_section_y = 80
        
        # Enemy info
        self.ui_manager.add_element(Label(enemy_section_x, enemy_section_y, f"{enemy.name}", (220, 100, 100), 28))
        self.ui_manager.add_element(Label(enemy_section_x, enemy_section_y + 40, f"HP: {enemy.current_hp}/{enemy.max_hp}", (220, 100, 100)))
        
        # Enemy HP bar
        hp_ratio = max(0, min(1, enemy.current_hp / enemy.max_hp))
        enemy_hp_bar = self.ui_manager.add_element(ProgressBar(enemy_section_x, enemy_section_y + 70, 200, 20, hp_ratio, (200, 0, 0)))
        
        # Enemy AP bar
        enemy_action = 0.0
        if enemy and action_manager and hasattr(enemy, 'id'):
            enemy_action = action_manager.get_current_action(enemy.id)
        
        ap_ratio = max(0, min(1, enemy_action / max_ap))
        enemy_ap_bar = self.ui_manager.add_element(ProgressBar(enemy_section_x, enemy_section_y + 110, 200, 20, ap_ratio, (255, 150, 100)))
        self.ui_manager.add_element(Label(enemy_section_x, enemy_section_y + 135, f"AP: {enemy_action:.1f}/{max_ap}", (255, 150, 100), 20))
        
        # Add enemy logo (hardcoded to goblin for now)
        enemy_image = self.ui_manager.asset_manager.get_image(AssetType.ENEMY_GOBLIN)
        if enemy_image:
            enemy_image = pygame.transform.scale(enemy_image, (80, 80))
            # Add the enemy image as a direct render in the update method
            self.ui_manager.enemy_image = enemy_image
            self.ui_manager.enemy_image_pos = (enemy_section_x + 60, enemy_section_y + 160)
        
        # Combat log section - bottom
        log_section_y = screen_height - 220  # Move up to prevent cutoff
        self.ui_manager.add_element(Label(50, log_section_y, "Combat Log:", (180, 180, 220), 24))
        
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
            self.ui_manager.add_element(Label(70, log_y, message, (200, 200, 240)))
            log_y += 30
    
    def build_game_over(self):
        from .game import GameState
        self.ui_manager.add_element(Label(self.screen_width // 2 - 100, 100, "Game Over", (255, 0, 0), 48))
        
        victory = False
        if hasattr(self.game, 'combat_manager') and hasattr(self.game.combat_manager, 'victory'):
            victory = self.game.combat_manager.victory
            
        result_message = "Victory!" if victory else "Defeat..."
        self.ui_manager.add_element(Label(
            self.screen_width // 2 - 50, 
            200, 
            result_message, 
            (0, 255, 0) if victory else (255, 0, 0), 
            36
        ))
        
        self.ui_manager.add_element(Button(
            self.screen_width // 2 - 100, 
            300, 
            200, 
            50, 
            "Continue", 
            lambda: self.game.change_state(GameState.CHARACTER)
        ))
    
    def build_world_map_ui(self):
        from .game import GameState
        
        self.ui_manager.add_element(Label(20, 20, "World Map", (255, 215, 0), 36))
        
        # Map background
        map_rect = pygame.Rect(50, 80, self.screen_width - 100, self.screen_height - 200)
        map_surface = pygame.Surface((map_rect.width, map_rect.height))
        map_surface.fill((50, 50, 80))
        
        # Draw a grid on the map
        grid_size = 40
        for x in range(0, map_rect.width, grid_size):
            pygame.draw.line(map_surface, (70, 70, 100), (x, 0), (x, map_rect.height))
        for y in range(0, map_rect.height, grid_size):
            pygame.draw.line(map_surface, (70, 70, 100), (0, y), (map_rect.width, y))
        
        # Store map surface for rendering in the UIManager's update method
        self.ui_manager.map_surface = map_surface
        self.ui_manager.map_rect = map_rect
        
        # Add locations on the map
        locations = [
            {"name": "Town", "pos": (100, 100), "color": (0, 200, 0)},
            {"name": "Forest", "pos": (300, 150), "color": (0, 150, 0)},
            {"name": "Mountain", "pos": (500, 200), "color": (150, 150, 150)},
            {"name": "Cave", "pos": (200, 300), "color": (100, 100, 100)},
            {"name": "Dungeon", "pos": (400, 350), "color": (150, 0, 0)}
        ]
        
        for location in locations:
            # Create a button for each location
            loc_x = map_rect.x + location["pos"][0] - 40
            loc_y = map_rect.y + location["pos"][1] - 20
            
            # Add a button for the location
            self.ui_manager.add_element(Button(
                loc_x, loc_y, 80, 40, location["name"],
                lambda loc=location["name"]: self.game.travel_to(loc)
            ))
        
        # Add character button
        self.ui_manager.add_element(Button(
            self.screen_width - 180, 20, 160, 40, "Character",
            lambda: self.game.change_state(GameState.CHARACTER)
        ))
        
    def build_settings_ui(self):
        from .game import GameState
        from .ui_elements import Slider
        
        # Title
        self.ui_manager.add_element(Label(self.screen_width // 2 - 50, 20, "Settings", (255, 215, 0), 36))
        
        # Volume sliders
        slider_width = 300
        slider_height = 30
        slider_x = self.screen_width // 2 - slider_width // 2
        start_y = 100
        spacing = 60
        
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
        button_width = 120
        button_height = 30
        button_x = self.screen_width // 2 - button_width // 2
        
        # Test UI sound button
        self.ui_manager.add_element(Button(
            slider_x, start_y + spacing * 4, button_width, button_height,
            "Test UI Sound",
            lambda: self.game.audio_manager.play_ui_click()
        ))
        
        # Test combat sound button
        self.ui_manager.add_element(Button(
            slider_x + button_width + 20, start_y + spacing * 4, button_width, button_height,
            "Test Combat Sound",
            lambda: self.game.audio_manager.play_attack_sound()
        ))
        
        # Back button
        self.ui_manager.add_element(Button(
            self.screen_width // 2 - button_width // 2, start_y + spacing * 5,
            button_width, button_height, "Back",
            lambda: self.game.change_state(GameState.MAIN_MENU)
        ))
