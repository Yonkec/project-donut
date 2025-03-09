from typing import Dict, List, Optional, Any
from .skill import Skill
from .skill_manager import SkillManager
from .skill_database import SkillDatabase
from .action_manager import ActionManager

class PlayerSkills:
    def __init__(self, player):
        self.player = player
        self.skills: List[Skill] = []
        self.combat_sequence: List[Skill] = []
        self.buffs = {}
        self.status_effects = {}
        
        self.skill_database = SkillDatabase()
        self.skill_manager = SkillManager(self.skill_database)
        self.skill_manager.register_default_effects()
        self.skill_manager.load_all_skills()
        
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        basic_attack = self.skill_manager.get_skill("basic_attack")
        if not basic_attack:
            basic_attack_data = {
                "name": "Basic Attack",
                "description": "A simple attack with your weapon",
                "effects": [
                    {
                        "type": "damage",
                        "params": {
                            "base_value": 5,
                            "stat_scaling": {"strength": 1.0}
                        }
                    }
                ]
            }
            basic_attack = self.skill_manager.create_skill("basic_attack", basic_attack_data)
        
        defend = self.skill_manager.get_skill("defend")
        if not defend:
            defend_data = {
                "name": "Defend",
                "description": "Take a defensive stance",
                "effects": [
                    {
                        "type": "buff",
                        "params": {
                            "buff_type": "defense",
                            "value": 5,
                            "duration": 2
                        }
                    }
                ]
            }
            defend = self.skill_manager.create_skill("defend", defend_data)
        
        heal = self.skill_manager.get_skill("heal")
        if not heal:
            heal_data = {
                "name": "Heal",
                "description": "Recover some health",
                "effects": [
                    {
                        "type": "heal",
                        "params": {
                            "base_value": 10,
                            "stat_scaling": {"wisdom": 1.0}
                        }
                    }
                ]
            }
            heal = self.skill_manager.create_skill("heal", heal_data)
        
        self.learn_skill(basic_attack)
        self.combat_sequence = [basic_attack] * 3
        self.learn_skill(defend)
        self.learn_skill(heal)
    
    def learn_skill(self, skill: Skill) -> bool:
        for existing_skill in self.skills:
            if existing_skill.id == skill.id:
                return False
                
        self.skills.append(skill)
        return True
        
    def learn_skill_by_id(self, skill_id: str) -> bool:
        for existing_skill in self.skills:
            if existing_skill.id == skill_id:
                return False
                
        skill = self.skill_manager.get_skill(skill_id)
        if skill:
            return self.learn_skill(skill)
        return False
        
    def add_to_combat_sequence(self, skill: Skill, position: int) -> bool:
        if skill in self.skills and 0 <= position < 5:  # Limit to 5 skills in sequence
            if len(self.combat_sequence) <= position:
                self.combat_sequence.extend([None] * (position - len(self.combat_sequence) + 1))
            self.combat_sequence[position] = skill
            return True
        return False
        
    def add_to_combat_sequence_by_id(self, skill_id: str, position: int) -> bool:
        for skill in self.skills:
            if skill.id == skill_id:
                return self.add_to_combat_sequence(skill, position)
        return False
    
    def update_status_effects(self) -> List[str]:
        messages = []
        
        buffs_to_remove = []
        for buff_type, buff_data in self.buffs.items():
            buff_data['duration'] -= 1
            if buff_data['duration'] <= 0:
                buffs_to_remove.append(buff_type)
                messages.append(f"{self.player.name}'s {buff_type} buff has expired.")
        
        for buff_type in buffs_to_remove:
            del self.buffs[buff_type]
        
        statuses_to_remove = []
        for status_type, status_data in self.status_effects.items():
            if status_type == 'poison':
                damage = status_data['value']
                self.player.current_hp = max(0, self.player.current_hp - damage)
                messages.append(f"{self.player.name} takes {damage} poison damage.")
            elif status_type == 'regeneration':
                healing = status_data['value']
                self.player.current_hp = min(self.player.max_hp, self.player.current_hp + healing)
                messages.append(f"{self.player.name} regenerates {healing} health.")
            elif status_type == 'stunned':
                messages.append(f"{self.player.name} is stunned and cannot act.")
                if self.player.action_manager:
                    self.player.action_manager.add_action_modifier(self.player.id, "stunned", -1.0, 1)
            elif status_type == 'slowed':
                slow_value = status_data.get('value', 0.5)
                messages.append(f"{self.player.name} is slowed and gains action more slowly.")
                if self.player.action_manager:
                    self.player.action_manager.add_action_modifier(self.player.id, "slowed", -slow_value, 1)
            
            status_data['duration'] -= 1
            if status_data['duration'] <= 0:
                statuses_to_remove.append(status_type)
                messages.append(f"{self.player.name} is no longer affected by {status_type}.")
        
        for status_type in statuses_to_remove:
            del self.status_effects[status_type]
        
        if self.player.action_manager:
            expired_modifiers = self.player.action_manager.update_action_modifiers(self.player.id)
            for modifier in expired_modifiers:
                messages.append(f"{self.player.name}'s {modifier} effect has expired.")
                
        return messages
