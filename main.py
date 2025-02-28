#!/usr/bin/env python3
"""
Project Donut - Incremental Fantasy RPG
A simple proof of concept using pygame
"""
import pygame
import sys
import random
import os
import json

# Initialize pygame with mixer for audio
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BLUE = (100, 150, 255)
RED = (230, 80, 80)
GREEN = (80, 230, 80)
BG_COLOR = (30, 30, 50)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Donut - Fantasy RPG")
clock = pygame.time.Clock()

# Game states
MAIN_MENU = 0
CHARACTER = 1
COMBAT = 2
RESULTS = 3

# Initialize game state
game_state = MAIN_MENU

# Player stats
player = {
    "name": "Hero",
    "level": 1,
    "max_hp": 100,
    "current_hp": 100,
    "attack": 15,
    "defense": 5,
    "skills": ["Basic Attack", "Power Strike", "Heal", "Quick Strike"],
    "experience": 0,
    "next_level": 100,
    "gold": 50
}

# Enemy stats
enemy = {
    "name": "Goblin",
    "max_hp": 60,
    "current_hp": 60,
    "attack": 10,
    "defense": 3
}

# Combat sequence
combat_sequence = ["Basic Attack", "Power Strike", "Basic Attack"]
available_skills = ["Basic Attack", "Power Strike", "Heal", "Quick Strike"]
dragging_skill = None
drag_from_index = -1
combat_log = []
combat_finished = False
player_turn = True
victory = False

# Button class
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def draw(self):
        color = (120, 120, 220) if self.hovered else (80, 80, 180)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        font = pygame.font.SysFont(None, 32)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                # Play click sound before action
                if ui_click_sound:
                    ui_click_sound.play()
                self.action()
                return True
        return False

# Create buttons
new_game_btn = Button(SCREEN_WIDTH//2 - 100, 250, 200, 50, "New Game", lambda: start_new_game())
load_game_btn = Button(SCREEN_WIDTH//2 - 100, 320, 200, 50, "Load Game", lambda: load_game())
exit_btn = Button(SCREEN_WIDTH//2 - 100, 390, 200, 50, "Exit", lambda: sys.exit())
combat_btn = Button(SCREEN_WIDTH//2 - 100, 520, 200, 50, "Enter Combat", lambda: start_combat())
back_btn = Button(50, 500, 120, 40, "Back", lambda: go_to_character())
save_game_btn = Button(SCREEN_WIDTH - 170, 500, 120, 40, "Save Game", lambda: save_game())
continue_btn = Button(SCREEN_WIDTH//2 - 100, 500, 200, 50, "Continue", lambda: go_to_character())

# Save file path
save_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "player_save.json")

def save_game():
    """Save player data to a JSON file"""
    try:
        # Create a dictionary with all player data
        save_data = {
            "player": player,
            "combat_sequence": combat_sequence
        }
        
        # Write to file
        with open(save_file_path, 'w') as f:
            json.dump(save_data, f)
            
        # Show a quick message in the log
        temp_message = "Game saved successfully!"
        if 'combat_log' in globals() and isinstance(combat_log, list):
            combat_log.append(temp_message)
        print(temp_message)  # Also print to console
        
        # Play UI sound for feedback
        if ui_click_sound:
            ui_click_sound.play()
            
    except Exception as e:
        error_msg = f"Error saving game: {e}"
        print(error_msg)
        if 'combat_log' in globals() and isinstance(combat_log, list):
            combat_log.append(error_msg)

def load_game():
    """Load player data from a JSON file"""
    global player, combat_sequence, game_state
    
    if not os.path.exists(save_file_path):
        print("No save file found.")
        return False
        
    try:
        # Read from file
        with open(save_file_path, 'r') as f:
            save_data = json.load(f)
            
        # Update player and combat_sequence
        if "player" in save_data:
            player = save_data["player"]
        if "combat_sequence" in save_data:
            combat_sequence = save_data["combat_sequence"]
            
        # Switch to character screen
        game_state = CHARACTER
        
        # Play town music
        play_town_music()
        
        return True
        
    except Exception as e:
        error_msg = f"Error loading game: {e}"
        print(error_msg)
        return False

def draw_text(text, font_size, color, x, y):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def start_new_game():
    global game_state, player, combat_log
    
    # Reset player to starting values
    player["level"] = 1
    player["experience"] = 0
    player["next_level"] = 100
    player["gold"] = 50
    player["max_hp"] = 100
    player["current_hp"] = 100
    player["attack"] = 15
    player["defense"] = 5
    
    combat_log = []
    game_state = CHARACTER
    
    # Switch from menu music to town music
    play_town_music()

def start_combat():
    global game_state, enemy, combat_log, combat_finished, player_turn, victory, combat_sequence_index
    
    # Reset enemy
    enemy["current_hp"] = enemy["max_hp"]
    
    # Reset combat state
    combat_log = ["Combat started!"]
    combat_finished = False
    player_turn = True
    victory = False
    combat_sequence_index = 0  # Start from the first skill in sequence
    
    # Switch from town music to battle music
    play_battle_music()
    
    # Choose random enemy type based on player level
    enemy_type = random.choice(["Goblin", "Orc", "Skeleton"])
    enemy_level = max(1, player["level"] + random.randint(-1, 1))
    
    if enemy_type == "Goblin":
        enemy["name"] = f"Goblin Lv.{enemy_level}"
        enemy["max_hp"] = 40 + (enemy_level * 10)
        enemy["attack"] = 8 + (enemy_level * 2)
        enemy["defense"] = 2 + enemy_level
    elif enemy_type == "Orc":
        enemy["name"] = f"Orc Lv.{enemy_level}"
        enemy["max_hp"] = 60 + (enemy_level * 15)
        enemy["attack"] = 12 + (enemy_level * 3)
        enemy["defense"] = 3 + enemy_level
    elif enemy_type == "Skeleton":
        enemy["name"] = f"Skeleton Lv.{enemy_level}"
        enemy["max_hp"] = 30 + (enemy_level * 8)
        enemy["attack"] = 10 + (enemy_level * 2)
        enemy["defense"] = 5 + enemy_level
    
    enemy["current_hp"] = enemy["max_hp"]
    combat_log.append(f"A {enemy['name']} appears!")
    
    game_state = COMBAT

def execute_combat_turn():
    global combat_log, player, enemy, combat_finished, player_turn, victory, game_state, combat_sequence_index, current_music
    
    if combat_finished:
        return
    
    if player_turn:
        # Player attacks using the skill from the combat sequence
        if not combat_sequence:
            combat_log.append(f"{player['name']} has no skills configured!")
            player_turn = not player_turn
            return
            
        # Get the next skill in the sequence
        skill = combat_sequence[combat_sequence_index]
        damage = 0
        
        # Different skills have different effects
        if skill == "Basic Attack":
            damage = max(1, player["attack"] - enemy["defense"] + random.randint(-3, 3))
        elif skill == "Power Strike":
            # More powerful but with variability
            damage = max(1, int(player["attack"] * 1.5) - enemy["defense"] + random.randint(-2, 5))
        elif skill == "Heal":
            # Healing skill
            heal_amount = 20 + random.randint(0, 10)
            player["current_hp"] = min(player["max_hp"], player["current_hp"] + heal_amount)
            combat_log.append(f"{player['name']} uses Heal for {heal_amount} HP!")
            # Go to next skill in the sequence
            combat_sequence_index = (combat_sequence_index + 1) % len(combat_sequence)
            player_turn = False
            return
        elif skill == "Quick Strike":
            # Fast attack with chance for double hit
            damage = max(1, int(player["attack"] * 0.7) - enemy["defense"] + random.randint(-2, 2))
            
            # 30% chance for a second hit
            if random.random() < 0.3:
                second_damage = max(1, int(player["attack"] * 0.5) - enemy["defense"])
                damage += second_damage
                combat_log.append(f"{player['name']} uses Quick Strike for {damage} damage (Double Hit)!")
            else:
                combat_log.append(f"{player['name']} uses Quick Strike for {damage} damage!")
        else:
            # Default attack if skill not recognized
            damage = max(1, player["attack"] - enemy["defense"])
            combat_log.append(f"{player['name']} attacks for {damage} damage!")
            
        # Apply damage to enemy
        enemy["current_hp"] = max(0, enemy["current_hp"] - damage)
        
        # Show combat message if not already shown
        if skill != "Quick Strike":
            combat_log.append(f"{player['name']} uses {skill} for {damage} damage!")
        
        # Check if enemy defeated
        if enemy["current_hp"] <= 0:
            combat_log.append(f"{enemy['name']} was defeated!")
            combat_finished = True
            victory = True
            game_state = RESULTS
            
            # Play after combat music when enemy is defeated
            play_after_combat_music()
            
        # Go to next skill in the sequence
        combat_sequence_index = (combat_sequence_index + 1) % len(combat_sequence)
    else:
        # Enemy attacks
        damage = max(1, enemy["attack"] - player["defense"] + random.randint(-2, 2))
        player["current_hp"] = max(0, player["current_hp"] - damage)
        combat_log.append(f"{enemy['name']} attacks for {damage} damage!")
        
        # Check if player defeated
        if player["current_hp"] <= 0:
            combat_log.append(f"{player['name']} was defeated!")
            combat_finished = True
            victory = False
            game_state = RESULTS
            
            # Play after combat music when player is defeated
            play_after_combat_music()
    
    # Switch turns
    player_turn = not player_turn

def go_to_character():
    global game_state, rewards_applied, animation_start_time, exp_animation_progress, gold_animation_progress, animation_complete
    game_state = CHARACTER
    
    # Reset rewards and animation variables when returning to character screen
    rewards_applied = False
    animation_start_time = 0
    exp_animation_progress = 0
    gold_animation_progress = 0
    animation_complete = False
    
    # Play town music when returning to character screen
    play_town_music()

def draw_health_bar(x, y, width, height, current, maximum, color):
    outline_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, (50, 50, 50), outline_rect)
    
    if current > 0:
        fill_width = int((current / maximum) * width)
        fill_rect = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(screen, color, fill_rect)
    
    pygame.draw.rect(screen, WHITE, outline_rect, 2)
    
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"{current}/{maximum}", True, WHITE)
    text_rect = text.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text, text_rect)

def draw_main_menu():
    # Draw the title screen background image or fallback to solid color
    if title_screen_img:
        screen.blit(title_screen_img, (0, 0))
    else:
        screen.fill(BG_COLOR)
        
    # Draw title text and buttons over the background
    draw_text("Project Donut", 64, GOLD, SCREEN_WIDTH//2 - 160, 100)
    draw_text("Fantasy RPG", 36, WHITE, SCREEN_WIDTH//2 - 90, 170)
    new_game_btn.draw()
    load_game_btn.draw()
    exit_btn.draw()
    
    # Show message if no save file exists
    if not os.path.exists(save_file_path):
        draw_text("No save file found", 20, (150, 150, 150), SCREEN_WIDTH//2 - 80, 370)

def draw_skill_slot(index, x, y, width, height, skill=None):
    # Draw skill slot background
    slot_color = (60, 60, 100)
    if skill is None:
        slot_color = (40, 40, 60)
    pygame.draw.rect(screen, slot_color, pygame.Rect(x, y, width, height))
    pygame.draw.rect(screen, (100, 100, 150), pygame.Rect(x, y, width, height), 2)
    
    # Draw skill name if present
    if skill:
        font = pygame.font.SysFont(None, 24)
        text_surf = font.render(skill, True, WHITE)
        text_rect = text_surf.get_rect(center=(x + width//2, y + height//2))
        screen.blit(text_surf, text_rect)
    else:
        draw_text("Empty", 24, (150, 150, 150), x + 10, y + 10)
    
    # Draw the sequence number
    number_font = pygame.font.SysFont(None, 20)
    number_surf = number_font.render(f"{index+1}", True, GOLD)
    screen.blit(number_surf, (x + 5, y + 5))
        
def draw_skill_in_list(skill, x, y, width, height, is_dragging=False):
    # Background
    skill_color = (80, 80, 150)
    if is_dragging:
        skill_color = (120, 120, 220)
    pygame.draw.rect(screen, skill_color, pygame.Rect(x, y, width, height))
    pygame.draw.rect(screen, (180, 180, 255), pygame.Rect(x, y, width, height), 2)
    
    # Skill text
    font = pygame.font.SysFont(None, 24)
    text_surf = font.render(skill, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surf, text_rect)

def draw_character_screen():
    global dragging_skill, drag_from_index
    screen.fill(BG_COLOR)
    draw_text("Character", 48, GOLD, 20, 20)
    
    # Character stats
    draw_text(f"Name: {player['name']}", 32, WHITE, 50, 80)
    draw_text(f"Level: {player['level']} ({player['experience']}/{player['next_level']} XP)", 32, WHITE, 50, 120)
    draw_text(f"Gold: {player['gold']}", 32, GOLD, 50, 160)
    
    # Health bar
    draw_text("HP:", 32, WHITE, 50, 200)
    draw_health_bar(100, 205, 200, 25, player["current_hp"], player["max_hp"], GREEN)
    
    # Combat stats
    draw_text(f"Attack: {player['attack']}", 28, WHITE, 400, 80)
    draw_text(f"Defense: {player['defense']}", 28, WHITE, 400, 120)
    
    # Combat mechanics explanation
    draw_text("Combat: Skills execute in sequence order", 20, (180, 180, 220), 400, 160)
    draw_text("Strategy: Order skills for maximum effect", 20, (180, 180, 220), 400, 185)
    
    # Available skills list
    draw_text("Available Skills:", 32, WHITE, 50, 250)
    skill_list_x = 50
    skill_list_y = 290
    skill_width = 160
    skill_height = 36
    
    for i, skill in enumerate(player["skills"]):
        # Check if this is the skill being dragged
        is_dragging = dragging_skill == skill
        
        if not is_dragging:  # Only draw skills that aren't being dragged
            draw_skill_in_list(skill, skill_list_x, skill_list_y + i*45, skill_width, skill_height)
    
    # Combat sequence - Slots where skills can be dragged
    draw_text("Combat Sequence:", 32, WHITE, 400, 250)
    slot_width = 180
    slot_height = 36
    slot_x = 400
    slot_y = 290
    
    # Draw the sequence slots
    for i in range(5):  # Always show 5 slots for the sequence
        skill = None if i >= len(combat_sequence) else combat_sequence[i]
        draw_skill_slot(i, slot_x, slot_y + i*45, slot_width, slot_height, skill)
    
    # Draw the skill being dragged
    if dragging_skill:
        mouse_pos = pygame.mouse.get_pos()
        draw_skill_in_list(dragging_skill, mouse_pos[0] - skill_width//2, 
                          mouse_pos[1] - skill_height//2, skill_width, skill_height, True)
    
    # Instructions
    draw_text("Drag skills to build and reorder combat sequence", 20, (180, 180, 220), 50, 480)
    
    # Buttons
    combat_btn.draw()
    save_game_btn.draw()

def draw_combat_screen():
    screen.fill(BG_COLOR)
    draw_text("Combat", 48, RED, 20, 20)
    
    # Player info
    draw_text(player["name"], 36, WHITE, 50, 80)
    draw_health_bar(50, 120, 200, 30, player["current_hp"], player["max_hp"], GREEN)
    
    # Enemy info
    draw_text(enemy["name"], 36, RED, SCREEN_WIDTH - 200, 80)
    draw_health_bar(SCREEN_WIDTH - 250, 120, 200, 30, enemy["current_hp"], enemy["max_hp"], RED)
    
    # Combat sequence preview
    draw_text("Combat Sequence:", 24, (180, 180, 255), 50, 160)
    seq_width = 80
    seq_height = 30
    seq_spacing = 10
    seq_y = 190
    
    # Highlight the active skill in the sequence
    for i, skill in enumerate(combat_sequence):
        highlight = i == combat_sequence_index and player_turn and not combat_finished
        color = (120, 120, 220) if highlight else (80, 80, 150)
        pygame.draw.rect(screen, color, pygame.Rect(50 + i*(seq_width + seq_spacing), seq_y, seq_width, seq_height))
        pygame.draw.rect(screen, (180, 180, 255), pygame.Rect(50 + i*(seq_width + seq_spacing), seq_y, seq_width, seq_height), 2 if highlight else 1)
        
        font = pygame.font.SysFont(None, 20)
        text = skill[:10] + ".." if len(skill) > 10 else skill  # Truncate long skill names
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(50 + i*(seq_width + seq_spacing) + seq_width//2, seq_y + seq_height//2))
        screen.blit(text_surf, text_rect)
    
    # Combat log
    draw_text("Combat Log:", 30, (200, 200, 255), 50, 240)
    for i, message in enumerate(combat_log[-6:]):
        draw_text(message, 24, WHITE, 70, 280 + i*30)
        
    # Back button if combat is finished
    if combat_finished:
        back_btn.draw()

def apply_rewards():
    global player, rewards_applied, reward_exp, reward_gold, reward_level_up
    
    # If rewards have already been applied, just return the calculated values without applying again
    if rewards_applied:
        return reward_exp, reward_gold, reward_level_up
    
    if victory:
        # Calculate rewards based on enemy level
        enemy_level = int(enemy["name"].split(".")[1]) if "." in enemy["name"] else 1
        exp_reward = enemy_level * 25 + random.randint(10, 20)
        gold_reward = enemy_level * 15 + random.randint(5, 10)
        
        # Store calculated rewards to show consistent values
        reward_exp = exp_reward
        reward_gold = gold_reward
        
        # Apply rewards
        player["experience"] += exp_reward
        player["gold"] += gold_reward
        
        # Check for level up
        level_up = False
        if player["experience"] >= player["next_level"]:
            player["level"] += 1
            player["experience"] -= player["next_level"]
            player["next_level"] = int(player["next_level"] * 1.5)
            player["max_hp"] += 20
            player["current_hp"] = player["max_hp"]
            player["attack"] += 3
            player["defense"] += 2
            level_up = True
            
        reward_level_up = level_up
        return exp_reward, gold_reward, level_up
    
    return 0, 0, False

def draw_results_screen():
    global rewards_applied, animation_start_time, exp_animation_progress, gold_animation_progress, animation_complete
    
    screen.fill(BG_COLOR)
    draw_text("Battle Results", 48, GOLD, 20, 20)
    
    result_text = "Victory!" if victory else "Defeat!"
    result_color = GREEN if victory else RED
    
    draw_text(result_text, 64, result_color, SCREEN_WIDTH//2 - 100, 100)
    
    if victory:
        # Calculate rewards
        exp_reward, gold_reward, leveled_up = apply_rewards()
        
        # Start animation when rewards are first applied
        if rewards_applied and animation_start_time == 0:
            animation_start_time = pygame.time.get_ticks()
            exp_animation_progress = 0
            gold_animation_progress = 0
            animation_complete = False
        
        # Update animation progress
        if animation_start_time > 0 and not animation_complete:
            current_time = pygame.time.get_ticks()
            time_elapsed = (current_time - animation_start_time) / 1000.0  # Convert to seconds
            
            # Calculate progress for exp and gold bars (0.0 to 1.0)
            exp_animation_progress = min(1.0, time_elapsed * animation_speed * 50)
            gold_animation_progress = min(1.0, (time_elapsed - 1) * animation_speed * 50)  # Gold starts after exp
            
            # Check if animation is complete
            if exp_animation_progress >= 1.0 and gold_animation_progress >= 1.0:
                animation_complete = True
                
            # Play UI sounds at specific animation points
            if exp_animation_progress == 1.0 and ui_click_sound and not animation_complete:
                ui_click_sound.play()
                
        # Display rewards with animated progress
        draw_text(f"Experience gained: {exp_reward}", 32, WHITE, SCREEN_WIDTH//2 - 150, 200)
        
        # EXP progress bar
        bar_width = 400
        bar_height = 25
        bar_x = SCREEN_WIDTH//2 - 200
        
        # Draw experience progress bar
        pygame.draw.rect(screen, (50, 50, 70), pygame.Rect(bar_x, 235, bar_width, bar_height))
        fill_width = int(bar_width * (exp_animation_progress if not animation_complete else 1.0))
        if fill_width > 0:
            pygame.draw.rect(screen, (100, 100, 255), pygame.Rect(bar_x, 235, fill_width, bar_height))
        pygame.draw.rect(screen, (150, 150, 200), pygame.Rect(bar_x, 235, bar_width, bar_height), 2)
        
        # Gold rewards
        draw_text(f"Gold gained: {gold_reward}", 32, GOLD, SCREEN_WIDTH//2 - 100, 280)
        
        # Gold progress bar
        pygame.draw.rect(screen, (50, 50, 70), pygame.Rect(bar_x, 315, bar_width, bar_height))
        fill_width = int(bar_width * (gold_animation_progress if not animation_complete else 1.0))
        if fill_width > 0:
            pygame.draw.rect(screen, (220, 180, 40), pygame.Rect(bar_x, 315, fill_width, bar_height))
        pygame.draw.rect(screen, (230, 200, 100), pygame.Rect(bar_x, 315, bar_width, bar_height), 2)
        
        # Sparkle animation when bars are filling
        if not animation_complete:
            sparkle_positions = []
            if exp_animation_progress < 1.0:
                # Add sparkles along the exp bar fill point
                sparkle_x = bar_x + fill_width
                sparkle_positions.append((sparkle_x, 235 + bar_height//2))
                
            if gold_animation_progress > 0 and gold_animation_progress < 1.0:
                # Add sparkles along the gold bar fill point
                gold_fill_width = int(bar_width * gold_animation_progress)
                sparkle_x = bar_x + gold_fill_width
                sparkle_positions.append((sparkle_x, 315 + bar_height//2))
                
            # Draw sparkles
            for sparkle_pos in sparkle_positions:
                sparkle_size = random.randint(2, 5)
                sparkle_color = (255, 255, 255)
                pygame.draw.circle(screen, sparkle_color, sparkle_pos, sparkle_size)
        
        # Level up notification (shown after gold animation completes)
        if leveled_up and (animation_complete or gold_animation_progress > 0.8):
            level_up_y = 370
            level_up_alpha = min(255, int(255 * ((gold_animation_progress - 0.8) * 5))) if not animation_complete else 255
            
            # Create a temporary surface for alpha blending
            level_text = f"Level Up! You are now level {player['level']}!"
            font = pygame.font.SysFont(None, 36)
            text_surf = font.render(level_text, True, (255, 255, 100))
            
            # Apply alpha blending
            alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, level_up_alpha))
            text_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw the text
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, level_up_y))
            screen.blit(text_surf, text_rect)
            
            # Add stat increase text with slight delay
            if gold_animation_progress > 0.9 or animation_complete:
                stats_alpha = min(255, int(255 * ((gold_animation_progress - 0.9) * 10))) if not animation_complete else 255
                
                # Create a temporary surface for alpha blending
                stats_text = "All stats increased!"
                font = pygame.font.SysFont(None, 28)
                stats_surf = font.render(stats_text, True, WHITE)
                
                # Apply alpha blending
                alpha_surf = pygame.Surface(stats_surf.get_size(), pygame.SRCALPHA)
                alpha_surf.fill((255, 255, 255, stats_alpha))
                stats_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                # Draw the text
                stats_rect = stats_surf.get_rect(center=(SCREEN_WIDTH//2, level_up_y + 50))
                screen.blit(stats_surf, stats_rect)
    else:
        draw_text("You were defeated...", 32, WHITE, SCREEN_WIDTH//2 - 130, 200)
        draw_text("Better luck next time!", 28, WHITE, SCREEN_WIDTH//2 - 120, 250)
    
    # Only show continue button after animation completes or if defeated
    if not victory or animation_complete or (animation_start_time > 0 and pygame.time.get_ticks() - animation_start_time > 3000):
        continue_btn.draw()

# Helper functions for skill dragging
def get_skill_rect(index, from_available=True):
    if from_available:
        skill_list_x = 50
        skill_list_y = 290
        skill_width = 160
        skill_height = 36
        return pygame.Rect(skill_list_x, skill_list_y + index*45, skill_width, skill_height)
    else:
        slot_x = 400
        slot_y = 290
        slot_width = 180
        slot_height = 36
        return pygame.Rect(slot_x, slot_y + index*45, slot_width, slot_height)

def start_drag(pos, from_sequence=False):
    global dragging_skill, drag_from_index, drag_from_sequence
    
    # Check if clicked on a skill in the available list
    if not from_sequence:
        for i, skill in enumerate(player["skills"]):
            rect = get_skill_rect(i, True)
            if rect.collidepoint(pos):
                dragging_skill = skill
                drag_from_index = i
                drag_from_sequence = False
                return True
    # Check if clicked on a skill in the sequence
    else:
        for i, skill in enumerate(combat_sequence):
            rect = get_skill_rect(i, False)
            if rect.collidepoint(pos):
                dragging_skill = skill
                drag_from_index = i
                drag_from_sequence = True
                # Remove from sequence while dragging
                combat_sequence.pop(i)
                return True
    return False

def end_drag(pos):
    global dragging_skill, drag_from_index, drag_from_sequence, combat_sequence
    
    if dragging_skill:
        # Check if dropped on a sequence slot
        for i in range(5):  # 5 slots for the sequence
            rect = get_skill_rect(i, False)
            if rect.collidepoint(pos):
                # Play drop sound when dropping a skill in combat setup area
                if ui_drop_sound:
                    ui_drop_sound.play()
                    
                # Add to sequence at the selected position
                if i >= len(combat_sequence):
                    combat_sequence.append(dragging_skill)
                else:
                    combat_sequence.insert(i, dragging_skill)
                    
                # Limit sequence to 5 skills
                while len(combat_sequence) > 5:
                    combat_sequence.pop()
                
                dragging_skill = None
                drag_from_index = -1
                return True
        
        # If not dropped on a valid slot, return skill to original position if from sequence
        if drag_from_sequence:
            if 0 <= drag_from_index < len(combat_sequence):
                combat_sequence.insert(drag_from_index, dragging_skill)
            else:
                combat_sequence.append(dragging_skill)
        
        dragging_skill = None
        drag_from_index = -1
    return False

# Load audio
audio_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
menu_music_path = os.path.join(audio_folder, "Project Donut.mp3")
town_music_path = os.path.join(audio_folder, "Town Music.mp3")
battle_music_path = os.path.join(audio_folder, "Battle Music 1.mp3")
after_combat_path = os.path.join(audio_folder, "After Combat.mp3")
ui_click_path = os.path.join(audio_folder, "ui_click.wav")
ui_drop_path = os.path.join(audio_folder, "ui_click2.mp3")

# Load images
images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
title_screen_path = os.path.join(images_folder, "title_screen.png")

# Load title screen image
title_screen_img = None
try:
    if os.path.exists(title_screen_path):
        title_screen_img = pygame.image.load(title_screen_path)
        title_screen_img = pygame.transform.scale(title_screen_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception as e:
    print(f"Error loading title screen image: {e}")

# Check if audio files exist
has_menu_music = os.path.exists(menu_music_path)
has_town_music = os.path.exists(town_music_path)
has_battle_music = os.path.exists(battle_music_path)
has_after_combat_music = os.path.exists(after_combat_path)
current_music = None

# Load UI sounds
ui_click_sound = None
ui_drop_sound = None
try:
    if os.path.exists(ui_click_path):
        ui_click_sound = pygame.mixer.Sound(ui_click_path)
    if os.path.exists(ui_drop_path):
        ui_drop_sound = pygame.mixer.Sound(ui_drop_path)
except Exception as e:
    print(f"Error loading UI sound: {e}")

# Set up music functions
def play_menu_music():
    global current_music
    if has_menu_music and current_music != "menu":
        pygame.mixer.music.stop()
        pygame.mixer.music.load(menu_music_path)
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        current_music = "menu"

def play_town_music():
    global current_music
    if has_town_music and current_music != "town":
        pygame.mixer.music.stop()
        pygame.mixer.music.load(town_music_path)
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        current_music = "town"

def play_battle_music():
    global current_music
    if has_battle_music and current_music != "battle":
        pygame.mixer.music.stop()
        pygame.mixer.music.load(battle_music_path)
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        current_music = "battle"

def play_after_combat_music():
    global current_music
    if has_after_combat_music and current_music != "after_combat":
        pygame.mixer.music.stop()
        pygame.mixer.music.load(after_combat_path)
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        current_music = "after_combat"

def stop_music():
    global current_music
    pygame.mixer.music.stop()
    current_music = None

# Main game loop
running = True
last_combat_action = 0
dragging_skill = None
drag_from_index = -1
drag_from_sequence = False
combat_sequence_index = 0  # Current index in combat sequence

# Initialize rewards variables
rewards_applied = False
reward_exp = 0
reward_gold = 0
reward_level_up = False

# Animation variables for results screen
animation_start_time = 0
exp_animation_progress = 0
gold_animation_progress = 0
animation_complete = False
animation_speed = 0.01  # Controls speed of filling progress bars

while running:
    current_time = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEMOTION:
            if game_state == MAIN_MENU:
                new_game_btn.check_hover(mouse_pos)
                load_game_btn.check_hover(mouse_pos)
                exit_btn.check_hover(mouse_pos)
            elif game_state == CHARACTER:
                combat_btn.check_hover(mouse_pos)
                save_game_btn.check_hover(mouse_pos)
            elif game_state == COMBAT and combat_finished:
                back_btn.check_hover(mouse_pos)
            elif game_state == RESULTS:
                continue_btn.check_hover(mouse_pos)
                
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == MAIN_MENU:
                new_game_btn.handle_event(event)
                load_game_btn.handle_event(event)
                exit_btn.handle_event(event)
            elif game_state == CHARACTER:
                # Check for drag start
                if not start_drag(event.pos, False):
                    # If not starting a skill drag, check if starting a sequence drag
                    start_drag(event.pos, True)
                    
                # Check for button press
                combat_btn.handle_event(event)
                save_game_btn.handle_event(event)
            elif game_state == COMBAT and combat_finished:
                back_btn.handle_event(event)
            elif game_state == RESULTS:
                continue_btn.handle_event(event)
                
        # Handle mouse button up for skill dragging
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if game_state == CHARACTER and dragging_skill:
                end_drag(event.pos)
    
    # Combat timing
    if game_state == COMBAT and not combat_finished:
        if current_time - last_combat_action > 1000:  # 1 second between actions
            execute_combat_turn()
            last_combat_action = current_time
            
    # Reset rewards_applied when leaving results screen
    if game_state != RESULTS:
        rewards_applied = False
    
    # Handle music
    if game_state == MAIN_MENU:
        play_menu_music()
    elif game_state == CHARACTER:
        play_town_music()
    elif game_state == COMBAT:
        play_battle_music()
    elif game_state == RESULTS:
        play_after_combat_music()
    
    # Rendering
    if game_state == MAIN_MENU:
        draw_main_menu()
    elif game_state == CHARACTER:
        draw_character_screen()
    elif game_state == COMBAT:
        draw_combat_screen()
    elif game_state == RESULTS:
        # Only apply rewards once
        if not rewards_applied:
            draw_results_screen()
            rewards_applied = True
        else:
            draw_results_screen()
    
    pygame.display.flip()
    clock.tick(60)

# Clean up before exiting
stop_music()
pygame.mixer.quit()
pygame.quit()
sys.exit()