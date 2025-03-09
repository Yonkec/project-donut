"""
Data-driven skill system for Project Donut.
Provides factory functions and utilities for creating and managing skills.
"""
from typing import Optional, Dict, Any, List, Callable

from .skill import Skill
from .skill_manager import SkillManager
from .skill_database import SkillDatabase
from .skill_effects import register_default_effects
from .skill_factory import SkillFactory, SkillBuilder, SkillValidator

def create_skill_manager(with_default_skills: bool = True) -> SkillManager:
    database = SkillDatabase()
    manager = SkillManager(database)
    manager.register_default_effects()
    manager.load_all_skills()
    
    if with_default_skills:
        manager.create_default_skills()
        
    return manager

def create_skill(skill_id: str, name: str, description: str, 
               builder_func: Callable[[SkillBuilder], SkillBuilder] = None) -> SkillBuilder:
    builder = SkillBuilder(skill_id, name, description)
    if builder_func:
        builder = builder_func(builder)
    return builder

def get_skills_by_category(skill_manager: SkillManager, category: str) -> List[Skill]:
    return skill_manager.get_skills_by_category(category)

def get_skills_by_tag(skill_manager: SkillManager, tag: str) -> List[Skill]:
    return skill_manager.get_skills_by_tag(tag)

def validate_skill_data(skill_data: Dict[str, Any]) -> List[str]:
    return SkillValidator.validate_skill_data(skill_data)