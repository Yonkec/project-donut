from typing import Dict, List, Any, Optional, Callable
import random
from .enemy_database import EnemyDatabase
from .skill import Skill
from .skill_manager import SkillManager
from .skill_database import SkillDatabase
from .action_manager import ActionManager

class Enemy:
    """
    Represents an enemy created from data.
    """
    def __init__(self, enemy_id: str, data: Dict[str, Any], skill_manager: SkillManager, action_manager: Optional[ActionManager] = None):
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
        
        # Ensure we have at least a basic attack
        if not self.skills:
            basic_attack = self.skill_manager.get_skill("basic_attack")
            if not basic_attack:
                basic_attack_data = {
                    "name": "Basic Attack",
                    "description": "A simple attack",
                    "effects": [
                        {
                            "type": "damage",
                            "params": {
                                "base_value": 5,
                                "stat_scaling": {"strength": 1.0}
                            }
                        }
                    ]
                }
                basic_attack = self.skill_manager.create_skill("basic_attack", basic_attack_data)
            self.skills.append(basic_attack)
        
        # Combat state
        self.buffs = {}
        self.status_effects = {}
        
        # Action management
        self.action_manager = action_manager
        if self.action_manager:
            action_speed = data.get("action_speed", 1.0)
            self.action_manager.register_entity(self.id, action_speed)
        
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
        messages.extend(self._update_buffs())
        
        # Update status effects
        messages.extend(self._update_status_effects_internal())
        
        # Update action modifiers
        if self.action_manager:
            expired_modifiers = self.action_manager.update_action_modifiers(self.id)
            for modifier in expired_modifiers:
                messages.append(f"{self.name}'s {modifier} effect has expired.")
            
        return messages
        
    def _update_buffs(self) -> List[str]:
        messages = []
        buffs_to_remove = []
        
        for buff_type, buff_data in self.buffs.items():
            buff_data['duration'] -= 1
            if buff_data['duration'] <= 0:
                buffs_to_remove.append(buff_type)
                messages.append(f"{self.name}'s {buff_type} buff has expired.")
        
        for buff_type in buffs_to_remove:
            del self.buffs[buff_type]
            
        return messages
        
    def _update_status_effects_internal(self) -> List[str]:
        messages = []
        statuses_to_remove = []
        
        for status_type, status_data in self.status_effects.items():
            messages.extend(self._process_status_effect(status_type, status_data))
            
            status_data['duration'] -= 1
            if status_data['duration'] <= 0:
                statuses_to_remove.append(status_type)
                messages.append(f"{self.name} is no longer affected by {status_type}.")
        
        for status_type in statuses_to_remove:
            del self.status_effects[status_type]
            
        return messages
        
    def _process_status_effect(self, status_type: str, status_data: Dict[str, Any]) -> List[str]:
        messages = []
        
        if status_type == 'poison':
            damage = status_data['value']
            self.current_hp = max(0, self.current_hp - damage)
            messages.append(f"{self.name} takes {damage} poison damage.")
        elif status_type == 'regeneration':
            healing = status_data['value']
            self.current_hp = min(self.max_hp, self.current_hp + healing)
            messages.append(f"{self.name} regenerates {healing} health.")
        elif status_type == 'stunned':
            messages.append(f"{self.name} is stunned and cannot act.")
            if self.action_manager:
                self.action_manager.add_action_modifier(self.id, "stunned", -1.0, 1)
        elif status_type == 'slowed':
            slow_value = status_data.get('value', 0.5)
            messages.append(f"{self.name} is slowed and gains action more slowly.")
            if self.action_manager:
                self.action_manager.add_action_modifier(self.id, "slowed", -slow_value, 1)
                
        return messages
        
    def choose_action(self, player) -> Any:
        """Choose a skill to use in combat based on behavior pattern"""
        available_skills = self._get_available_skills()
        
        if not available_skills:
            return self.skills[0] if self.skills else None
        
        if self.behavior == "random":
            return random.choice(available_skills)
        elif self.behavior == "weighted":
            return self._choose_weighted_skill(available_skills)
        elif self.behavior == "smart":
            return self._choose_smart_skill(available_skills)
        
        # Default fallback
        return random.choice(available_skills)
        
    def _get_available_skills(self) -> List[Any]:
        if self.action_manager and hasattr(self, 'id'):
            current_action = self.action_manager.get_current_action(self.id)
            return [skill for skill in self.skills if skill.can_use(self) and current_action >= skill.action_cost]
        else:
            return [skill for skill in self.skills if skill.can_use(self)]
            
    def _choose_weighted_skill(self, available_skills: List[Any]) -> Any:
        weighted_skills = []
        for skill in available_skills:
            weight = self.skill_weights.get(skill.id, 1)
            weighted_skills.extend([skill] * weight)
        return random.choice(weighted_skills) if weighted_skills else available_skills[0]
        
    def _choose_smart_skill(self, available_skills: List[Any]) -> Any:
        # Use healing when low HP
        if self.current_hp < self.max_hp * 0.3:
            healing_skills = [s for s in available_skills if any(e["type"] == "healing" for e in s.effects)]
            if healing_skills:
                return random.choice(healing_skills)
        
        # Otherwise use damage skills
        damage_skills = [s for s in available_skills if any(e["type"] == "damage" for e in s.effects)]
        if damage_skills:
            return random.choice(damage_skills)
            
        return random.choice(available_skills)


class EnemyManager:
    """
    Manages enemy creation and loading from database.
    """
    def __init__(self, database: Optional[EnemyDatabase] = None, skill_manager: Optional[SkillManager] = None, action_manager: Optional[ActionManager] = None):
        self.database = database or EnemyDatabase()
        self.skill_manager = skill_manager or SkillManager(SkillDatabase())
        self.action_manager = action_manager
        self.enemies = {}
        
        self._initialize_skill_manager()
    
    def create_enemy(self, enemy_id: str, enemy_data: Dict[str, Any], level: Optional[int] = None) -> Enemy:
        """Create an enemy from data, possibly using a template"""
        processed_data = self._process_enemy_data(enemy_id, enemy_data, level)
        return Enemy(enemy_id, processed_data, self.skill_manager, self.action_manager)
        
    def _initialize_skill_manager(self):
        # Ensure skill manager has loaded skills
        if not self.skill_manager.skills:
            self.skill_manager.register_default_effects()
            self.skill_manager.load_all_skills()
            
    def _process_enemy_data(self, enemy_id: str, enemy_data: Dict[str, Any], level: Optional[int] = None) -> Dict[str, Any]:
        processed_data = self._apply_template(enemy_data)
        
        # Override level if specified
        if level is not None:
            processed_data["level"] = level
            processed_data = self._update_name_with_level(processed_data, level)
            
        return processed_data
        
    def _apply_template(self, enemy_data: Dict[str, Any]) -> Dict[str, Any]:
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
                        
            return template
        return enemy_data
        
    def _update_name_with_level(self, enemy_data: Dict[str, Any], level: int) -> Dict[str, Any]:
        if "name" in enemy_data and "Lv." in enemy_data["name"]:
            name_parts = enemy_data["name"].split("Lv.")
            if len(name_parts) > 1:
                enemy_data["name"] = f"{name_parts[0]}Lv.{level}"
        return enemy_data
    
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
    
    def create_random_enemy(self, level: Optional[int] = None, player_level: int = 1) -> Optional[Enemy]:
        """Create a random enemy from available enemies based on player level"""
        all_enemies = self.database.get_all_enemies()
        if not all_enemies:
            return None
            
        suitable_enemies = self._get_suitable_enemies(all_enemies, player_level)
        
        if not suitable_enemies:
            return None
        
        # Choose a random enemy from suitable ones
        enemy_id, enemy_data = random.choice(suitable_enemies)
        return self.create_enemy(enemy_id, enemy_data, level)
        
    def _get_suitable_enemies(self, all_enemies: Dict[str, Dict[str, Any]], player_level: int) -> List[tuple]:
        # Filter enemies by player level requirement
        suitable_enemies = []
        for enemy_id, enemy_data in all_enemies.items():
            min_player_level = enemy_data.get("min_player_level", 1)
            if player_level >= min_player_level:
                suitable_enemies.append((enemy_id, enemy_data))
        
        if not suitable_enemies:
            # Fallback to basic enemies if no suitable ones found
            suitable_enemies = [(enemy_id, enemy_data) for enemy_id, enemy_data in all_enemies.items() 
                              if enemy_data.get("min_player_level", 1) == 1]
                              
        return suitable_enemies
