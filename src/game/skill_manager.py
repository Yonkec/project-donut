from typing import Dict, List, Any, Callable, Optional
import random
import os
import pygame
from .skill_database import SkillDatabase

# Initialize sound variables
attack_sound = None
heal_sound = None
sounds_initialized = False

def init_sounds():
    """Initialize sound effects when pygame is ready"""
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
    """
    Represents a skill created from data.
    """
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
        
    def can_use(self, user) -> bool:
        """Check if the skill can be used"""
        if self.current_cooldown > 0:
            return False
            
        # Check energy cost
        if hasattr(user, 'energy') and user.energy < self.energy_cost:
            return False
            
        # Check action cost if user has an action manager
        if hasattr(user, 'action_manager') and hasattr(user, 'id'):
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
                    
        return True
        
    def use(self, user, target) -> Dict[str, Any]:
        """Use the skill and apply all effects"""
        self.current_cooldown = self.cooldown
        
        # Consume energy if applicable
        if hasattr(user, 'energy'):
            user.energy -= self.energy_cost
            
        # Consume action if applicable
        if hasattr(user, 'action_manager') and hasattr(user, 'id'):
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
                effect_result = self.effect_functions[effect_type](user, target, effect.get("params", {}))
                # Merge effect result with overall result
                result.update(effect_result)
                
        return result
        
    def reset_cooldown(self) -> None:
        """Reset the skill cooldown to 0"""
        self.current_cooldown = 0
        
    def update_cooldown(self) -> None:
        """Reduce the cooldown by 1 if it's greater than 0"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class SkillManager:
    """
    Manages skill creation and effect registration.
    """
    def __init__(self, database: Optional[SkillDatabase] = None):
        self.database = database or SkillDatabase()
        self.effect_functions = {}
        self.skills = {}
        
    def register_effect(self, effect_type: str, effect_function: Callable) -> None:
        """Register an effect function that can be used by skills"""
        self.effect_functions[effect_type] = effect_function
        
    def create_skill(self, skill_id: str, skill_data: Dict[str, Any]) -> Skill:
        """Create a skill from data"""
        skill = Skill(skill_id, skill_data, self.effect_functions)
        self.skills[skill_id] = skill
        return skill
        
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by ID"""
        return self.skills.get(skill_id)
        
    def load_all_skills(self) -> None:
        """Load all skills from the database"""
        for skill_id, skill_data in self.database.get_all_skills().items():
            self.create_skill(skill_id, skill_data)
            
    def register_default_effects(self) -> None:
        """Register the default effect functions"""
        self.register_effect("damage", self._damage_effect)
        self.register_effect("healing", self._healing_effect)
        self.register_effect("buff", self._buff_effect)
        self.register_effect("status", self._status_effect)
        self.register_effect("multi_hit", self._multi_hit_effect)
        
    def _damage_effect(self, user, target, params):
        base_damage = self._calculate_base_damage(user, params)
        actual_damage = target.take_damage(base_damage)
        message = self._format_damage_message(user, target, actual_damage, params)
        
        return {
            "damage": actual_damage,
            "message": message
        }
    
    def _calculate_base_damage(self, user, params):
        base_damage = params.get("base_value", 0)
        base_damage = self._apply_weapon_scaling(user, base_damage, params)
        base_damage = self._apply_stat_scaling(user, base_damage, params)
        return self._apply_variance(base_damage, params)
    
    def _apply_weapon_scaling(self, user, base_damage, params):
        weapon_scaling = params.get("weapon_scaling", 0)
        if weapon_scaling > 0 and hasattr(user, 'equipment') and user.equipment.get('weapon'):
            base_damage += user.equipment['weapon'].damage * weapon_scaling
        return base_damage
    
    def _apply_stat_scaling(self, user, base_damage, params):
        stat_scaling = params.get("stat_scaling", {})
        if hasattr(user, 'get_stats'):
            stats = user.get_stats()
            for stat, scale in stat_scaling.items():
                base_damage += stats.get(stat, 0) * scale
        return base_damage
    
    def _apply_variance(self, base_value, params, is_damage=True):
        if is_damage:
            variance_min = params.get("variance_min", 0.8)
            variance_max = params.get("variance_max", 1.2)
        else:
            variance_min = params.get("variance_min", 0.9)
            variance_max = params.get("variance_max", 1.1)
            
        variance = random.uniform(variance_min, variance_max)
        return max(1, int(base_value * variance))
    
    def _format_damage_message(self, user, target, damage, params):
        message = params.get("message", "")
        if not message:
            return f"{user.name} deals {damage} damage to {target.name}!"
        return message.format(user=user.name, target=target.name, damage=damage)
    
    def _healing_effect(self, user, target, params):
        base_healing = params.get("base_value", 0)
        base_healing = self._apply_stat_scaling(user, base_healing, params)
        healing = self._apply_variance(base_healing, params, is_damage=False)
        
        actual_healing = target.heal(healing)
        message = self._format_healing_message(user, target, actual_healing, params)
        
        return {
            "healing": actual_healing,
            "message": message
        }
    
    def _format_healing_message(self, user, target, healing, params):
        message = params.get("message", "")
        if not message:
            return f"{user.name} heals {target.name} for {healing} health!"
        return message.format(user=user.name, target=target.name, healing=healing)
    
    def _buff_effect(self, user, target, params):
        buff_type = params.get("buff_type", "defense")
        value = params.get("value", 1)
        duration = params.get("duration", 3)
        
        self._apply_buff(target, buff_type, value, duration)
        message = self._format_buff_message(user, target, buff_type, value, duration, params)
        
        return {
            "buff_type": buff_type,
            "value": value,
            "duration": duration,
            "message": message
        }
    
    def _apply_buff(self, target, buff_type, value, duration):
        if not hasattr(target, 'buffs'):
            target.buffs = {}
            
        target.buffs[buff_type] = {
            "value": value,
            "duration": duration
        }
    
    def _format_buff_message(self, user, target, buff_type, value, duration, params):
        message = params.get("message", "")
        if not message:
            return f"{target.name} gains {value} {buff_type} for {duration} turns!"
        return message.format(user=user.name, target=target.name, 
                            value=value, buff_type=buff_type, duration=duration)
    
    def _status_effect(self, user, target, params):
        status_type = params.get("status_type", "poison")
        value = params.get("value", 1)
        duration = params.get("duration", 3)
        chance = params.get("chance", 1.0)
        
        if random.random() > chance:
            return {
                "status_applied": False,
                "message": f"{user.name} failed to apply {status_type} to {target.name}!"
            }
        
        self._apply_status(target, status_type, value, duration)
        message = self._format_status_message(user, target, status_type, duration, params)
        
        return {
            "status_type": status_type,
            "value": value,
            "duration": duration,
            "status_applied": True,
            "message": message
        }
    
    def _apply_status(self, target, status_type, value, duration):
        if not hasattr(target, 'status_effects'):
            target.status_effects = {}
            
        target.status_effects[status_type] = {
            "value": value,
            "duration": duration
        }
    
    def _format_status_message(self, user, target, status_type, duration, params):
        message = params.get("message", "")
        if not message:
            return f"{target.name} is afflicted with {status_type} for {duration} turns!"
        return message.format(user=user.name, target=target.name, 
                            status_type=status_type, duration=duration)
    
    def _multi_hit_effect(self, user, target, params):
        base_damage = self._calculate_base_damage_for_multi_hit(user, params)
        num_hits = self._determine_number_of_hits(params)
        
        hit_results, total_damage = self._apply_multi_hits(user, target, base_damage, num_hits, params)
        message = self._format_multi_hit_message(user, target, num_hits, total_damage)
        
        return {
            "hits": num_hits,
            "total_damage": total_damage,
            "hit_results": hit_results,
            "message": message
        }
    
    def _calculate_base_damage_for_multi_hit(self, user, params):
        base_damage = params.get("base_value", 0)
        base_damage = self._apply_weapon_scaling(user, base_damage, params)
        base_damage = self._apply_stat_scaling(user, base_damage, params)
        return base_damage
    
    def _determine_number_of_hits(self, params):
        min_hits = params.get("min_hits", 1)
        max_hits = params.get("max_hits", 1)
        hit_chance = params.get("hit_chance", 1.0)
        
        if min_hits == max_hits:
            return min_hits
        
        num_hits = 0
        for _ in range(max_hits):
            if random.random() < hit_chance:
                num_hits += 1
        return max(min_hits, num_hits)
    
    def _apply_multi_hits(self, user, target, base_damage, num_hits, params):
        total_damage = 0
        hit_results = []
        damage_scaling = params.get("damage_scaling", 1.0)
        
        for hit in range(num_hits):
            hit_damage_scaling = damage_scaling ** hit
            damage = self._calculate_hit_damage(base_damage, hit_damage_scaling, params)
            actual_damage = target.take_damage(damage)
            
            total_damage += actual_damage
            hit_results.append({
                "hit": hit + 1,
                "damage": actual_damage
            })
            
        return hit_results, total_damage
    
    def _calculate_hit_damage(self, base_damage, hit_damage_scaling, params):
        variance_min = params.get("variance_min", 0.8)
        variance_max = params.get("variance_max", 1.2)
        variance = random.uniform(variance_min, variance_max)
        
        return max(1, int(base_damage * hit_damage_scaling * variance))
    
    def _format_multi_hit_message(self, user, target, num_hits, total_damage):
        if num_hits == 1:
            return f"{user.name} hits {target.name} for {total_damage} damage!"
        return f"{user.name} hits {target.name} {num_hits} times for {total_damage} total damage!"
