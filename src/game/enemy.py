from typing import Dict, List, Optional
import random
from .skills import Skill, BasicAttack

class Enemy:
    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        
        # Stats based on level
        self.base_stats = {
            "strength": 8 + level,
            "dexterity": 8 + level,
            "constitution": 8 + level,
            "intelligence": 8 + level,
            "wisdom": 8 + level
        }
        
        # Health
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        
        # Combat
        self.damage = 2 + level
        self.defense = level // 2
        self.skills: List[Skill] = [BasicAttack()]  # All enemies have basic attack
        self.defense_buff = 0
        
    def _calculate_max_hp(self) -> int:
        base_hp = 30
        con_bonus = self.base_stats["constitution"] * 3
        level_bonus = (self.level - 1) * 15
        return base_hp + con_bonus + level_bonus
        
    def get_stats(self) -> Dict[str, int]:
        """Return the enemy's stats"""
        return self.base_stats.copy()
        
    def take_damage(self, amount: int) -> int:
        """Take damage and return the actual amount taken"""
        # Apply defense and defense buff
        damage_reduction = self.defense + self.defense_buff
        
        # Reset defense buff after use
        self.defense_buff = 0
        
        # Minimum 1 damage
        actual_damage = max(1, amount - damage_reduction)
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
        
    def heal(self, amount: int) -> int:
        """Heal the enemy and return the actual amount healed"""
        if self.current_hp >= self.max_hp:
            return 0
            
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
        
    def is_alive(self) -> bool:
        """Check if the enemy is alive"""
        return self.current_hp > 0
        
    def choose_action(self, player) -> Skill:
        """Choose a skill to use in combat"""
        # Filter skills that can be used
        available_skills = [skill for skill in self.skills if skill.can_use(self)]
        
        if not available_skills:
            # If no skills are available, return basic attack
            return self.skills[0]
            
        # Simple AI: prioritize healing at low health, otherwise attack
        if self.current_hp < self.max_hp * 0.3:  # Below 30% health
            # Try to find a healing skill
            healing_skills = [skill for skill in available_skills 
                             if skill.__class__.__name__ == 'HealingSkill']
            if healing_skills:
                return random.choice(healing_skills)
                
        # Choose a random skill to use
        return random.choice(available_skills)

# Enemy factory methods
def create_goblin(level: int = 1) -> Enemy:
    enemy = Enemy(f"Goblin Lv.{level}", level)
    # Goblins have slightly higher dexterity but lower constitution
    enemy.base_stats["dexterity"] += 2
    enemy.base_stats["constitution"] -= 1
    enemy.max_hp = enemy._calculate_max_hp()
    enemy.current_hp = enemy.max_hp
    return enemy

def create_orc(level: int = 1) -> Enemy:
    enemy = Enemy(f"Orc Lv.{level}", level)
    # Orcs have higher strength and constitution but lower dexterity
    enemy.base_stats["strength"] += 3
    enemy.base_stats["constitution"] += 2
    enemy.base_stats["dexterity"] -= 2
    enemy.damage += 2
    enemy.max_hp = enemy._calculate_max_hp()
    enemy.current_hp = enemy.max_hp
    return enemy

def create_skeleton(level: int = 1) -> Enemy:
    enemy = Enemy(f"Skeleton Lv.{level}", level)
    # Skeletons have higher defense but lower health
    enemy.base_stats["constitution"] -= 3
    enemy.defense += 2
    enemy.max_hp = enemy._calculate_max_hp()
    enemy.current_hp = enemy.max_hp
    return enemy

def create_random_enemy(level: int = 1) -> Enemy:
    enemy_types = [create_goblin, create_orc, create_skeleton]
    creator = random.choice(enemy_types)
    return creator(level)