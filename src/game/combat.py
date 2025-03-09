from typing import Dict, List, Optional
import random
import time
import os
import pygame
import logging
from .player import Player
from .enemy import Enemy, create_random_enemy
from .skills import create_skill_manager
from .items import Item, create_health_potion
from .action_manager import ActionManager
from .enemy_database import EnemyDatabase
from .enemy_manager import EnemyManager

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize sound variables
attack_sound = None
heal_sound = None
sounds_initialized = False

def init_combat_sounds():
    """Initialize combat sound effects when pygame is ready"""
    global attack_sound, heal_sound, sounds_initialized
    
    if sounds_initialized:
        return
        
    try:
        if pygame.mixer.get_init() is None:
            return
            
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'audio')
        attack_sound_path = os.path.join(audio_dir, 'attack.wav')
        heal_sound_path = os.path.join(audio_dir, 'heal.wav')
        
        if os.path.exists(attack_sound_path):
            attack_sound = pygame.mixer.Sound(attack_sound_path)
        if os.path.exists(heal_sound_path):
            heal_sound = pygame.mixer.Sound(heal_sound_path)
            
        sounds_initialized = True
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
        self.action_delay = 0.5  # seconds between actions
        self.last_action_time = 0
        self.last_tick_time = 0
        self.tick_interval = 0.5  # seconds between ticks for action points
        self.action_manager = player.action_manager if hasattr(player, 'action_manager') else ActionManager()
        
        # Create skill and enemy managers
        self.skill_manager = create_skill_manager()
        self.enemy_database = EnemyDatabase()
        self.enemy_manager = EnemyManager(self.enemy_database, self.skill_manager, self.action_manager)
        self.enemy_manager.load_all_enemies()
        
        # Initialize sounds
        init_combat_sounds()
        

        
    def start_new_battle(self, enemy_level: Optional[int] = None):
        if enemy_level is None:
            enemy_level = max(1, self.player.level)
            
        self.current_enemy = create_random_enemy(enemy_level, self.player.level)
        
        if not self.current_enemy:
            # Fallback to create a basic enemy if no enemies are defined
            enemy_data = {
                "name": f"Goblin Lv.{enemy_level}",
                "level": enemy_level,
                "skills": ["basic_attack"],
                "stats": {
                    "strength": 5 + enemy_level,
                    "dexterity": 7 + enemy_level,
                    "intelligence": 3 + enemy_level,
                    "vitality": 4 + enemy_level
                },
                "max_hp": 20 + (enemy_level * 5),
                "max_energy": 10 + (enemy_level * 2)
            }
            self.current_enemy = Enemy("goblin", enemy_data, self.skill_manager, self.action_manager)
            
        # Make sure the enemy uses the same action manager as the player
        if self.action_manager and hasattr(self.current_enemy, 'id'):
            logging.debug(f"Combat: Setting enemy {self.current_enemy.id} to use the combat manager's action manager")
            self.current_enemy.action_manager = self.action_manager
            
            # Force register the enemy with the action manager
            logging.debug(f"Combat: Registering enemy {self.current_enemy.id} with action manager")
            self.action_manager.unregister_entity(self.current_enemy.id)  # Remove any existing registration
            self.action_manager.register_entity(self.current_enemy.id, 1.0)
            logging.debug(f"Combat: Action manager entities: {list(self.action_manager.action_consumers.keys())}")
            
        self.combat_active = True
        self.victory = False
        self.turn = 0
        self.player_sequence_index = 0
        self.combat_log = []
        self.log_message(f"Battle started against {self.current_enemy.name}!")
        
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
            
        # Update action points for both combatants
        self._update_action_points()
            
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
        
    def _update_action_points(self):
        logging.debug(f"Updating action points. Action manager exists: {self.action_manager is not None}")
        if self.action_manager:
            if hasattr(self.player, 'id'):
                logging.debug(f"Generating action for player {self.player.id}")
                tick_rate = self.action_manager.action_generators[self.player.id]["current_rate"]
                self.action_manager.generate_action(self.player.id, tick_rate)
                player_action = self.action_manager.get_current_action(self.player.id)
                logging.debug(f"Player action points: {player_action}, tick rate: {tick_rate}")
            else:
                logging.debug("Player has no id attribute")
            
            if self.current_enemy and hasattr(self.current_enemy, 'id'):
                logging.debug(f"Generating action for enemy {self.current_enemy.id}")
                tick_rate = self.action_manager.action_generators[self.current_enemy.id]["current_rate"]
                self.action_manager.generate_action(self.current_enemy.id, tick_rate)
                enemy_action = self.action_manager.get_current_action(self.current_enemy.id)
                logging.debug(f"Enemy action points: {enemy_action}, tick rate: {tick_rate}")
            elif self.current_enemy:
                logging.debug("Enemy has no id attribute")
            else:
                logging.debug("No current enemy")
        else:
            logging.debug("No action manager in combat manager")
    
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