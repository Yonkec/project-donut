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
        
    def to_dict(self) -> Dict[str, Any]:
        equipment_dict = {}
        for slot, item in self.equipment.items():
            if item:
                equipment_dict[slot] = item.to_dict() if hasattr(item, 'to_dict') else {
                    "name": item.name,
                    "slot": item.slot,
                    "attack": getattr(item, 'attack', 0),
                    "defense": getattr(item, 'defense', 0),
                    "stat_bonuses": getattr(item, 'stat_bonuses', {})
                }
            else:
                equipment_dict[slot] = None
                
        inventory_list = []
        for item in self.inventory:
            if hasattr(item, 'to_dict'):
                inventory_list.append(item.to_dict())
            else:
                inventory_list.append({
                    "name": item.name,
                    "slot": getattr(item, 'slot', ''),
                    "attack": getattr(item, 'attack', 0),
                    "defense": getattr(item, 'defense', 0),
                    "stat_bonuses": getattr(item, 'stat_bonuses', {})
                })
                
        return {
            "equipment": equipment_dict,
            "inventory": inventory_list
        }
        
    def from_dict(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            return
            
        from .items import Weapon, Armor, Helmet, Boots, Accessory
        
        # Clear current equipment and inventory
        for slot in self.equipment:
            self.equipment[slot] = None
        self.inventory.clear()
        
        # Restore equipment
        if "equipment" in data and isinstance(data["equipment"], dict):
            for slot, item_data in data["equipment"].items():
                if item_data is None:
                    continue
                    
                if not isinstance(item_data, dict):
                    continue
                    
                item_class = None
                if slot == "weapon":
                    item_class = Weapon
                elif slot == "armor":
                    item_class = Armor
                elif slot == "helmet":
                    item_class = Helmet
                elif slot == "boots":
                    item_class = Boots
                elif slot == "accessory":
                    item_class = Accessory
                    
                if item_class:
                    name = item_data.get("name", "Unknown Item")
                    attack = item_data.get("attack", 0)
                    defense = item_data.get("defense", 0)
                    stat_bonuses = item_data.get("stat_bonuses", {})
                    
                    item = item_class(name, attack, defense, 0)
                    item.stat_bonuses = stat_bonuses
                    self.equipment[slot] = item
        
        # Restore inventory
        if "inventory" in data and isinstance(data["inventory"], list):
            for item_data in data["inventory"]:
                if not isinstance(item_data, dict):
                    continue
                    
                name = item_data.get("name", "Unknown Item")
                slot = item_data.get("slot", "")
                attack = item_data.get("attack", 0)
                defense = item_data.get("defense", 0)
                stat_bonuses = item_data.get("stat_bonuses", {})
                
                item_class = None
                if slot == "weapon":
                    item_class = Weapon
                elif slot == "armor":
                    item_class = Armor
                elif slot == "helmet":
                    item_class = Helmet
                elif slot == "boots":
                    item_class = Boots
                elif slot == "accessory":
                    item_class = Accessory
                else:
                    item_class = Item
                    
                if item_class:
                    item = item_class(name, attack, defense, 0) if item_class != Item else Item(name)
                    if hasattr(item, 'stat_bonuses'):
                        item.stat_bonuses = stat_bonuses
                    self.inventory.append(item)
