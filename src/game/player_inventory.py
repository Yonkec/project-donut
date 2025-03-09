from typing import Dict, List, Optional, Any
from .items import Item, Equipment

class PlayerInventory:
    def __init__(self, player):
        self.player = player
        self.equipment: Dict[str, Optional[Equipment]] = {
            "weapon": None,
            "armor": None,
            "helmet": None,
            "boots": None,
            "accessory": None
        }
        self.inventory: List[Item] = []
        self._initialize_defaults()

    def _initialize_defaults(self):
        from .items import Weapon, Armor
        
        starter_sword = Weapon("Wooden Sword", 2, 0, 0)
        starter_armor = Armor("Cloth Tunic", 1, 0, 0)
        
        self.equip_item(starter_sword)
        self.equip_item(starter_armor)

    def get_equipment_stats(self) -> Dict[str, int]:
        stats = {}
        
        for slot, item in self.equipment.items():
            if item:
                for stat, value in item.stat_bonuses.items():
                    if stat in stats:
                        stats[stat] += value
                    else:
                        stats[stat] = value
        
        return stats
        
    def equip_item(self, item: Equipment) -> bool:
        if item.slot in self.equipment:
            old_item = self.equipment[item.slot]
            if old_item:
                self.inventory.append(old_item)
                
            self.equipment[item.slot] = item
            self.player._update_hp_after_stat_change()
            return True
        return False
        
    def unequip_item(self, slot: str) -> bool:
        if slot in self.equipment and self.equipment[slot]:
            item = self.equipment[slot]
            self.inventory.append(item)
            self.equipment[slot] = None
            self.player._update_hp_after_stat_change()
            return True
        return False
    
    def get_defense(self) -> int:
        defense = 0
        for slot, item in self.equipment.items():
            if item and hasattr(item, 'defense'):
                defense += item.defense
        return defense
    
    def add_to_inventory(self, item: Item) -> bool:
        self.inventory.append(item)
        return True
    
    def remove_from_inventory(self, item: Item) -> bool:
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name == name:
                return item
        return None
