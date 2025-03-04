"""
Data-driven skill system for Project Donut.
Re-exports components from skill_manager and skill_database modules.
"""
from typing import Dict, List, Any, Optional
import os
import sys
from pathlib import Path

from .skill_manager import SkillManager, Skill
from .skill_database import SkillDatabase

def get_skill_manager() -> SkillManager:
    """Create and return a new SkillManager instance with default effects registered"""
    database = SkillDatabase()
    manager = SkillManager(database)
    manager.register_default_effects()
    manager.load_all_skills()
    return manager