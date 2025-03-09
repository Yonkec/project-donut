from typing import Dict, List, Optional, Any, Union
from .action_manager import ActionManager
from .player_inventory import PlayerInventory
from .player_skills import PlayerSkills

class Player:
    def __init__(self, name: str, action_manager: Optional[ActionManager] = None):
        self.name = name
        self.id = f"player_{name}"
        self.level = 1
        self.experience = 0
        self.experience_to_level = 100
        self.gold = 50
        
        self.base_stats = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10
        }
        
        # Initialize HP before other components that might need it
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        
        self.action_manager = action_manager
        if self.action_manager:
            self.action_manager.register_entity(self.id, 8.0) #player's action rate
        
        # Initialize component managers after HP is set
        self.inventory = PlayerInventory(self)
        self.skills_manager = PlayerSkills(self)
        
        # If we have an action manager, make sure it's available to the skills manager
        if self.action_manager and not hasattr(self.skills_manager, 'action_manager'):
            self.skills_manager.action_manager = self.action_manager
        
    def __getattr__(self, name):
        # Forward attribute access to the appropriate component
        if name == 'equipment':
            return self.inventory.equipment
        elif name in ['skills', 'combat_sequence', 'buffs', 'status_effects', 'skill_manager', 'skill_database']:
            if hasattr(self.skills_manager, name):
                return getattr(self.skills_manager, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
    def _calculate_max_hp(self) -> int:
        base_hp = 50
        con_bonus = self.base_stats["constitution"] * 5
        level_bonus = (self.level - 1) * 20
        return base_hp + con_bonus + level_bonus
        
    def get_stats(self) -> Dict[str, int]:
        stats = self.base_stats.copy()
        equipment_stats = self.inventory.get_equipment_stats()
        
        for stat, value in equipment_stats.items():
            if stat in stats:
                stats[stat] += value
        
        return stats
    
    def _update_hp_after_stat_change(self):
        old_max_hp = self.max_hp
        self.max_hp = self._calculate_max_hp()
        
        if old_max_hp != self.max_hp:
            self.current_hp = int(self.current_hp * (self.max_hp / old_max_hp))
    
    def equip_item(self, item):
        return self.inventory.equip_item(item)
    
    def unequip_item(self, slot):
        return self.inventory.unequip_item(slot)
    
    def learn_skill(self, skill):
        return self.skills_manager.learn_skill(skill)
    
    def learn_skill_by_id(self, skill_id):
        return self.skills_manager.learn_skill_by_id(skill_id)
    
    def add_to_combat_sequence(self, skill, position):
        return self.skills_manager.add_to_combat_sequence(skill, position)
    
    def add_to_combat_sequence_by_id(self, skill_id, position):
        return self.skills_manager.add_to_combat_sequence_by_id(skill_id, position)
        
    def gain_experience(self, amount: int) -> bool:
        self.experience += amount
        
        if self.experience >= self.experience_to_level:
            self.level_up()
            return True
        return False
        
    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_level
        self.experience_to_level = int(self.experience_to_level * 1.5)
        
        for stat in self.base_stats:
            self.base_stats[stat] += 2
            
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
    
    def take_damage(self, amount: int) -> int:
        damage_reduction = self.inventory.get_defense()
                
        if 'defense' in self.skills_manager.buffs:
            damage_reduction += self.skills_manager.buffs['defense']['value']
                
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
        return self.skills_manager.update_status_effects()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "level": self.level,
            "experience": self.experience,
            "experience_to_level": self.experience_to_level,
            "gold": self.gold,
            "base_stats": self.base_stats,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "inventory": self.inventory.to_dict() if hasattr(self.inventory, 'to_dict') else {},
            "skills": self.skills_manager.to_dict() if hasattr(self.skills_manager, 'to_dict') else {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], action_manager: Optional[ActionManager] = None) -> 'Player':
        if not isinstance(data, dict):
            raise ValueError("Player data must be a dictionary")
            
        player = cls(data.get("name", "Hero"), action_manager)
        
        player.id = data.get("id", player.id)
        player.level = data.get("level", 1)
        player.experience = data.get("experience", 0)
        player.experience_to_level = data.get("experience_to_level", 100)
        player.gold = data.get("gold", 50)
        
        if "base_stats" in data and isinstance(data["base_stats"], dict):
            for stat, value in data["base_stats"].items():
                if stat in player.base_stats:
                    player.base_stats[stat] = value
        
        player.max_hp = data.get("max_hp", player._calculate_max_hp())
        player.current_hp = data.get("current_hp", player.max_hp)
        
        if "inventory" in data and hasattr(player.inventory, 'from_dict'):
            player.inventory.from_dict(data["inventory"])
            
        if "skills" in data and hasattr(player.skills_manager, 'from_dict'):
            player.skills_manager.from_dict(data["skills"])
            
        return player