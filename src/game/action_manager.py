from typing import Dict, List, Any, Optional, Callable, Set
import random
import logging

class ActionManager:
    def __init__(self):
        self.action_generators = {}
        self.action_consumers = {}
        
    def register_entity(self, entity_id: str, base_action_rate: float = 1.0):
        logging.debug(f"Registering entity {entity_id} with base rate {base_action_rate}")
        self.action_generators[entity_id] = {
            "base_rate": base_action_rate,
            "current_rate": base_action_rate,
            "modifiers": {}
        }
        self.action_consumers[entity_id] = {
            "current_action": 0.0,
            "next_skill": None,
            "skill_sequence": []
        }
    
    def unregister_entity(self, entity_id: str):
        self.action_generators.pop(entity_id, None)
        self.action_consumers.pop(entity_id, None)
    
    def set_action_rate(self, entity_id: str, rate: float):
        if self._entity_exists(entity_id):
            self.action_generators[entity_id]["base_rate"] = rate
            self._recalculate_action_rate(entity_id)
    
    def add_action_modifier(self, entity_id: str, modifier_id: str, value: float, duration: int = -1):
        if self._entity_exists(entity_id):
            self.action_generators[entity_id]["modifiers"][modifier_id] = {
                "value": value,
                "duration": duration
            }
            self._recalculate_action_rate(entity_id)
    
    def remove_action_modifier(self, entity_id: str, modifier_id: str):
        if self._entity_exists(entity_id) and modifier_id in self.action_generators[entity_id]["modifiers"]:
            del self.action_generators[entity_id]["modifiers"][modifier_id]
            self._recalculate_action_rate(entity_id)
    
    def _entity_exists(self, entity_id: str) -> bool:
        return entity_id in self.action_generators and entity_id in self.action_consumers
        
    def _recalculate_action_rate(self, entity_id: str):
        if entity_id not in self.action_generators:
            return
            
        base_rate = self.action_generators[entity_id]["base_rate"]
        total_modifier = sum(mod["value"] for mod in self.action_generators[entity_id]["modifiers"].values())
        
        # Apply modifiers (can be positive for haste or negative for slow)
        new_rate = max(0.0, base_rate * (1.0 + total_modifier))
        self.action_generators[entity_id]["current_rate"] = new_rate
    
    def update_action_modifiers(self, entity_id: str) -> List[str]:
        if entity_id not in self.action_generators:
            return []
            
        expired_modifiers = []
        modifiers = self.action_generators[entity_id]["modifiers"]
        
        for modifier_id, modifier_data in list(modifiers.items()):
            if modifier_data["duration"] > 0:
                modifier_data["duration"] -= 1
                if modifier_data["duration"] <= 0:
                    expired_modifiers.append(modifier_id)
                    del modifiers[modifier_id]
        
        if expired_modifiers:
            self._recalculate_action_rate(entity_id)
            
        return expired_modifiers
    
    def get_current_action(self, entity_id: str) -> float:
        if entity_id in self.action_consumers:
            return self.action_consumers[entity_id]["current_action"]
        return 0.0
    
    def get_action_rate(self, entity_id: str) -> float:
        if entity_id in self.action_generators:
            return self.action_generators[entity_id]["current_rate"]
        return 0.0
    
    def is_stunned(self, entity_id: str) -> bool:
        if entity_id in self.action_generators:
            return "stunned" in self.action_generators[entity_id]["modifiers"]
        return False
    
    def generate_action(self, entity_id: str, tick_time: float = 1.0) -> float:
        if not self._entity_exists(entity_id):
            return 0.0
        
        # Don't generate action if stunned
        if self.is_stunned(entity_id):
            return 0.0
            
        rate = self.action_generators[entity_id]["current_rate"]
        action_gained = rate * tick_time
        
        # Add the action points
        self.action_consumers[entity_id]["current_action"] += action_gained
        
        return action_gained
    
    def consume_action(self, entity_id: str, amount: float) -> bool:
        if entity_id not in self.action_consumers:
            return False
            
        current = self.action_consumers[entity_id]["current_action"]
        
        if current >= amount:
            self.action_consumers[entity_id]["current_action"] -= amount
            return True
        
        return False
    
    def reduce_action(self, entity_id: str, amount: float) -> float:
        if entity_id not in self.action_consumers:
            return 0.0
            
        current = self.action_consumers[entity_id]["current_action"]
        reduction = min(current, amount)
        
        self.action_consumers[entity_id]["current_action"] -= reduction
        return reduction
    
    def set_next_skill(self, entity_id: str, skill):
        if entity_id in self.action_consumers:
            self.action_consumers[entity_id]["next_skill"] = skill
    
    def get_next_skill(self, entity_id: str):
        if entity_id in self.action_consumers:
            return self.action_consumers[entity_id]["next_skill"]
        return None
    
    def set_skill_sequence(self, entity_id: str, skill_sequence: List):
        if entity_id in self.action_consumers:
            self.action_consumers[entity_id]["skill_sequence"] = skill_sequence.copy()
    
    def get_skill_sequence(self, entity_id: str) -> List:
        if entity_id in self.action_consumers:
            return self.action_consumers[entity_id]["skill_sequence"].copy()
        return []
    
    def update_skill_sequence(self, entity_id: str):
        if entity_id not in self.action_consumers or not self.action_consumers[entity_id]["skill_sequence"]:
            return
            
        # Set the next skill from the sequence if not already set
        if self.action_consumers[entity_id]["next_skill"] is None:
            next_skill = self.action_consumers[entity_id]["skill_sequence"][0]
            self.action_consumers[entity_id]["next_skill"] = next_skill
    
    def cycle_skill_sequence(self, entity_id: str):
        if entity_id not in self.action_consumers:
            return
            
        sequence = self.action_consumers[entity_id]["skill_sequence"]
        if not sequence:
            return
            
        # Move the first skill to the end of the sequence
        first_skill = sequence.pop(0)
        sequence.append(first_skill)
        
        # Set the next skill from the updated sequence
        self.action_consumers[entity_id]["next_skill"] = sequence[0] if sequence else None
