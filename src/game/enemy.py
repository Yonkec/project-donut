"""
Data-driven enemy system for Project Donut.
Provides factory functions for creating enemy instances.
"""

from .enemy_manager import Enemy, EnemyManager
from .enemy_database import EnemyDatabase
from .skill_manager import SkillManager
from .skill_database import SkillDatabase
from .action_manager import ActionManager

# Create a singleton action manager for the enemies
_action_manager = ActionManager()

# Create a skill manager for enemies
_skill_database = SkillDatabase()
_skill_manager = SkillManager(_skill_database)
_skill_manager.register_default_effects()
_skill_manager.load_all_skills()

# Create a singleton enemy manager
_enemy_database = EnemyDatabase()
_enemy_manager = EnemyManager(_enemy_database, _skill_manager, _action_manager)
_enemy_manager.load_all_enemies()

# Factory functions that return Enemy instances
def create_goblin(level: int = 1) -> Enemy:
    enemy = _enemy_manager.get_enemy("goblin", level)
    if enemy is None:
        return None
        
    if not hasattr(enemy, 'skills') or enemy.skills is None:
        enemy.skills = []
        
    if "quick_strike" not in [skill.id for skill in enemy.skills]:
        quick_strike = _skill_manager.get_skill("quick_strike")
        if quick_strike:
            enemy.skills.append(quick_strike)
    return enemy

def create_orc(level: int = 1) -> Enemy:
    enemy = _enemy_manager.get_enemy("orc", level)
    if enemy is None:
        return None
        
    if not hasattr(enemy, 'skills') or enemy.skills is None:
        enemy.skills = []
        
    if "power_attack" not in [skill.id for skill in enemy.skills]:
        power_attack = _skill_manager.get_skill("power_attack")
        if power_attack:
            enemy.skills.append(power_attack)
    return enemy

def create_skeleton(level: int = 1) -> Enemy:
    enemy = _enemy_manager.get_enemy("skeleton", level)
    if enemy is None:
        return None
        
    if not hasattr(enemy, 'skills') or enemy.skills is None:
        enemy.skills = []
        
    if "poison_dart" not in [skill.id for skill in enemy.skills]:
        poison_dart = _skill_manager.get_skill("poison_dart")
        if poison_dart:
            enemy.skills.append(poison_dart)
    return enemy

def create_random_enemy(level: int = 1, player_level: int = 1) -> Enemy:
    return _enemy_manager.create_random_enemy(level, player_level)