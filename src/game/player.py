from typing import Dict, List, Optional, Any
from .items import Item, Equipment
from .skill_manager import Skill
from .skill_manager import SkillManager
from .skill_database import SkillDatabase
from .action_manager import ActionManager

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
        
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        
        self.equipment: Dict[str, Optional[Equipment]] = {
            "weapon": None,
            "armor": None,
            "helmet": None,
            "boots": None,
            "accessory": None
        }
        self.inventory: List[Item] = []
        
        self.skills: List[Skill] = []
        self.combat_sequence: List[Skill] = []
        self.buffs = {}
        self.status_effects = {}
        
        self.action_manager = action_manager
        if self.action_manager:
            self.action_manager.register_entity(self.id, 1.0)
            
        self._initialize_defaults()
        
    def _initialize_defaults(self):
        from .items import Weapon, Armor
        
        self.skill_database = SkillDatabase()
        self.skill_manager = SkillManager(self.skill_database)
        self.skill_manager.register_default_effects()
        self.skill_manager.load_all_skills()
        
        starter_sword = Weapon("Wooden Sword", 2, 0, 0)
        starter_armor = Armor("Cloth Tunic", 1, 0, 0)
        
        self.equip_item(starter_sword)
        self.equip_item(starter_armor)
        
        basic_attack = self.skill_manager.get_skill("basic_attack")
        defend = self.skill_manager.get_skill("defend")
        
        if basic_attack and defend:
            self.learn_skill(basic_attack)
            self.learn_skill(defend)
            
            self.combat_sequence = [basic_attack] * 3
        
    def _calculate_max_hp(self) -> int:
        base_hp = 50
        con_bonus = self.base_stats["constitution"] * 5
        level_bonus = (self.level - 1) * 20
        return base_hp + con_bonus + level_bonus
        
    def get_stats(self) -> Dict[str, int]:
        """Return combined stats from base stats and equipment"""
        stats = self.base_stats.copy()
        
        for slot, item in self.equipment.items():
            if item:
                for stat, value in item.stat_bonuses.items():
                    if stat in stats:
                        stats[stat] += value
        
        return stats
        
    def equip_item(self, item: Equipment) -> bool:
        """Equip an item in the appropriate slot"""
        if item.slot in self.equipment:
            old_item = self.equipment[item.slot]
            if old_item:
                self.inventory.append(old_item)
                
            self.equipment[item.slot] = item
            self._update_hp_after_stat_change()
            return True
        return False
        
    def unequip_item(self, slot: str) -> bool:
        """Unequip an item from the specified slot"""
        if slot in self.equipment and self.equipment[slot]:
            item = self.equipment[slot]
            self.inventory.append(item)
            self.equipment[slot] = None
            self._update_hp_after_stat_change()
            return True
        return False
        
    def learn_skill(self, skill: Skill) -> bool:
        """Learn a new skill if player doesn't already know it"""
        for existing_skill in self.skills:
            if existing_skill.id == skill.id:
                return False
                
        self.skills.append(skill)
        return True
        
    def learn_skill_by_id(self, skill_id: str) -> bool:
        """Learn a new skill by its ID"""
        for existing_skill in self.skills:
            if existing_skill.id == skill_id:
                return False
                
        skill = self.skill_manager.get_skill(skill_id)
        if skill:
            return self.learn_skill(skill)
        return False
        
    def add_to_combat_sequence(self, skill: Skill, position: int) -> bool:
        """Add a skill to the combat sequence at the specified position"""
        if skill in self.skills and 0 <= position < 5:  # Limit to 5 skills in sequence
            if len(self.combat_sequence) <= position:
                self.combat_sequence.extend([None] * (position - len(self.combat_sequence) + 1))
            self.combat_sequence[position] = skill
            return True
        return False
        
    def add_to_combat_sequence_by_id(self, skill_id: str, position: int) -> bool:
        """Add a skill to the combat sequence by its ID"""
        for skill in self.skills:
            if skill.id == skill_id:
                return self.add_to_combat_sequence(skill, position)
        return False
        
    def gain_experience(self, amount: int) -> bool:
        """Gain experience and level up if necessary. Returns True if leveled up."""
        self.experience += amount
        
        if self.experience >= self.experience_to_level:
            self.level_up()
            return True
        return False
        
    def level_up(self):
        """Level up the player, increasing stats and health"""
        self.level += 1
        self.experience -= self.experience_to_level
        self.experience_to_level = int(self.experience_to_level * 1.5)
        
        for stat in self.base_stats:
            self.base_stats[stat] += 2
            
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        
    def _update_hp_after_stat_change(self):
        old_max_hp = self.max_hp
        self.max_hp = self._calculate_max_hp()
        
        if old_max_hp != self.max_hp:
            self.current_hp = int(self.current_hp * (self.max_hp / old_max_hp))
    
    def take_damage(self, amount: int) -> int:
        """Take damage and return the actual amount taken"""
        damage_reduction = 0
        for slot, item in self.equipment.items():
            if item and hasattr(item, 'defense'):
                damage_reduction += item.defense
                
        if hasattr(self, 'buffs') and 'defense' in self.buffs:
            damage_reduction += self.buffs['defense']['value']
                
        actual_damage = max(1, amount - damage_reduction)
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
        
    def heal(self, amount: int) -> int:
        """Heal the player and return the actual amount healed"""
        if self.current_hp >= self.max_hp:
            return 0
            
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
        
    def is_alive(self) -> bool:
        return self.current_hp > 0
        
    def update_status_effects(self) -> List[str]:
        """Update all status effects and buffs, return messages"""
        messages = []
        
        buffs_to_remove = []
        for buff_type, buff_data in self.buffs.items():
            buff_data['duration'] -= 1
            if buff_data['duration'] <= 0:
                buffs_to_remove.append(buff_type)
                messages.append(f"{self.name}'s {buff_type} buff has expired.")
        
        for buff_type in buffs_to_remove:
            del self.buffs[buff_type]
        
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
            elif status_type == 'stunned':
                messages.append(f"{self.name} is stunned and cannot act.")
                if self.action_manager:
                    self.action_manager.add_action_modifier(self.id, "stunned", -1.0, 1)
            elif status_type == 'slowed':
                slow_value = status_data.get('value', 0.5)
                messages.append(f"{self.name} is slowed and gains action more slowly.")
                if self.action_manager:
                    self.action_manager.add_action_modifier(self.id, "slowed", -slow_value, 1)
            
            status_data['duration'] -= 1
            if status_data['duration'] <= 0:
                statuses_to_remove.append(status_type)
                messages.append(f"{self.name} is no longer affected by {status_type}.")
        
        for status_type in statuses_to_remove:
            del self.status_effects[status_type]
        
        if self.action_manager:
            expired_modifiers = self.action_manager.update_action_modifiers(self.id)
            for modifier in expired_modifiers:
                messages.append(f"{self.name}'s {modifier} effect has expired.")
                
        return messages