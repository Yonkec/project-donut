import unittest
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from game.enemy import Enemy, create_goblin, create_orc, create_skeleton
from game.skill import Skill
from game.skill_manager import SkillManager
from game.skill_database import SkillDatabase
from game.player import Player
from game.action_manager import ActionManager

class TestEnemySkills(unittest.TestCase):
    
    def setUp(self):
        self.database = SkillDatabase()
        self.skill_manager = SkillManager(self.database)
        self.skill_manager.register_default_effects()
        self.skill_manager.load_all_skills()
        self.action_manager = ActionManager()
        self.player = Player("Test Player", self.action_manager)
        
        # Create test skills if they don't exist
        self._create_test_skills()
        
    def _create_test_skills(self):
        # Create quick strike skill if it doesn't exist
        quick_strike = self.skill_manager.get_skill("quick_strike")
        if not quick_strike:
            quick_strike_data = {
                "name": "Quick Strike",
                "description": "A fast attack that deals damage",
                "effects": [
                    {
                        "type": "damage",
                        "params": {
                            "base_value": 5,
                            "stat_scaling": {"dexterity": 1.0}
                        }
                    }
                ]
            }
            self.skill_manager.create_skill("quick_strike", quick_strike_data)
            
        # Create power attack skill if it doesn't exist
        power_attack = self.skill_manager.get_skill("power_attack")
        if not power_attack:
            power_attack_data = {
                "name": "Power Attack",
                "description": "A powerful attack that deals heavy damage",
                "effects": [
                    {
                        "type": "damage",
                        "params": {
                            "base_value": 10,
                            "stat_scaling": {"strength": 1.5}
                        }
                    }
                ]
            }
            self.skill_manager.create_skill("power_attack", power_attack_data)
            
        # Create poison dart skill if it doesn't exist
        poison_dart = self.skill_manager.get_skill("poison_dart")
        if not poison_dart:
            poison_dart_data = {
                "name": "Poison Dart",
                "description": "A poisoned dart that deals damage over time",
                "effects": [
                    {
                        "type": "damage",
                        "params": {
                            "base_value": 3,
                            "stat_scaling": {"dexterity": 0.5}
                        }
                    },
                    {
                        "type": "status_effect",
                        "params": {
                            "effect_type": "poison",
                            "value": 2,
                            "duration": 3
                        }
                    }
                ]
            }
            self.skill_manager.create_skill("poison_dart", poison_dart_data)
    
    def test_goblin_creation(self):
        from game.enemy_manager import Enemy
        goblin_data = {
            "name": "Goblin",
            "level": 2,
            "skills": ["basic_attack", "quick_strike"]
        }
        goblin = Enemy("goblin", goblin_data, self.skill_manager, self.action_manager)
            
        self.assertEqual(goblin.name, "Goblin")
        self.assertEqual(goblin.level, 2)
        self.assertTrue(len(goblin.skills) > 0)
        self.assertTrue(any(skill.id == "quick_strike" for skill in goblin.skills))
        
    def test_orc_creation(self):
        from game.enemy_manager import Enemy
        orc_data = {
            "name": "Orc",
            "level": 3,
            "skills": ["basic_attack", "power_attack"]
        }
        orc = Enemy("orc", orc_data, self.skill_manager, self.action_manager)
            
        self.assertEqual(orc.name, "Orc")
        self.assertEqual(orc.level, 3)
        self.assertTrue(len(orc.skills) > 0)
        self.assertTrue(any(skill.id == "power_attack" for skill in orc.skills))
        
    def test_skeleton_creation(self):
        from game.enemy_manager import Enemy
        skeleton_data = {
            "name": "Skeleton",
            "level": 2,
            "skills": ["basic_attack", "poison_dart"]
        }
        skeleton = Enemy("skeleton", skeleton_data, self.skill_manager, self.action_manager)
            
        self.assertEqual(skeleton.name, "Skeleton")
        self.assertEqual(skeleton.level, 2)
        self.assertTrue(len(skeleton.skills) > 0)
        self.assertTrue(any(skill.id == "poison_dart" for skill in skeleton.skills))
        
    def test_enemy_damage_skill(self):
        from game.enemy_manager import Enemy
        goblin_data = {
            "name": "Goblin",
            "level": 1,
            "skills": ["basic_attack", "quick_strike"]
        }
        goblin = Enemy("goblin", goblin_data, self.skill_manager, self.action_manager)
        
        # Get the quick strike skill for testing
        quick_strike = next((skill for skill in goblin.skills if skill.id == "quick_strike"), None)
        self.assertIsNotNone(quick_strike, "Quick strike skill not found in goblin skills")
            
        initial_hp = self.player.current_hp
        result = quick_strike.use(goblin, self.player)
        
        self.assertLess(self.player.current_hp, initial_hp)
        self.assertIn("damage", result)
        
    def test_enemy_buff_application(self):
        from game.enemy_manager import Enemy
        orc_data = {
            "name": "Orc",
            "level": 1,
            "skills": ["basic_attack"]
        }
        orc = Enemy("orc", orc_data, self.skill_manager, self.action_manager)
        
        buff_skill_data = {
            "name": "Rage",
            "description": "Increases strength",
            "effects": [
                {
                    "type": "buff",
                    "params": {
                        "buff_type": "strength",
                        "value": 5,
                        "duration": 3
                    }
                }
            ]
        }
        
        rage_skill = self.skill_manager.create_skill("rage", buff_skill_data)
        orc.skills.append(rage_skill)
        
        result = rage_skill.use(orc, orc)
        
        self.assertIn("strength", orc.buffs)
        self.assertEqual(orc.buffs["strength"]["value"], 5)
        self.assertEqual(orc.buffs["strength"]["duration"], 3)
        
    def test_enemy_status_effect_application(self):
        from game.enemy_manager import Enemy
        skeleton_data = {
            "name": "Skeleton",
            "level": 1,
            "skills": ["basic_attack", "poison_dart"]
        }
        skeleton = Enemy("skeleton", skeleton_data, self.skill_manager, self.action_manager)
        
        # Create a poison dart skill with status effect
        poison_dart_data = {
            "name": "Poison Dart",
            "description": "Fires a poisoned dart",
            "effects": [
                {
                    "type": "damage",
                    "params": {
                        "base_value": 3
                    }
                },
                {
                    "type": "status_effect",
                    "params": {
                        "effect_type": "poison",
                        "value": 2,
                        "duration": 3
                    }
                }
            ]
        }
        self.skill_manager.create_skill("poison_dart", poison_dart_data)
        
        # Initialize player status effects if needed
        if not hasattr(self.player, 'status_effects'):
            self.player.status_effects = {}
        
        # Get the poison dart skill from the skeleton
        poison_dart = next((skill for skill in skeleton.skills if skill.id == "poison_dart"), None)
        self.assertIsNotNone(poison_dart, "Poison dart skill not found in skeleton skills")
            
        # Use the skill
        result = poison_dart.use(skeleton, self.player)
        
        # Check if the status effect was applied
        self.assertIn("poison", self.player.status_effects)
        self.assertEqual(self.player.status_effects["poison"]["value"], 3)
        self.assertEqual(self.player.status_effects["poison"]["duration"], 3)
        
    def test_enemy_choose_action(self):
        from game.enemy_manager import Enemy
        goblin_data = {
            "name": "Goblin",
            "level": 1,
            "skills": ["basic_attack", "quick_strike"],
            "behavior": "random"
        }
        goblin = Enemy("goblin", goblin_data, self.skill_manager, self.action_manager)
        
        # Generate action points so the enemy can choose an action
        if self.action_manager:
            self.action_manager.register_entity(goblin.id)
            self.action_manager.generate_action(goblin.id, 10.0)
            
        action = goblin.choose_action(self.player)
        
        self.assertIsNotNone(action)
        self.assertIsInstance(action, Skill)
        
    def test_enemy_update_status_effects(self):
        from game.enemy_manager import Enemy
        orc_data = {
            "name": "Orc",
            "level": 1,
            "skills": ["basic_attack"]
        }
        orc = Enemy("orc", orc_data, self.skill_manager, self.action_manager)
        
        poison_skill_data = {
            "name": "Poison",
            "description": "Poisons the target",
            "effects": [
                {
                    "type": "status",
                    "params": {
                        "status_type": "poison",
                        "value": 3,
                        "duration": 3
                    }
                }
            ]
        }
        
        poison_skill = self.skill_manager.create_skill("poison", poison_skill_data)
        
        initial_hp = orc.current_hp
        result = poison_skill.use(self.player, orc)
        
        messages = orc.update_status_effects()
        
        self.assertTrue(len(messages) > 0)
        self.assertLess(orc.current_hp, initial_hp)
        self.assertEqual(orc.status_effects["poison"]["duration"], 2)
        
    def test_enemy_multi_hit_skill(self):
        from game.enemy_manager import Enemy
        skeleton_data = {
            "name": "Skeleton",
            "level": 1,
            "skills": ["basic_attack"]
        }
        skeleton = Enemy("skeleton", skeleton_data, self.skill_manager, self.action_manager)
        
        multi_hit_data = {
            "name": "Bone Barrage",
            "description": "Throws multiple bone shards",
            "effects": [
                {
                    "type": "multi_hit",
                    "params": {
                        "base_value": 3,
                        "min_hits": 2,
                        "max_hits": 4,
                        "hit_chance": 0.8
                    }
                }
            ]
        }
        
        bone_barrage = self.skill_manager.create_skill("bone_barrage", multi_hit_data)
        skeleton.skills.append(bone_barrage)
        
        initial_hp = self.player.current_hp
        result = bone_barrage.use(skeleton, self.player)
        
        self.assertLess(self.player.current_hp, initial_hp)
        self.assertIn("hits", result)
        self.assertIn("total_damage", result)
        self.assertIn("hit_results", result)

if __name__ == "__main__":
    unittest.main()
