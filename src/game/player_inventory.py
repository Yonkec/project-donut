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
        
        starter_sword = Weapon("Wooden Sword", 5, 0, 0)
        starter_armor = Armor("Cloth Tunic", 1, 0, 0)
        
        self.equip_item(starter_sword)
        self.equip_item(starter_armor)
        
        if not self.equipment["weapon"] or not self.equipment["armor"]:
            raise RuntimeError("Failed to equip starter equipment")

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
        if item.slot not in self.equipment:
            return False
            
        from .items import Weapon, Armor, Helmet, Boots, Accessory
        
        valid_slot = False
        if item.slot == "weapon" and isinstance(item, Weapon):
            valid_slot = True
        elif item.slot == "armor" and isinstance(item, Armor):
            valid_slot = True
        elif item.slot == "helmet" and isinstance(item, Helmet):
            valid_slot = True
        elif item.slot == "boots" and isinstance(item, Boots):
            valid_slot = True
        elif item.slot == "accessory" and isinstance(item, Accessory):
            valid_slot = True
            
        if not valid_slot:
            return False
        
        old_item = self.equipment[item.slot]
        if old_item:
            if not hasattr(self, 'inventory') or self.inventory is None:
                self.inventory = []
            self.inventory.append(old_item)
        
        self.equipment[item.slot] = item
        self.player._update_hp_after_stat_change()
        return True
        
    def unequip_item(self, slot: str) -> bool:
        if slot in self.equipment and self.equipment[slot]:
            item = self.equipment[slot]
            if not hasattr(self, 'inventory') or self.inventory is None:
                self.inventory = []
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
        if not hasattr(self, 'inventory') or self.inventory is None:
            self.inventory = []
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
                if hasattr(item, 'to_dict'):
                    equipment_dict[slot] = item.to_dict()
                else:
                    item_dict = {
                        "name": item.name,
                        "slot": item.slot,
                        "value": getattr(item, 'value', 0),
                        "stat_bonuses": getattr(item, 'stat_bonuses', {})
                    }
                    
                    # Save specific attributes based on item type
                    if slot == "weapon" and hasattr(item, 'damage'):
                        item_dict["damage"] = item.damage
                    elif hasattr(item, 'defense'):
                        item_dict["defense"] = item.defense
                        
                    equipment_dict[slot] = item_dict
            else:
                equipment_dict[slot] = None
                
        inventory_list = []
        for item in self.inventory:
            if hasattr(item, 'to_dict'):
                inventory_list.append(item.to_dict())
            else:
                item_dict = {
                    "name": item.name,
                    "value": getattr(item, 'value', 0),
                    "slot": getattr(item, 'slot', '')
                }
                
                # Save specific attributes based on item type
                if hasattr(item, 'damage'):
                    item_dict["damage"] = item.damage
                if hasattr(item, 'defense'):
                    item_dict["defense"] = item.defense
                if hasattr(item, 'stat_bonuses'):
                    item_dict["stat_bonuses"] = item.stat_bonuses
                    
                inventory_list.append(item_dict)
                
        return {
            "equipment": equipment_dict,
            "inventory": inventory_list
        }
        
    def from_dict(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            return
            
        from .items import Weapon, Armor, Helmet, Boots, Accessory, Item, Potion
        
        # Clear current equipment and inventory
        for slot in self.equipment:
            self.equipment[slot] = None
            
        # Ensure inventory is initialized
        if not hasattr(self, 'inventory') or self.inventory is None:
            self.inventory = []
        else:
            self.inventory.clear()
        
        # Restore equipment
        if "equipment" in data and isinstance(data["equipment"], dict):
            for slot, item_data in data["equipment"].items():
                if item_data is None:
                    continue
                    
                if not isinstance(item_data, dict):
                    continue
                    
                name = item_data.get("name", "Unknown Item")
                value = item_data.get("value", 0)
                stat_bonuses = item_data.get("stat_bonuses", {})
                
                if slot == "weapon":
                    damage = item_data.get("damage", 0)
                    str_bonus = stat_bonuses.get("strength", 0)
                    dex_bonus = stat_bonuses.get("dexterity", 0)
                    item = Weapon(name, damage, value, str_bonus, dex_bonus)
                elif slot == "armor":
                    defense = item_data.get("defense", 0)
                    con_bonus = stat_bonuses.get("constitution", 0)
                    item = Armor(name, defense, value, con_bonus)
                elif slot == "helmet":
                    defense = item_data.get("defense", 0)
                    int_bonus = stat_bonuses.get("intelligence", 0)
                    item = Helmet(name, defense, value, int_bonus)
                elif slot == "boots":
                    defense = item_data.get("defense", 0)
                    dex_bonus = stat_bonuses.get("dexterity", 0)
                    item = Boots(name, defense, value, dex_bonus)
                elif slot == "accessory":
                    item = Accessory(name, value, stat_bonuses)
                    
                self.equipment[slot] = item
        
        # Restore inventory
        if "inventory" in data and isinstance(data["inventory"], list):
            for item_data in data["inventory"]:
                if not isinstance(item_data, dict):
                    continue
                    
                name = item_data.get("name", "Unknown Item")
                value = item_data.get("value", 0)
                slot = item_data.get("slot", "")
                
                # Determine item type and create appropriate object
                if "effect_type" in item_data and "effect_value" in item_data:
                    # This is a potion
                    effect_type = item_data.get("effect_type", "heal")
                    effect_value = item_data.get("effect_value", 0)
                    item = Potion(name, value, effect_type, effect_value)
                elif slot == "weapon" and "damage" in item_data:
                    damage = item_data.get("damage", 0)
                    stat_bonuses = item_data.get("stat_bonuses", {})
                    str_bonus = stat_bonuses.get("strength", 0)
                    dex_bonus = stat_bonuses.get("dexterity", 0)
                    item = Weapon(name, damage, value, str_bonus, dex_bonus)
                elif slot in ["armor", "helmet", "boots"] and "defense" in item_data:
                    defense = item_data.get("defense", 0)
                    stat_bonuses = item_data.get("stat_bonuses", {})
                    
                    if slot == "armor":
                        con_bonus = stat_bonuses.get("constitution", 0)
                        item = Armor(name, defense, value, con_bonus)
                    elif slot == "helmet":
                        int_bonus = stat_bonuses.get("intelligence", 0)
                        item = Helmet(name, defense, value, int_bonus)
                    elif slot == "boots":
                        dex_bonus = stat_bonuses.get("dexterity", 0)
                        item = Boots(name, defense, value, dex_bonus)
                elif slot == "accessory":
                    stat_bonuses = item_data.get("stat_bonuses", {})
                    item = Accessory(name, value, stat_bonuses)
                else:
                    item = Item(name, value)
                    
                if not hasattr(self, 'inventory') or self.inventory is None:
                    self.inventory = []
                self.inventory.append(item)
