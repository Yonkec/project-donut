from typing import Dict, List, Any, Callable, Optional
import random
import os
import pygame
from .skill_database import SkillDatabase

# Initialize sound effects
attack_sound = None
heal_sound = None

# Load sound effects
try:
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'audio')
    attack_sound_path = os.path.join(audio_dir, 'attack.wav')
    heal_sound_path = os.path.join(audio_dir, 'heal.wav')
    
    if os.path.exists(attack_sound_path):
        attack_sound = pygame.mixer.Sound(attack_sound_path)
    if os.path.exists(heal_sound_path):
        heal_sound = pygame.mixer.Sound(heal_sound_path)
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
        """Create a skill from data, possibly using a template"""
        if "template" in skill_data and skill_data["template"] in self.database.templates:
            # Start with template and override with specific data
            template = self.database.get_template(skill_data["template"]).copy()
            for key, value in skill_data.items():
                if key != "template":
                    if key == "effects" and "effects" in template:
                        # For effects, we might want to replace or extend
                        if skill_data.get("extend_effects", False):
                            template[key].extend(value)
                        else:
                            template[key] = value
                    else:
                        template[key] = value
            skill_data = template
            
        # Create the skill object
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
        
        # Damage effect
        def damage_effect(user, target, params):
            # Calculate base damage
            base_damage = params.get("base_value", 0)
            
            # Add weapon damage if applicable
            weapon_scaling = params.get("weapon_scaling", 0)
            if weapon_scaling > 0 and hasattr(user, 'equipment') and user.equipment.get('weapon'):
                base_damage += user.equipment['weapon'].damage * weapon_scaling
                
            # Add stat scaling
            stat_scaling = params.get("stat_scaling", {})
            if hasattr(user, 'get_stats'):
                stats = user.get_stats()
                for stat, scale in stat_scaling.items():
                    base_damage += stats.get(stat, 0) * scale
                    
            # Apply random variance
            variance_min = params.get("variance_min", 0.8)
            variance_max = params.get("variance_max", 1.2)
            variance = random.uniform(variance_min, variance_max)
            damage = max(1, int(base_damage * variance))
            
            # Apply damage to target
            actual_damage = target.take_damage(damage)
            
            # Create message if not provided
            message = params.get("message", "")
            if not message:
                message = f"{user.name} deals {actual_damage} damage to {target.name}!"
            else:
                message = message.format(user=user.name, target=target.name, damage=actual_damage)
                
            return {
                "damage": actual_damage,
                "message": message
            }
            
        # Healing effect
        def healing_effect(user, target, params):
            # Calculate base healing
            base_healing = params.get("base_value", 0)
            
            # Add stat scaling
            stat_scaling = params.get("stat_scaling", {})
            if hasattr(user, 'get_stats'):
                stats = user.get_stats()
                for stat, scale in stat_scaling.items():
                    base_healing += stats.get(stat, 0) * scale
                    
            # Apply random variance
            variance_min = params.get("variance_min", 0.9)
            variance_max = params.get("variance_max", 1.1)
            variance = random.uniform(variance_min, variance_max)
            healing = max(1, int(base_healing * variance))
            
            # Apply healing
            actual_healing = target.heal(healing)
            
            # Create message if not provided
            message = params.get("message", "")
            if not message:
                message = f"{user.name} heals {target.name} for {actual_healing} health!"
            else:
                message = message.format(user=user.name, target=target.name, healing=actual_healing)
                
            return {
                "healing": actual_healing,
                "message": message
            }
            
        # Buff effect
        def buff_effect(user, target, params):
            buff_type = params.get("buff_type", "defense")
            value = params.get("value", 1)
            duration = params.get("duration", 3)
            
            # Apply buff to target
            if not hasattr(target, 'buffs'):
                target.buffs = {}
                
            target.buffs[buff_type] = {
                "value": value,
                "duration": duration
            }
            
            # Create message if not provided
            message = params.get("message", "")
            if not message:
                message = f"{target.name} gains {value} {buff_type} for {duration} turns!"
            else:
                message = message.format(user=user.name, target=target.name, 
                                        value=value, buff_type=buff_type, duration=duration)
                
            return {
                "buff_type": buff_type,
                "value": value,
                "duration": duration,
                "message": message
            }
            
        # Status effect
        def status_effect(user, target, params):
            status_type = params.get("status_type", "poison")
            value = params.get("value", 1)
            duration = params.get("duration", 3)
            chance = params.get("chance", 1.0)
            
            # Check if status effect applies (based on chance)
            if random.random() > chance:
                return {
                    "status_applied": False,
                    "message": f"{user.name} failed to apply {status_type} to {target.name}!"
                }
                
            # Apply status to target
            if not hasattr(target, 'status_effects'):
                target.status_effects = {}
                
            target.status_effects[status_type] = {
                "value": value,
                "duration": duration
            }
            
            # Create message if not provided
            message = params.get("message", "")
            if not message:
                message = f"{target.name} is afflicted with {status_type} for {duration} turns!"
            else:
                message = message.format(user=user.name, target=target.name, 
                                        status_type=status_type, duration=duration)
                
            return {
                "status_type": status_type,
                "value": value,
                "duration": duration,
                "status_applied": True,
                "message": message
            }
            
        # Multi-hit effect
        def multi_hit_effect(user, target, params):
            # Get base damage calculation parameters
            base_damage = params.get("base_value", 0)
            weapon_scaling = params.get("weapon_scaling", 0)
            stat_scaling = params.get("stat_scaling", {})
            
            # Get multi-hit parameters
            min_hits = params.get("min_hits", 1)
            max_hits = params.get("max_hits", 1)
            hit_chance = params.get("hit_chance", 1.0)
            damage_scaling = params.get("damage_scaling", 1.0)
            
            # Calculate base damage (same as damage_effect)
            if weapon_scaling > 0 and hasattr(user, 'equipment') and user.equipment.get('weapon'):
                base_damage += user.equipment['weapon'].damage * weapon_scaling
                
            if hasattr(user, 'get_stats'):
                stats = user.get_stats()
                for stat, scale in stat_scaling.items():
                    base_damage += stats.get(stat, 0) * scale
            
            # Determine number of hits
            if min_hits == max_hits:
                num_hits = min_hits
            else:
                # Determine hits based on chance
                num_hits = 0
                for _ in range(max_hits):
                    if random.random() < hit_chance:
                        num_hits += 1
                num_hits = max(min_hits, num_hits)
                
            # Apply hits
            total_damage = 0
            hit_results = []
            
            for hit in range(num_hits):
                # Calculate damage for this hit
                hit_damage_scaling = damage_scaling ** hit  # Diminishing returns for later hits
                
                # Apply random variance
                variance_min = params.get("variance_min", 0.8)
                variance_max = params.get("variance_max", 1.2)
                variance = random.uniform(variance_min, variance_max)
                
                damage = max(1, int(base_damage * hit_damage_scaling * variance))
                actual_damage = target.take_damage(damage)
                total_damage += actual_damage
                
                hit_results.append({
                    "hit": hit + 1,
                    "damage": actual_damage
                })
                
            # Create message
            if num_hits == 1:
                message = f"{user.name} hits {target.name} for {total_damage} damage!"
            else:
                message = f"{user.name} hits {target.name} {num_hits} times for {total_damage} total damage!"
                
            return {
                "hits": num_hits,
                "total_damage": total_damage,
                "hit_results": hit_results,
                "message": message
            }
            
        # Register all the effect functions
        self.register_effect("damage", damage_effect)
        self.register_effect("healing", healing_effect)
        self.register_effect("buff", buff_effect)
        self.register_effect("status", status_effect)
        self.register_effect("multi_hit", multi_hit_effect)
