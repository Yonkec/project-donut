from typing import Dict, List, Optional
from .items import Item, Equipment
from .skills import Skill

class Player:
    def __init__(self, name: str):
        self.name = name
        self.level = 1
        self.experience = 0
        self.experience_to_level = 100
        self.gold = 50
        
        # Stats
        self.base_stats = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10
        }
        
        # Health
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        
        # Equipment and inventory
        self.equipment: Dict[str, Optional[Equipment]] = {
            "weapon": None,
            "armor": None,
            "helmet": None,
            "boots": None,
            "accessory": None
        }
        self.inventory: List[Item] = []
        
        # Skills and combat
        self.skills: List[Skill] = []
        self.combat_sequence: List[Skill] = []
        
        # Initialize with default equipment and skills
        self._initialize_defaults()
        
    def _initialize_defaults(self):
        from .items import Weapon, Armor
        from .skills import BasicAttack, Defend
        
        # Add starter equipment
        starter_sword = Weapon("Wooden Sword", 2, 0, 0)
        starter_armor = Armor("Cloth Tunic", 1, 0, 0)
        
        self.equip_item(starter_sword)
        self.equip_item(starter_armor)
        
        # Add basic skills
        self.learn_skill(BasicAttack())
        self.learn_skill(Defend())
        
        # Set initial combat sequence
        self.combat_sequence = [self.skills[0]] * 3  # Just use basic attack for now
        
    def _calculate_max_hp(self) -> int:
        base_hp = 50
        con_bonus = self.base_stats["constitution"] * 5
        level_bonus = (self.level - 1) * 20
        return base_hp + con_bonus + level_bonus
        
    def get_stats(self) -> Dict[str, int]:
        """Return combined stats from base stats and equipment"""
        stats = self.base_stats.copy()
        
        # Add bonuses from equipment
        for slot, item in self.equipment.items():
            if item:
                for stat, value in item.stat_bonuses.items():
                    if stat in stats:
                        stats[stat] += value
        
        return stats
        
    def equip_item(self, item: Equipment) -> bool:
        """Equip an item in the appropriate slot"""
        if item.slot in self.equipment:
            # Unequip existing item if any
            old_item = self.equipment[item.slot]
            if old_item:
                self.inventory.append(old_item)
                
            # Equip new item
            self.equipment[item.slot] = item
            
            # Update health if constitution changed
            old_max_hp = self.max_hp
            self.max_hp = self._calculate_max_hp()
            
            # Adjust current HP proportionally if max HP changed
            if old_max_hp != self.max_hp:
                self.current_hp = int(self.current_hp * (self.max_hp / old_max_hp))
                
            return True
        return False
        
    def unequip_item(self, slot: str) -> bool:
        """Unequip an item from the specified slot"""
        if slot in self.equipment and self.equipment[slot]:
            item = self.equipment[slot]
            self.inventory.append(item)
            self.equipment[slot] = None
            
            # Update health if constitution changed
            old_max_hp = self.max_hp
            self.max_hp = self._calculate_max_hp()
            
            # Adjust current HP proportionally if max HP changed
            if old_max_hp != self.max_hp:
                self.current_hp = int(self.current_hp * (self.max_hp / old_max_hp))
                
            return True
        return False
        
    def learn_skill(self, skill: Skill) -> bool:
        """Learn a new skill if player doesn't already know it"""
        for existing_skill in self.skills:
            if existing_skill.name == skill.name:
                return False  # Already knows this skill
                
        self.skills.append(skill)
        return True
        
    def add_to_combat_sequence(self, skill: Skill, position: int) -> bool:
        """Add a skill to the combat sequence at the specified position"""
        if skill in self.skills and 0 <= position < 5:  # Limit to 5 skills in sequence
            if len(self.combat_sequence) <= position:
                # Extend the sequence if needed
                self.combat_sequence.extend([None] * (position - len(self.combat_sequence) + 1))
            self.combat_sequence[position] = skill
            return True
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
        
        # Increase base stats
        for stat in self.base_stats:
            self.base_stats[stat] += 2
            
        # Update health
        old_max_hp = self.max_hp
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp  # Full heal on level up
        
    def take_damage(self, amount: int) -> int:
        """Take damage and return the actual amount taken"""
        # Apply damage reduction from armor
        damage_reduction = 0
        for slot, item in self.equipment.items():
            if item and hasattr(item, 'defense'):
                damage_reduction += item.defense
                
        # Minimum 1 damage
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
        """Check if the player is alive"""
        return self.current_hp > 0