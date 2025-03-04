from typing import Dict, List, Any, Optional, Callable
import random
from .enemy_database import EnemyDatabase
from .skill_manager import SkillManager
from .skill_database import SkillDatabase

class Enemy:
    """
    Represents an enemy created from data.
    """
    def __init__(self, enemy_id: str, data: Dict[str, Any], skill_manager: SkillManager):
        self.id = enemy_id
        self.name = data["name"]
        self.level = data.get("level", 1)
        
        # Stats
        self.base_stats = data.get("base_stats", {
            "strength": 8 + self.level,
            "dexterity": 8 + self.level,
            "constitution": 8 + self.level,
            "intelligence": 8 + self.level,
            "wisdom": 8 + self.level
        })
        
        # HP and combat stats
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        self.damage = data.get("damage", 2 + self.level)
        self.defense = data.get("defense", self.level // 2)
        
        # Skills
        self.skill_manager = skill_manager
        self.skills = []
        
        # Load skills
        skill_ids = data.get("skills", ["basic_attack"])
        for skill_id in skill_ids:
            skill = self.skill_manager.get_skill(skill_id)
            if skill:
                self.skills.append(skill)
        
        # Combat state
        self.buffs = {}
        self.status_effects = {}
        
        # AI behavior
        self.behavior = data.get("behavior", "random")
        self.skill_weights = data.get("skill_weights", {})
        
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
        
        # Update buffs
        buffs_to_remove = []
        for buff_type, buff_data in self.buffs.items():
            buff_data['duration'] -= 1
            if buff_data['duration'] <= 0:
                buffs_to_remove.append(buff_type)
                messages.append(f"{self.name}'s {buff_type} buff has expired.")
        
        for buff_type in buffs_to_remove:
            del self.buffs[buff_type]
        
        # Update status effects
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
        
    def choose_action(self, player) -> Any:
        """Choose a skill to use in combat based on behavior pattern"""
        available_skills = [skill for skill in self.skills if skill.can_use(self)]
        
        if not available_skills:
            return self.skills[0] if self.skills else None
        
        if self.behavior == "random":
            return random.choice(available_skills)
        elif self.behavior == "weighted":
            # Use skill weights if defined
            weighted_skills = []
            for skill in available_skills:
                weight = self.skill_weights.get(skill.id, 1)
                weighted_skills.extend([skill] * weight)
            return random.choice(weighted_skills) if weighted_skills else available_skills[0]
        elif self.behavior == "smart":
            # Simple smart behavior - use healing when low HP, otherwise attack
            if self.current_hp < self.max_hp * 0.3:
                healing_skills = [s for s in available_skills if any(e["type"] == "healing" for e in s.effects)]
                if healing_skills:
                    return random.choice(healing_skills)
            
            # Otherwise use damage skills
            damage_skills = [s for s in available_skills if any(e["type"] == "damage" for e in s.effects)]
            if damage_skills:
                return random.choice(damage_skills)
        
        # Default fallback
        return random.choice(available_skills)


class EnemyManager:
    """
    Manages enemy creation and loading from database.
    """
    def __init__(self, database: Optional[EnemyDatabase] = None, skill_manager: Optional[SkillManager] = None):
        self.database = database or EnemyDatabase()
        self.skill_manager = skill_manager or SkillManager(SkillDatabase())
        self.enemies = {}
        
        # Ensure skill manager has loaded skills
        if not self.skill_manager.skills:
            self.skill_manager.register_default_effects()
            self.skill_manager.load_all_skills()
    
    def create_enemy(self, enemy_id: str, enemy_data: Dict[str, Any], level: Optional[int] = None) -> Enemy:
        """Create an enemy from data, possibly using a template"""
        if "template" in enemy_data and enemy_data["template"] in self.database.templates:
            # Start with template and override with specific data
            template = self.database.get_template(enemy_data["template"]).copy()
            for key, value in enemy_data.items():
                if key != "template":
                    if key == "skills" and "skills" in template:
                        # For skills, we might want to replace or extend
                        if enemy_data.get("extend_skills", False):
                            template[key].extend(value)
                        else:
                            template[key] = value
                    else:
                        template[key] = value
            enemy_data = template
        
        # Override level if specified
        if level is not None:
            enemy_data["level"] = level
            
            # Update name if it contains level
            if "name" in enemy_data and "Lv." in enemy_data["name"]:
                name_parts = enemy_data["name"].split("Lv.")
                if len(name_parts) > 1:
                    enemy_data["name"] = f"{name_parts[0]}Lv.{level}"
        
        # Create the enemy object
        enemy = Enemy(enemy_id, enemy_data, self.skill_manager)
        return enemy
    
    def get_enemy(self, enemy_id: str, level: Optional[int] = None) -> Optional[Enemy]:
        """Get an enemy by ID with optional level override"""
        enemy_data = self.database.get_enemy(enemy_id)
        if enemy_data:
            return self.create_enemy(enemy_id, enemy_data, level)
        return None
    
    def load_all_enemies(self) -> None:
        """Load all enemies from the database"""
        for enemy_id, enemy_data in self.database.get_all_enemies().items():
            self.create_enemy(enemy_id, enemy_data)
    
    def create_random_enemy(self, level: Optional[int] = None) -> Optional[Enemy]:
        """Create a random enemy from available enemies"""
        all_enemies = list(self.database.get_all_enemies().items())
        if not all_enemies:
            return None
            
        enemy_id, enemy_data = random.choice(all_enemies)
        return self.create_enemy(enemy_id, enemy_data, level)
