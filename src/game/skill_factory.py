from typing import Dict, List, Any, Optional, Callable, Union
from .skill import Skill
from .skill_manager import SkillManager

class SkillBuilder:
    def __init__(self, skill_id: str, name: str, description: str):
        self.skill_data = {
            "id": skill_id,
            "name": name,
            "description": description,
            "energy_cost": 0,
            "action_cost": 5.0,
            "cooldown": 0,
            "effects": [],
            "conditions": [],
            "tags": [],
            "category": "general"
        }
        
    def with_energy_cost(self, cost: int) -> 'SkillBuilder':
        self.skill_data["energy_cost"] = cost
        return self
        
    def with_action_cost(self, cost: float) -> 'SkillBuilder':
        self.skill_data["action_cost"] = cost
        return self
        
    def with_cooldown(self, cooldown: int) -> 'SkillBuilder':
        self.skill_data["cooldown"] = cooldown
        return self
        
    def with_sound(self, sound_type: str) -> 'SkillBuilder':
        self.skill_data["sound"] = sound_type
        return self
        
    def with_category(self, category: str) -> 'SkillBuilder':
        self.skill_data["category"] = category
        return self
        
    def with_tags(self, tags: List[str]) -> 'SkillBuilder':
        self.skill_data["tags"] = tags
        return self
        
    def add_tag(self, tag: str) -> 'SkillBuilder':
        if "tags" not in self.skill_data:
            self.skill_data["tags"] = []
        self.skill_data["tags"].append(tag)
        return self
        
    def add_damage_effect(self, base_value: int, 
                         weapon_scaling: float = 0.0,
                         stat_scaling: Dict[str, float] = None,
                         variance_min: float = 0.8,
                         variance_max: float = 1.2,
                         message: str = "") -> 'SkillBuilder':
        effect = {
            "type": "damage",
            "params": {
                "base_value": base_value,
                "weapon_scaling": weapon_scaling,
                "variance_min": variance_min,
                "variance_max": variance_max
            }
        }
        
        if stat_scaling:
            effect["params"]["stat_scaling"] = stat_scaling
            
        if message:
            effect["params"]["message"] = message
            
        self.skill_data["effects"].append(effect)
        return self
        
    def add_healing_effect(self, base_value: int,
                          stat_scaling: Dict[str, float] = None,
                          variance_min: float = 0.9,
                          variance_max: float = 1.1,
                          message: str = "") -> 'SkillBuilder':
        effect = {
            "type": "healing",
            "params": {
                "base_value": base_value,
                "variance_min": variance_min,
                "variance_max": variance_max
            }
        }
        
        if stat_scaling:
            effect["params"]["stat_scaling"] = stat_scaling
            
        if message:
            effect["params"]["message"] = message
            
        self.skill_data["effects"].append(effect)
        return self
        
    def add_buff_effect(self, buff_type: str, value: int, duration: int,
                       message: str = "") -> 'SkillBuilder':
        effect = {
            "type": "buff",
            "params": {
                "buff_type": buff_type,
                "value": value,
                "duration": duration
            }
        }
        
        if message:
            effect["params"]["message"] = message
            
        self.skill_data["effects"].append(effect)
        return self
        
    def add_status_effect(self, status_type: str, value: int, duration: int,
                         chance: float = 1.0, message: str = "") -> 'SkillBuilder':
        effect = {
            "type": "status",
            "params": {
                "status_type": status_type,
                "value": value,
                "duration": duration,
                "chance": chance
            }
        }
        
        if message:
            effect["params"]["message"] = message
            
        self.skill_data["effects"].append(effect)
        return self
        
    def add_multi_hit_effect(self, base_value: int, min_hits: int = 1, max_hits: int = 3,
                            hit_chance: float = 0.8, damage_scaling: float = 0.8,
                            weapon_scaling: float = 0.0, stat_scaling: Dict[str, float] = None,
                            variance_min: float = 0.8, variance_max: float = 1.2,
                            message: str = "") -> 'SkillBuilder':
        effect = {
            "type": "multi_hit",
            "params": {
                "base_value": base_value,
                "min_hits": min_hits,
                "max_hits": max_hits,
                "hit_chance": hit_chance,
                "damage_scaling": damage_scaling,
                "weapon_scaling": weapon_scaling,
                "variance_min": variance_min,
                "variance_max": variance_max
            }
        }
        
        if stat_scaling:
            effect["params"]["stat_scaling"] = stat_scaling
            
        if message:
            effect["params"]["message"] = message
            
        self.skill_data["effects"].append(effect)
        return self
        
    def add_custom_effect(self, effect_type: str, params: Dict[str, Any]) -> 'SkillBuilder':
        effect = {
            "type": effect_type,
            "params": params
        }
        
        self.skill_data["effects"].append(effect)
        return self
        
    def add_min_stat_condition(self, stat: str, value: int) -> 'SkillBuilder':
        condition = {
            "type": "min_stat",
            "stat": stat,
            "value": value
        }
        
        self.skill_data["conditions"].append(condition)
        return self
        
    def add_required_item_condition(self, item_type: str) -> 'SkillBuilder':
        condition = {
            "type": "required_item",
            "item_type": item_type
        }
        
        self.skill_data["conditions"].append(condition)
        return self
        
    def add_custom_condition(self, condition_type: str, params: Dict[str, Any]) -> 'SkillBuilder':
        condition = {
            "type": condition_type,
            **params
        }
        
        self.skill_data["conditions"].append(condition)
        return self
        
    def build(self, skill_manager: SkillManager) -> Skill:
        skill_id = self.skill_data.pop("id")
        return skill_manager.create_skill(skill_id, self.skill_data)
        
    def get_data(self) -> Dict[str, Any]:
        return self.skill_data.copy()


class SkillFactory:
    @staticmethod
    def create_basic_attack(skill_manager: SkillManager, weapon_scaling: float = 1.0) -> Skill:
        return (SkillBuilder("basic_attack", "Basic Attack", "A simple attack with your weapon")
                .with_action_cost(3.0)
                .with_sound("attack")
                .with_category("physical")
                .with_tags(["attack", "physical", "basic"])
                .add_damage_effect(5, weapon_scaling=weapon_scaling, 
                                  stat_scaling={"strength": 0.5})
                .build(skill_manager))
    
    @staticmethod
    def create_defend(skill_manager: SkillManager) -> Skill:
        return (SkillBuilder("defend", "Defend", "Take a defensive stance to reduce incoming damage")
                .with_action_cost(2.0)
                .with_category("defensive")
                .with_tags(["defensive", "buff"])
                .add_buff_effect("defense", 3, 1, 
                                message="{user} takes a defensive stance!")
                .build(skill_manager))
    
    @staticmethod
    def create_fireball(skill_manager: SkillManager) -> Skill:
        return (SkillBuilder("fireball", "Fireball", "Hurl a ball of fire at your enemy")
                .with_energy_cost(10)
                .with_action_cost(5.0)
                .with_cooldown(2)
                .with_sound("attack")
                .with_category("magic")
                .with_tags(["attack", "magic", "fire"])
                .add_damage_effect(15, stat_scaling={"intelligence": 1.5},
                                  message="{user} hurls a fireball at {target} for {damage} damage!")
                .add_min_stat_condition("intelligence", 12)
                .build(skill_manager))
    
    @staticmethod
    def create_heal(skill_manager: SkillManager) -> Skill:
        return (SkillBuilder("heal", "Heal", "Restore health to yourself or an ally")
                .with_energy_cost(15)
                .with_action_cost(4.0)
                .with_cooldown(3)
                .with_sound("heal")
                .with_category("magic")
                .with_tags(["healing", "magic", "support"])
                .add_healing_effect(20, stat_scaling={"wisdom": 1.5},
                                   message="{user} heals {target} for {healing} health!")
                .add_min_stat_condition("wisdom", 12)
                .build(skill_manager))
    
    @staticmethod
    def create_quick_strike(skill_manager: SkillManager) -> Skill:
        return (SkillBuilder("quick_strike", "Quick Strike", "A fast attack that strikes multiple times")
                .with_action_cost(4.0)
                .with_cooldown(2)
                .with_sound("attack")
                .with_category("physical")
                .with_tags(["attack", "physical", "multi"])
                .add_multi_hit_effect(4, min_hits=2, max_hits=3, 
                                     stat_scaling={"dexterity": 0.8},
                                     message="{user} strikes {target} with lightning speed!")
                .add_min_stat_condition("dexterity", 12)
                .build(skill_manager))
    
    @staticmethod
    def create_power_attack(skill_manager: SkillManager) -> Skill:
        return (SkillBuilder("power_attack", "Power Attack", "A powerful attack that deals heavy damage")
                .with_action_cost(6.0)
                .with_cooldown(3)
                .with_sound("attack")
                .with_category("physical")
                .with_tags(["attack", "physical", "heavy"])
                .add_damage_effect(20, weapon_scaling=1.5, stat_scaling={"strength": 2.0},
                                  message="{user} delivers a devastating blow to {target} for {damage} damage!")
                .add_min_stat_condition("strength", 14)
                .build(skill_manager))
    
    @staticmethod
    def create_poison_dart(skill_manager: SkillManager) -> Skill:
        return (SkillBuilder("poison_dart", "Poison Dart", "Fire a poisoned dart that deals damage over time")
                .with_action_cost(4.0)
                .with_cooldown(4)
                .with_category("physical")
                .with_tags(["attack", "physical", "poison"])
                .add_damage_effect(5, stat_scaling={"dexterity": 0.5})
                .add_status_effect("poison", 3, 3, chance=0.8,
                                  message="{target} is poisoned and will take damage over time!")
                .build(skill_manager))
    
    @staticmethod
    def create_custom_skill(skill_manager: SkillManager, 
                           skill_id: str, 
                           name: str, 
                           description: str,
                           builder_func: Callable[[SkillBuilder], SkillBuilder]) -> Skill:
        builder = SkillBuilder(skill_id, name, description)
        builder = builder_func(builder)
        return builder.build(skill_manager)


class SkillValidator:
    @staticmethod
    def validate_skill_data(skill_data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if "name" not in skill_data:
            errors.append("Skill data missing required field: name")
            
        if "description" not in skill_data:
            errors.append("Skill data missing required field: description")
            
        if "effects" not in skill_data or not skill_data["effects"]:
            errors.append("Skill must have at least one effect")
            
        for effect in skill_data.get("effects", []):
            if "type" not in effect:
                errors.append("Effect missing required field: type")
                
            if "params" not in effect:
                errors.append(f"Effect of type {effect.get('type', 'unknown')} missing required field: params")
                
        for condition in skill_data.get("conditions", []):
            if "type" not in condition:
                errors.append("Condition missing required field: type")
                
        return errors
