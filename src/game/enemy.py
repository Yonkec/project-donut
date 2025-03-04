"""
Data-driven enemy system for Project Donut.
Re-exports components from enemy_manager and enemy_database modules.
"""

from .enemy_manager import Enemy, EnemyManager
from .enemy_database import EnemyDatabase
from .skills import get_enemy_manager

# Create a singleton enemy manager for backwards compatibility
_enemy_manager = get_enemy_manager()

# Re-export create functions that return Enemy instances from the data-driven system
def create_goblin(level: int = 1) -> Enemy:
    return _enemy_manager.get_enemy("goblin", level)

def create_orc(level: int = 1) -> Enemy:
    return _enemy_manager.get_enemy("orc", level)

def create_skeleton(level: int = 1) -> Enemy:
    return _enemy_manager.get_enemy("skeleton", level)

def create_random_enemy(level: int = 1) -> Enemy:
    return _enemy_manager.create_random_enemy(level)