from typing import Dict, List, Optional
import random
from .skill_manager import Skill, SkillManager
from .skill_database import SkillDatabase

class Enemy:
    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        
        self.base_stats = {
            "strength": 8 + level,
            "dexterity": 8 + level,
            "constitution": 8 + level,
            "intelligence": 8 + level,
            "wisdom": 8 + level
        }
        

        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        
        self.damage = 2 + level
        self.defense = level // 2
        
        self.skill_database = SkillDatabase()
        self.skill_manager = SkillManager(self.skill_database)
        self.skill_manager.register_default_effects()
        self.skill_manager.load_all_skills()
        
        self.skills: List[Skill] = []
        basic_attack = self.skill_manager.get_skill("basic_attack")
        if basic_attack:
            self.skills.append(basic_attack)
            
        self.buffs = {}
        self.status_effects = {}
        
    def _calculate_max_hp(self) -> int:
        base_hp = 30
        con_bonus = self.base_stats["constitution"] * 3
        level_bonus = (self.level - 1) * 15
        return base_hp + con_bonus + level_bonus
        
    def get_stats(self) -> Dict[str, int]:
        return self.base_stats.copy()
        
    def take_damage(self, amount: int) -> int:
        damage_reduction = self.defense
        
        if hasattr(self, 'buffs') and 'defense' in self.buffs:
            damage_reduction += self.buffs['defense']['value']
        
        actual_damage = max(1, amount - damage_reduction)
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
        
    def heal(self, amount: int) -> int:
        if self.current_hp >= self.max_hp:
            return 0
            
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
        
    def is_alive(self) -> bool:
        return self.current_hp > 0
        
    def update_status_effects(self) -> List[str]:
        messages = []
        
        if hasattr(self, 'buffs'):
            buffs_to_remove = []
            for buff_type, buff_data in self.buffs.items():
                buff_data['duration'] -= 1
                if buff_data['duration'] <= 0:
                    buffs_to_remove.append(buff_type)
                    messages.append(f"{self.name}'s {buff_type} buff has expired.")
            
            for buff_type in buffs_to_remove:
                del self.buffs[buff_type]
        
        if hasattr(self, 'status_effects'):
            statuses_to_remove = []
            for status_type, status_data in self.status_effects.items():
                if status_type == 'poison':
                    damage = status_data['value']
                    self.current_hp = max(0, self.current_hp - damage)
                    messages.append(f"{self.name} takes {damage} poison damage.")
                elif status_type == 'regeneration':
                    healing = status_data['value']
                    self.current_hp = min(self.max_hp, self.current_hp + healing)
                    messages.append(f"{self.name} regenerates {healing} health.")
                
                status_data['duration'] -= 1
                if status_data['duration'] <= 0:
                    statuses_to_remove.append(status_type)
                    messages.append(f"{self.name} is no longer affected by {status_type}.")
            
            for status_type in statuses_to_remove:
                del self.status_effects[status_type]
                
        return messages
        
    def choose_action(self, player) -> Skill:
        """Choose a skill to use in combat"""
        available_skills = [skill for skill in self.skills if skill.can_use(self)]
        
        if not available_skills:
            return self.skills[0]
                
        return random.choice(available_skills)


def create_goblin(level: int = 1) -> Enemy:
    enemy = Enemy(f"Goblin Lv.{level}", level)
    enemy.base_stats["dexterity"] += 2
    enemy.base_stats["constitution"] -= 1
    enemy.max_hp = enemy._calculate_max_hp()
    enemy.current_hp = enemy.max_hp
    
    quick_strike = enemy.skill_manager.get_skill("quick_strike")
    if quick_strike:
        enemy.skills.append(quick_strike)
    
    return enemy

def create_orc(level: int = 1) -> Enemy:
    enemy = Enemy(f"Orc Lv.{level}", level)
    enemy.base_stats["strength"] += 3
    enemy.base_stats["constitution"] += 2
    enemy.base_stats["dexterity"] -= 2
    enemy.damage += 2
    enemy.max_hp = enemy._calculate_max_hp()
    enemy.current_hp = enemy.max_hp
    
    power_attack = enemy.skill_manager.get_skill("power_attack")
    if power_attack:
        enemy.skills.append(power_attack)
    
    return enemy

def create_skeleton(level: int = 1) -> Enemy:
    enemy = Enemy(f"Skeleton Lv.{level}", level)
    enemy.base_stats["constitution"] -= 3
    enemy.defense += 2
    enemy.max_hp = enemy._calculate_max_hp()
    enemy.current_hp = enemy.max_hp
    
    poison_dart = enemy.skill_manager.get_skill("poison_dart")
    if poison_dart:
        enemy.skills.append(poison_dart)
    
    return enemy

def create_random_enemy(level: int = 1) -> Enemy:
    enemy_types = [create_goblin, create_orc, create_skeleton]
    creator = random.choice(enemy_types)
    return creator(level)