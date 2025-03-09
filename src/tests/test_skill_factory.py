import unittest
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from game.skill import Skill
from game.skill_manager import SkillManager
from game.skill_database import SkillDatabase
from game.skill_factory import SkillBuilder, SkillFactory, SkillValidator
from game.player import Player
from game.enemy import create_goblin, Enemy
from game.action_manager import ActionManager

class TestSkillFactory(unittest.TestCase):
    
    def setUp(self):
        self.action_manager = ActionManager()
        self.database = SkillDatabase()
        self.skill_manager = SkillManager(self.database)
        self.skill_manager.register_default_effects()
        self.player = Player("Test Player", self.action_manager)
        
    def test_skill_builder(self):
        builder = SkillBuilder("test_skill", "Test Skill", "A test skill")
        builder.with_energy_cost(10)
        builder.with_action_cost(4.0)
        builder.with_cooldown(2)
        builder.with_sound("attack")
        builder.with_category("test")
        builder.with_tags(["test", "debug"])
        builder.add_damage_effect(15, stat_scaling={"strength": 1.2})
        
        skill_data = builder.get_data()
        
        self.assertEqual(skill_data["name"], "Test Skill")
        self.assertEqual(skill_data["description"], "A test skill")
        self.assertEqual(skill_data["energy_cost"], 10)
        self.assertEqual(skill_data["action_cost"], 4.0)
        self.assertEqual(skill_data["cooldown"], 2)
        self.assertEqual(skill_data["sound"], "attack")
        self.assertEqual(skill_data["category"], "test")
        self.assertEqual(skill_data["tags"], ["test", "debug"])
        self.assertEqual(len(skill_data["effects"]), 1)
        self.assertEqual(skill_data["effects"][0]["type"], "damage")
        self.assertEqual(skill_data["effects"][0]["params"]["base_value"], 15)
        
    def test_skill_builder_chaining(self):
        skill = (SkillBuilder("chain_skill", "Chain Skill", "A skill created with method chaining")
                .with_energy_cost(5)
                .with_cooldown(1)
                .add_damage_effect(10)
                .add_status_effect("poison", 2, 3)
                .build(self.skill_manager))
        
        self.assertEqual(skill.name, "Chain Skill")
        self.assertEqual(skill.energy_cost, 5)
        self.assertEqual(skill.cooldown, 1)
        self.assertEqual(len(skill.effects), 2)
        
    def test_skill_factory_basic_attack(self):
        basic_attack = SkillFactory.create_basic_attack(self.skill_manager)
        
        self.assertEqual(basic_attack.id, "basic_attack")
        self.assertEqual(basic_attack.category, "physical")
        self.assertIn("attack", basic_attack.tags)
        self.assertIn("physical", basic_attack.tags)
        
        dummy_target = Player("Dummy", self.action_manager)
        
        basic_attack.action_cost = 0  # Remove action cost for testing
        result = basic_attack.use(self.player, dummy_target)
        
        self.assertIn("damage", result)
        self.assertGreater(result["damage"], 0)
        
    def test_skill_factory_fireball(self):
        fireball = SkillFactory.create_fireball(self.skill_manager)
        
        self.assertEqual(fireball.id, "fireball")
        self.assertEqual(fireball.category, "magic")
        self.assertIn("magic", fireball.tags)
        self.assertIn("fire", fireball.tags)
        
        self.player.base_stats["intelligence"] = 15
        dummy_target = Player("Dummy", self.action_manager)
        
        fireball.action_cost = 0  # Remove action cost for testing
        fireball.energy_cost = 0  # Remove energy cost for testing
        result = fireball.use(self.player, dummy_target)
        
        self.assertIn("damage", result)
        self.assertGreater(result["damage"], 0)
        
    def test_skill_factory_custom_skill(self):
        def builder_func(builder):
            return (builder
                   .with_energy_cost(8)
                   .with_cooldown(2)
                   .with_category("custom")
                   .add_tag("special")
                   .add_multi_hit_effect(5, min_hits=2, max_hits=4))
        
        custom_skill = SkillFactory.create_custom_skill(
            self.skill_manager,
            "custom_skill",
            "Custom Skill",
            "A custom skill created with a builder function",
            builder_func
        )
        
        self.assertEqual(custom_skill.id, "custom_skill")
        self.assertEqual(custom_skill.category, "custom")
        self.assertIn("special", custom_skill.tags)
        
        dummy_target = Player("Dummy", self.action_manager)
        
        custom_skill.action_cost = 0  # Remove action cost for testing
        custom_skill.energy_cost = 0  # Remove energy cost for testing
        result = custom_skill.use(self.player, dummy_target)
        
        self.assertIn("hits", result)
        self.assertIn("total_damage", result)
        
    def test_skill_validator(self):
        valid_data = {
            "name": "Valid Skill",
            "description": "A valid skill",
            "effects": [
                {
                    "type": "damage",
                    "params": {
                        "base_value": 10
                    }
                }
            ]
        }
        
        invalid_data = {
            "description": "Missing name",
            "effects": [
                {
                    "type": "damage"
                }
            ]
        }
        
        empty_effects_data = {
            "name": "No Effects",
            "description": "A skill with no effects",
            "effects": []
        }
        
        self.assertEqual(len(SkillValidator.validate_skill_data(valid_data)), 0)
        self.assertGreater(len(SkillValidator.validate_skill_data(invalid_data)), 0)
        self.assertGreater(len(SkillValidator.validate_skill_data(empty_effects_data)), 0)
        
    def test_skill_categories(self):
        SkillFactory.create_basic_attack(self.skill_manager)
        SkillFactory.create_fireball(self.skill_manager)
        SkillFactory.create_heal(self.skill_manager)
        
        physical_skills = self.skill_manager.get_skills_by_category("physical")
        magic_skills = self.skill_manager.get_skills_by_category("magic")
        
        self.assertGreater(len(physical_skills), 0)
        self.assertGreater(len(magic_skills), 0)
        self.assertTrue(all(skill.category == "physical" for skill in physical_skills))
        self.assertTrue(all(skill.category == "magic" for skill in magic_skills))
        
    def test_skill_tags(self):
        SkillFactory.create_basic_attack(self.skill_manager)
        SkillFactory.create_fireball(self.skill_manager)
        SkillFactory.create_heal(self.skill_manager)
        
        attack_skills = self.skill_manager.get_skills_by_tag("attack")
        magic_skills = self.skill_manager.get_skills_by_tag("magic")
        healing_skills = self.skill_manager.get_skills_by_tag("healing")
        
        self.assertGreater(len(attack_skills), 0)
        self.assertGreater(len(magic_skills), 0)
        self.assertGreater(len(healing_skills), 0)
        self.assertTrue(all("attack" in skill.tags for skill in attack_skills))
        self.assertTrue(all("magic" in skill.tags for skill in magic_skills))
        self.assertTrue(all("healing" in skill.tags for skill in healing_skills))
        
    def test_message_formatting(self):
        heal_skill = SkillFactory.create_heal(self.skill_manager)
        
        self.player.base_stats["wisdom"] = 15
        dummy_target = Player("Dummy", self.action_manager)
        initial_hp = dummy_target.current_hp
        dummy_target.current_hp -= 30
        
        heal_skill.action_cost = 0  # Remove action cost for testing
        heal_skill.energy_cost = 0  # Remove energy cost for testing
        result = heal_skill.use(self.player, dummy_target)
        
        self.assertIn("message", result)
        self.assertIn(self.player.name, result["message"])
        self.assertIn(dummy_target.name, result["message"])
        self.assertIn(str(result["healing"]), result["message"])
        
    def test_enemy_skill_integration(self):
        from game.enemy_database import EnemyDatabase
        from game.enemy_manager import EnemyManager
        
        enemy_database = EnemyDatabase()
        enemy_manager = EnemyManager(enemy_database, self.skill_manager, self.action_manager)
        enemy_manager.load_all_enemies()
        
        enemy_data = {
            "name": "Test Goblin",
            "level": 1,
            "stats": {
                "strength": 6,
                "dexterity": 8,
                "intelligence": 4,
                "vitality": 5
            },
            "max_hp": 25,
            "max_energy": 12,
            "skills": ["basic_attack"]
        }
        
        goblin = Enemy("goblin", enemy_data, self.skill_manager, self.action_manager)
        
        quick_strike = SkillFactory.create_quick_strike(self.skill_manager)
        goblin.skills.append(quick_strike)
        
        self.assertIsNotNone(quick_strike)
        self.assertEqual(quick_strike.category, "physical")
        self.assertIn("multi", quick_strike.tags)
        
        dummy_target = Player("Dummy", self.action_manager)
        
        quick_strike.action_cost = 0  # Remove action cost for testing
        result = quick_strike.use(goblin, dummy_target)
        
        self.assertIn("hits", result)
        self.assertIn("total_damage", result)

if __name__ == "__main__":
    unittest.main()
