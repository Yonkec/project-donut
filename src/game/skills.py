"""
Data-driven skill and enemy system for Project Donut.
Re-exports components from skill_manager, skill_database, enemy_manager, and enemy_database modules.
"""
from typing import Dict, List, Any, Optional
import os
import sys
from pathlib import Path

from .skill_manager import SkillManager, Skill
from .skill_database import SkillDatabase
from .enemy_manager import EnemyManager, Enemy
from .enemy_database import EnemyDatabase

def get_skill_manager() -> SkillManager:
    """Create and return a new SkillManager instance with default effects registered"""
    database = SkillDatabase()
    manager = SkillManager(database)
    manager.register_default_effects()
    manager.load_all_skills()
    return manager

def get_enemy_manager() -> EnemyManager:
    """Create and return a new EnemyManager instance with skill manager configured"""
    skill_manager = get_skill_manager()
    enemy_database = EnemyDatabase()
    enemy_manager = EnemyManager(enemy_database, skill_manager)
    return enemy_manager