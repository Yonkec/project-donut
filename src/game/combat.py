from typing import Dict, List, Optional
import random
import time
import os
import pygame
from .player import Player
from .enemy import Enemy, create_random_enemy
from .items import Item, create_health_potion

attack_sound = None
heal_sound = None

try:
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'audio')
    attack_sound_path = os.path.join(audio_dir, 'attack.wav')
    heal_sound_path = os.path.join(audio_dir, 'heal.wav')
    
    if os.path.exists(attack_sound_path):
        attack_sound = pygame.mixer.Sound(attack_sound_path)
    if os.path.exists(heal_sound_path):
        heal_sound = pygame.mixer.Sound(heal_sound_path)
except Exception as e:
    print(f"Error loading combat sounds: {e}")

class CombatManager:
    def __init__(self, player: Player):
        self.player = player
        self.current_enemy: Optional[Enemy] = None
        self.turn = 0
        self.combat_log: List[str] = []
        self.combat_active = False
        self.victory = False
        self.rewards: Dict = {}
        self.player_sequence_index = 0
        self.action_delay = 0.8  # seconds between actions
        self.last_action_time = 0
        
    def start_new_battle(self, enemy_level: Optional[int] = None):
        """Start a new battle with a random enemy"""
        # Determine enemy level based on player level
        if enemy_level is None:
            # Randomly choose level close to player's level
            level_diff = random.randint(-1, 1)
            enemy_level = max(1, self.player.level + level_diff)
            
        self.current_enemy = create_random_enemy(enemy_level)
        self.turn = 0
        self.combat_log = []
        self.log_message(f"Battle started against {self.current_enemy.name}!")
        self.combat_active = True
        self.victory = False
        self.rewards = {}
        self.player_sequence_index = 0
        self.last_action_time = time.time()
        
    def log_message(self, message: str):
        """Add a message to the combat log"""
        self.combat_log.append(message)
        
    def update(self) -> bool:
        """
        Update the combat state, executing actions when appropriate
        Returns True if combat is finished
        """
        if not self.combat_active:
            return True
            
        current_time = time.time()
        if current_time - self.last_action_time < self.action_delay:
            return False  # Wait for delay
            
        # First check if either combatant is defeated
        if not self.player.is_alive():
            self.log_message(f"{self.player.name} has been defeated!")
            self.end_combat(False)
            return True
            
        if not self.current_enemy.is_alive():
            self.log_message(f"{self.current_enemy.name} has been defeated!")
            self.end_combat(True)
            return True
            
        # Execute the next action
        if self.turn % 2 == 0:
            # Player's turn - execute the next skill in sequence
            self._execute_player_action()
        else:
            # Enemy's turn
            self._execute_enemy_action()
            
        self.turn += 1
        self.last_action_time = current_time
        
        # Update skill cooldowns at end of turn pair
        if self.turn % 2 == 0:
            self._update_cooldowns()
            
        return False
        
    def _execute_player_action(self):
        """Execute the player's next skill in the combat sequence"""
        # Get the next skill in sequence
        if not self.player.combat_sequence or self.player_sequence_index >= len(self.player.combat_sequence):
            # Reset to beginning of sequence if we've reached the end
            self.player_sequence_index = 0
            
        if not self.player.combat_sequence:
            self.log_message(f"{self.player.name} has no skills configured!")
            return
            
        skill = self.player.combat_sequence[self.player_sequence_index]
        
        # Check if skill can be used
        if not skill or not skill.can_use(self.player):
            # Skill on cooldown, use basic attack instead
            skill = self.player.skills[0]  # Basic attack as fallback
            self.log_message(f"{skill.name} on cooldown, using Basic Attack instead")
            
        # Use the skill
        result = skill.use(self.player, self.current_enemy)
        self.log_message(result["message"])
        
        # Play appropriate sound effect
        if skill.name == "Healing":
            if heal_sound:
                heal_sound.play()
        elif "attack" in skill.name.lower() or "strike" in skill.name.lower():
            if attack_sound:
                attack_sound.play()
        
        # Move to next skill in sequence
        self.player_sequence_index = (self.player_sequence_index + 1) % len(self.player.combat_sequence)
        
    def _execute_enemy_action(self):
        """Execute the enemy's chosen action"""
        if not self.current_enemy:
            return
            
        # Enemy AI chooses a skill
        skill = self.current_enemy.choose_action(self.player)
        
        # Use the skill
        result = skill.use(self.current_enemy, self.player)
        self.log_message(result["message"])
        
    def _update_cooldowns(self):
        """Update cooldowns for all skills"""
        # Update player skill cooldowns
        for skill in self.player.skills:
            skill.update_cooldown()
            
        # Update enemy skill cooldowns
        if self.current_enemy:
            for skill in self.current_enemy.skills:
                skill.update_cooldown()
                
    def end_combat(self, victory: bool):
        """End the combat and determine rewards if victorious"""
        self.combat_active = False
        self.victory = victory
        
        if victory:
            # Calculate rewards
            exp_reward = self.current_enemy.level * 20
            gold_reward = self.current_enemy.level * 10 + random.randint(0, 10)
            
            # Maybe reward an item (20% chance)
            items_reward = []
            if random.random() < 0.2:
                items_reward.append(create_health_potion())
                
            self.rewards = {
                "experience": exp_reward,
                "gold": gold_reward,
                "items": items_reward
            }
            
            # Apply rewards to player
            self.player.gold += gold_reward
            leveled_up = self.player.gain_experience(exp_reward)
            
            for item in items_reward:
                self.player.inventory.append(item)
                
            # Add reward info to log
            self.log_message(f"Gained {exp_reward} experience and {gold_reward} gold!")
            if items_reward:
                self.log_message(f"Found: {', '.join(item.name for item in items_reward)}")
            if leveled_up:
                self.log_message(f"{self.player.name} leveled up to level {self.player.level}!")
        else:
            # Player was defeated - maybe apply penalties in the future
            pass