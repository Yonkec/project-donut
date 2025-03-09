from typing import Dict, Optional

class Item:
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value  # Gold value
        
    def use(self, target) -> bool:
        """Use the item on the target. Returns True if successful."""
        return False

class Equipment(Item):
    VALID_SLOTS = ["weapon", "armor", "helmet", "boots", "accessory"]
    
    def __init__(self, name: str, value: int, slot: str, stat_bonuses: Optional[Dict[str, int]] = None):
        super().__init__(name, value)
        
        if slot not in self.VALID_SLOTS:
            raise ValueError(f"Invalid equipment slot: {slot}. Must be one of {self.VALID_SLOTS}")
            
        self.slot = slot
        self.stat_bonuses = stat_bonuses or {}

class Weapon(Equipment):
    def __init__(self, name: str, damage: int, value: int, str_bonus: int = 0, dex_bonus: int = 0):
        stat_bonuses = {"strength": str_bonus, "dexterity": dex_bonus}
        super().__init__(name, value, "weapon", stat_bonuses)
        self._damage = damage  # Use a protected attribute
        
    @property
    def damage(self):
        return self._damage
        
    @damage.setter
    def damage(self, value):
        self._damage = value

class Armor(Equipment):
    def __init__(self, name: str, defense: int, value: int, con_bonus: int = 0):
        stat_bonuses = {"constitution": con_bonus}
        super().__init__(name, value, "armor", stat_bonuses)
        self._defense = defense
        
    @property
    def defense(self):
        return self._defense
        
    @defense.setter
    def defense(self, value):
        self._defense = value

class Helmet(Equipment):
    def __init__(self, name: str, defense: int, value: int, int_bonus: int = 0):
        stat_bonuses = {"intelligence": int_bonus}
        super().__init__(name, value, "helmet", stat_bonuses)
        self._defense = defense
        
    @property
    def defense(self):
        return self._defense
        
    @defense.setter
    def defense(self, value):
        self._defense = value

class Boots(Equipment):
    def __init__(self, name: str, defense: int, value: int, dex_bonus: int = 0):
        stat_bonuses = {"dexterity": dex_bonus}
        super().__init__(name, value, "boots", stat_bonuses)
        self._defense = defense
        
    @property
    def defense(self):
        return self._defense
        
    @defense.setter
    def defense(self, value):
        self._defense = value

class Accessory(Equipment):
    def __init__(self, name: str, value: int, stat_bonuses: Dict[str, int]):
        super().__init__(name, value, "accessory", stat_bonuses)

class Potion(Item):
    def __init__(self, name: str, value: int, effect_type: str, effect_value: int):
        super().__init__(name, value)
        self.effect_type = effect_type  # "heal", "strength", etc.
        self.effect_value = effect_value
        
    def use(self, target) -> bool:
        if self.effect_type == "heal":
            if hasattr(target, 'heal'):
                target.heal(self.effect_value)
                return True
        return False

def create_starter_weapon() -> Weapon:
    return Weapon("Wooden Sword", 3, 10)

def create_starter_armor() -> Armor:
    return Armor("Cloth Tunic", 2, 10)

def create_health_potion(tier: int = 1) -> Potion:
    if tier == 1:
        return Potion("Minor Health Potion", 20, "heal", 30)
    elif tier == 2:
        return Potion("Health Potion", 50, "heal", 70)
    else:
        return Potion("Major Health Potion", 100, "heal", 150)