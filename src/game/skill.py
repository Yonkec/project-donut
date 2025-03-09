from typing import Dict, Any, Callable, List, Optional, Set
import random
import os
import pygame

# Initialize sound variables
attack_sound = None
heal_sound = None
sounds_initialized = False

def init_sounds():
    global attack_sound, heal_sound, sounds_initialized
    
    if sounds_initialized:
        return
        
    try:
        if pygame.mixer.get_init() is None:
            return
            
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'audio')
        attack_sound_path = os.path.join(audio_dir, 'attack.wav')
        heal_sound_path = os.path.join(audio_dir, 'heal.wav')
        
        if os.path.exists(attack_sound_path):
            attack_sound = pygame.mixer.Sound(attack_sound_path)
        if os.path.exists(heal_sound_path):
            heal_sound = pygame.mixer.Sound(heal_sound_path)
            
        sounds_initialized = True
    except Exception as e:
        print(f"Error loading skill sounds: {e}")

class Skill:
    def __init__(self, skill_id: str, data: Dict[str, Any], effect_functions: Dict[str, Callable]):
        self.id = skill_id
        self.name = data["name"]
        self.description = data["description"]
        self.energy_cost = data.get("energy_cost", 0)
        self.action_cost = data.get("action_cost", 5.0)
        self.cooldown = data.get("cooldown", 0)
        self.current_cooldown = 0
        self.effects = data.get("effects", [])
        self.effect_functions = effect_functions
        self.conditions = data.get("conditions", [])
        self.sound = data.get("sound")
        self.category = data.get("category", "general")
        self.tags = data.get("tags", [])
        
    def can_use(self, user) -> bool:
        if self.current_cooldown > 0:
            return False
            
        # Check energy cost
        if hasattr(user, 'energy') and user.energy < self.energy_cost:
            return False
            
        # Check action cost if user has an action manager
        if hasattr(user, 'action_manager') and user.action_manager is not None and hasattr(user, 'id'):
            current_action = user.action_manager.get_current_action(user.id)
            if current_action < self.action_cost:
                return False
                
        # Check conditions (e.g., minimum stats, required equipment)
        for condition in self.conditions:
            condition_type = condition["type"]
            if condition_type == "min_stat":
                stat = condition["stat"]
                value = condition["value"]
                if hasattr(user, 'get_stats') and user.get_stats().get(stat, 0) < value:
                    return False
            elif condition_type == "required_item":
                item_type = condition["item_type"]
                if not self._has_required_item(user, item_type):
                    return False
                    
        return True
        
    def _has_required_item(self, user, item_type: str) -> bool:
        if hasattr(user, 'equipment') and user.equipment:
            for slot, item in user.equipment.items():
                if item and hasattr(item, 'type') and item.type == item_type:
                    return True
        return False
        
    def use(self, user, target) -> Dict[str, Any]:
        self.current_cooldown = self.cooldown
        
        # Consume energy if applicable
        if hasattr(user, 'energy'):
            user.energy -= self.energy_cost
            
        # Consume action if applicable
        if hasattr(user, 'action_manager') and user.action_manager is not None and hasattr(user, 'id'):
            user.action_manager.consume_action(user.id, self.action_cost)
            
        # Initialize sounds if needed
        init_sounds()
            
        # Play sound if specified
        if self.sound == "attack" and attack_sound:
            attack_sound.play()
        elif self.sound == "heal" and heal_sound:
            heal_sound.play()
            
        result = {"success": True, "message": f"{user.name} used {self.name}"}
        
        # Apply each effect
        for effect in self.effects:
            effect_type = effect["type"]
            if effect_type in self.effect_functions:
                params = effect.get("params", {})
                
                # Add basic user and target info to params
                params["user"] = user.name
                params["target"] = target.name if hasattr(target, 'name') else "target"
                
                # Let the effect function handle the message formatting
                effect_result = self.effect_functions[effect_type](user, target, params)
                
                # Format any message templates in the result
                if "message" in effect_result and isinstance(effect_result["message"], str):
                    effect_result["message"] = effect_result["message"].format(
                        user=user.name,
                        target=target.name if hasattr(target, 'name') else "target",
                        **{k: v for k, v in effect_result.items() if k != "message"}
                    )
                    
                # Merge effect result with overall result
                result.update(effect_result)
                
        return result
        
    def reset_cooldown(self) -> None:
        self.current_cooldown = 0
        
    def update_cooldown(self) -> None:
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            
    def has_tag(self, tag: str) -> bool:
        return tag in self.tags
        
    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
            
    def remove_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            
    def set_category(self, category: str) -> None:
        self.category = category
