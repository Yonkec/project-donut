import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class SkillDatabase:
    """
    Handles loading and saving skill data from JSON files.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.skills_dir = self.data_dir / "skills"
        self.templates = {}
        self.skills = {}
        self.effects = {}
        
        # Create directories if they don't exist
        os.makedirs(self.skills_dir, exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self) -> None:
        """Load all skill data from JSON files"""
        # Load templates
        template_path = self.skills_dir / "templates.json"
        if template_path.exists():
            with open(template_path, 'r') as f:
                self.templates = json.load(f)
        
        # Load skills
        skills_path = self.skills_dir / "skills.json"
        if skills_path.exists():
            with open(skills_path, 'r') as f:
                self.skills = json.load(f)
        
        # Load effects
        effects_path = self.skills_dir / "effects.json"
        if effects_path.exists():
            with open(effects_path, 'r') as f:
                self.effects = json.load(f)
    
    def save_data(self) -> None:
        """Save all skill data to JSON files"""
        # Save templates
        with open(self.skills_dir / "templates.json", 'w') as f:
            json.dump(self.templates, f, indent=2)
        
        # Save skills
        with open(self.skills_dir / "skills.json", 'w') as f:
            json.dump(self.skills, f, indent=2)
        
        # Save effects
        with open(self.skills_dir / "effects.json", 'w') as f:
            json.dump(self.effects, f, indent=2)
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get a skill definition by ID"""
        return self.skills.get(skill_id)
    
    def get_effect(self, effect_id: str) -> Optional[Dict[str, Any]]:
        """Get an effect definition by ID"""
        return self.effects.get(effect_id)
    
    def add_template(self, template_id: str, template_data: Dict[str, Any]) -> None:
        """Add or update a template"""
        self.templates[template_id] = template_data
        self.save_data()
    
    def add_skill(self, skill_id: str, skill_data: Dict[str, Any]) -> None:
        """Add or update a skill"""
        self.skills[skill_id] = skill_data
        self.save_data()
    
    def add_effect(self, effect_id: str, effect_data: Dict[str, Any]) -> None:
        """Add or update an effect"""
        self.effects[effect_id] = effect_data
        self.save_data()
    
    def get_all_skills(self) -> Dict[str, Any]:
        """Get all skills"""
        return self.skills
    
    def get_all_templates(self) -> Dict[str, Any]:
        """Get all templates"""
        return self.templates
    
    def get_all_effects(self) -> Dict[str, Any]:
        """Get all effects"""
        return self.effects
