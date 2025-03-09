from typing import Dict, List, Any, Callable
import random

def register_default_effects(skill_manager):
    """Register the default effect functions with the skill manager"""
    skill_manager.register_effect("damage", damage_effect)
    skill_manager.register_effect("healing", healing_effect)
    skill_manager.register_effect("buff", buff_effect)
    skill_manager.register_effect("status", status_effect)
    skill_manager.register_effect("multi_hit", multi_hit_effect)

def damage_effect(user, target, params):
    base_damage = calculate_base_damage(user, params)
    actual_damage = target.take_damage(base_damage)
    
    # Add the damage value to the params for message formatting
    if "message" in params:
        params["damage"] = actual_damage
        
    message = format_damage_message(user, target, actual_damage, params)
    
    return {
        "damage": actual_damage,
        "message": message
    }

def calculate_base_damage(user, params):
    base_damage = params.get("base_value", 0)
    base_damage = apply_weapon_scaling(user, base_damage, params)
    base_damage = apply_stat_scaling(user, base_damage, params)
    return apply_variance(base_damage, params)

def apply_weapon_scaling(user, base_damage, params):
    weapon_scaling = params.get("weapon_scaling", 0)
    
    if weapon_scaling <= 0:
        return base_damage
        
    weapon = None
    
    if hasattr(user, 'get_weapon'):
        weapon = user.get_weapon()
    elif hasattr(user, 'equipment') and user.equipment.get('weapon'):
        weapon = user.equipment['weapon']
    
    if weapon and hasattr(weapon, 'damage'):
        damage_from_weapon = int(weapon.damage * weapon_scaling)
        base_damage += damage_from_weapon
    
    return base_damage

def apply_stat_scaling(user, base_damage, params):
    stat_scaling = params.get("stat_scaling", {})
    if hasattr(user, 'get_stats'):
        stats = user.get_stats()
        for stat, scale in stat_scaling.items():
            stat_value = stats.get(stat, 0)
            damage_from_stat = stat_value * scale
            base_damage += damage_from_stat
    return base_damage

def apply_variance(base_value, params, is_damage=True):
    if is_damage:
        variance_min = params.get("variance_min", 0.8)
        variance_max = params.get("variance_max", 1.2)
    else:
        variance_min = params.get("variance_min", 0.9)
        variance_max = params.get("variance_max", 1.1)
        
    variance = random.uniform(variance_min, variance_max)
    final_value = max(1, int(base_value * variance))
    return final_value

def format_damage_message(user, target, damage, params):
    message = params.get("message", "")
    if not message:
        return f"{user.name} deals {damage} damage to {target.name}!"
    
    # Add values to params for message formatting
    params["user"] = user.name
    params["target"] = target.name
    params["damage"] = damage
    
    try:
        return message.format(**params)
    except KeyError:
        # Fallback in case of missing keys
        return f"{user.name} deals {damage} damage to {target.name}!"

def healing_effect(user, target, params):
    base_healing = params.get("base_value", 0)
    base_healing = apply_stat_scaling(user, base_healing, params)
    healing = apply_variance(base_healing, params, is_damage=False)
    
    actual_healing = target.heal(healing)
    message = format_healing_message(user, target, actual_healing, params)
    
    # Add the healing value to the params for message formatting
    if "message" in params:
        params["healing"] = actual_healing
    
    return {
        "healing": actual_healing,
        "message": message
    }

def format_healing_message(user, target, healing, params):
    message = params.get("message", "")
    if not message:
        return f"{user.name} heals {target.name} for {healing} health!"
    
    # Add values to params for message formatting
    params["user"] = user.name
    params["target"] = target.name
    params["healing"] = healing
    
    try:
        return message.format(**params)
    except KeyError:
        # Fallback in case of missing keys
        return f"{user.name} heals {target.name} for {healing} health!"

def buff_effect(user, target, params):
    buff_type = params.get("buff_type", "defense")
    value = params.get("value", 1)
    duration = params.get("duration", 3)
    
    apply_buff(target, buff_type, value, duration)
    message = format_buff_message(user, target, buff_type, value, duration, params)
    
    return {
        "buff_type": buff_type,
        "value": value,
        "duration": duration,
        "message": message
    }

def apply_buff(target, buff_type, value, duration):
    if not hasattr(target, 'buffs'):
        target.buffs = {}
        
    target.buffs[buff_type] = {
        "value": value,
        "duration": duration
    }

def format_buff_message(user, target, buff_type, value, duration, params):
    message = params.get("message", "")
    if not message:
        return f"{target.name} gains {value} {buff_type} for {duration} turns!"
    return message.format(user=user.name, target=target.name, 
                        value=value, buff_type=buff_type, duration=duration)

def status_effect(user, target, params):
    status_type = params.get("status_type", "poison")
    value = params.get("value", 1)
    duration = params.get("duration", 3)
    chance = params.get("chance", 1.0)
    
    if random.random() > chance:
        return {
            "status_applied": False,
            "message": f"{user.name} failed to apply {status_type} to {target.name}!"
        }
    
    apply_status(target, status_type, value, duration)
    message = format_status_message(user, target, status_type, duration, params)
    
    return {
        "status_type": status_type,
        "value": value,
        "duration": duration,
        "status_applied": True,
        "message": message
    }

def apply_status(target, status_type, value, duration):
    if not hasattr(target, 'status_effects'):
        target.status_effects = {}
        
    target.status_effects[status_type] = {
        "value": value,
        "duration": duration
    }

def format_status_message(user, target, status_type, duration, params):
    message = params.get("message", "")
    if not message:
        return f"{target.name} is afflicted with {status_type} for {duration} turns!"
    return message.format(user=user.name, target=target.name, 
                        status_type=status_type, duration=duration)

def multi_hit_effect(user, target, params):
    base_damage = calculate_base_damage_for_multi_hit(user, params)
    num_hits = determine_number_of_hits(params)
    
    hit_results, total_damage = apply_multi_hits(user, target, base_damage, num_hits, params)
    message = format_multi_hit_message(user, target, num_hits, total_damage, params)
    
    return {
        "hits": num_hits,
        "total_damage": total_damage,
        "hit_results": hit_results,
        "message": message,
        "damage": total_damage  # Add damage key for compatibility
    }

def calculate_base_damage_for_multi_hit(user, params):
    base_damage = params.get("base_value", 0)
    base_damage = apply_weapon_scaling(user, base_damage, params)
    base_damage = apply_stat_scaling(user, base_damage, params)
    return base_damage

def determine_number_of_hits(params):
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

def apply_multi_hits(user, target, base_damage, num_hits, params):
    total_damage = 0
    hit_results = []
    damage_scaling = params.get("damage_scaling", 1.0)
    
    for hit in range(num_hits):
        hit_damage_scaling = damage_scaling ** hit
        damage = calculate_hit_damage(base_damage, hit_damage_scaling, params)
        actual_damage = target.take_damage(damage)
        
        total_damage += actual_damage
        hit_results.append({
            "hit": hit + 1,
            "damage": actual_damage
        })
        
    return hit_results, total_damage

def calculate_hit_damage(base_damage, hit_damage_scaling, params):
    variance_min = params.get("variance_min", 0.8)
    variance_max = params.get("variance_max", 1.2)
    variance = random.uniform(variance_min, variance_max)
    
    return max(1, int(base_damage * hit_damage_scaling * variance))

def format_multi_hit_message(user, target, num_hits, total_damage, params=None):
    if params and "message" in params:
        # Add values to params for message formatting
        params["user"] = user.name
        params["target"] = target.name
        params["hits"] = num_hits
        params["total_damage"] = total_damage
        params["damage"] = total_damage
        return params["message"].format(**params)
    
    if num_hits == 1:
        return f"{user.name} hits {target.name} for {total_damage} damage!"
    return f"{user.name} hits {target.name} {num_hits} times for {total_damage} total damage!"
