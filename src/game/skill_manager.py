from typing import Dict, Any, Callable, Optional, List
from .skill_database import SkillDatabase
from .skill import Skill
from .skill_effects import register_default_effects

class SkillManager:
    def __init__(self, database: Optional[SkillDatabase] = None):
        self.database = database or SkillDatabase()
        self.effect_functions = {}
        self.skills = {}
        self.skill_categories = set()
        self.skill_tags = set()
        
    def register_effect(self, effect_type: str, effect_function: Callable) -> None:
        self.effect_functions[effect_type] = effect_function
        
    def create_skill(self, skill_id: str, skill_data: Dict[str, Any]) -> Skill:
        from .skill_factory import SkillValidator
        
        errors = SkillValidator.validate_skill_data(skill_data)
        if errors:
            error_message = "\n".join(errors)
            raise ValueError(f"Invalid skill data for {skill_id}: {error_message}")
            
        skill = Skill(skill_id, skill_data, self.effect_functions)
        self.skills[skill_id] = skill
        
        if "category" in skill_data:
            self.skill_categories.add(skill_data["category"])
            
        if "tags" in skill_data:
            for tag in skill_data["tags"]:
                self.skill_tags.add(tag)
                
        return skill
        
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)
        
    def get_skills_by_category(self, category: str) -> List[Skill]:
        return [skill for skill in self.skills.values() 
                if "category" in skill.__dict__ and skill.__dict__["category"] == category]
                
    def get_skills_by_tag(self, tag: str) -> List[Skill]:
        return [skill for skill in self.skills.values() 
                if "tags" in skill.__dict__ and tag in skill.__dict__["tags"]]
        
    def load_all_skills(self) -> None:
        for skill_id, skill_data in self.database.get_all_skills().items():
            try:
                self.create_skill(skill_id, skill_data)
            except ValueError as e:
                print(f"Error loading skill {skill_id}: {e}")
                
    def register_default_effects(self) -> None:
        register_default_effects(self)
        
    def create_default_skills(self) -> None:
        pass  # All skills are now loaded from the skills.json file
