import unittest
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from game.player import Player
from game.skill import Skill
from game.skill_manager import SkillManager
from game.skill_database import SkillDatabase
from game.action_manager import ActionManager

class TestPlayerSkills(unittest.TestCase):
    
    def setUp(self):
        self.database = SkillDatabase()
        self.skill_manager = SkillManager(self.database)
        self.skill_manager.register_default_effects()
        self.skill_manager.load_all_skills()
        self.action_manager = ActionManager()
        self.player = Player("Test Player", self.action_manager)
        
    def test_player_initialization(self):
        self.assertEqual(self.player.name, "Test Player")
        self.assertTrue(len(self.player.skills) > 0)
        self.assertTrue(len(self.player.combat_sequence) > 0)
        
    def test_learn_skill(self):
        initial_skill_count = len(self.player.skills)
        fireball = self.skill_manager.get_skill("fireball")
        
        if not fireball:
            fireball_data = {
                "name": "Fireball",
                "description": "A ball of fire that deals damage",
                "effects": [
                    {
                        "type": "damage",
                        "params": {
                            "base_value": 15,
                            "stat_scaling": {"intelligence": 1.5}
                        }
                    }
                ]
            }
            fireball = self.skill_manager.create_skill("fireball", fireball_data)
            
        self.player.learn_skill(fireball)
        self.assertEqual(len(self.player.skills), initial_skill_count + 1)
        self.assertIn(fireball, self.player.skills)
        
    def test_learn_skill_by_id(self):
        initial_skill_count = len(self.player.skills)
        
        ice_spike_data = {
            "name": "Ice Spike",
            "description": "A spike of ice that deals damage and slows",
            "effects": [
                {
                    "type": "damage",
                    "params": {
                        "base_value": 10,
                        "stat_scaling": {"intelligence": 1.2}
                    }
                },
                {
                    "type": "status",
                    "params": {
                        "status_type": "slowed",
                        "value": 0.5,
                        "duration": 2
                    }
                }
            ]
        }
        
        self.skill_manager.create_skill("ice_spike", ice_spike_data)
        self.player.learn_skill_by_id("ice_spike")
        
        self.assertEqual(len(self.player.skills), initial_skill_count + 1)
        self.assertTrue(any(skill.id == "ice_spike" for skill in self.player.skills))
        
    def test_add_to_combat_sequence(self):
        # Create a unique fireball skill for this test
        test_fireball_data = {
            "name": "Test Fireball",
            "description": "A test ball of fire that deals damage",
            "effects": [
                {
                    "type": "damage",
                    "params": {
                        "base_value": 15,
                        "stat_scaling": {"intelligence": 1.5}
                    }
                }
            ]
        }
        test_fireball = self.skill_manager.create_skill("test_fireball", test_fireball_data)
        
        # Learn the skill
        self.player.learn_skill(test_fireball)
        
        # Save the original combat sequence
        original_sequence = self.player.combat_sequence.copy() if self.player.combat_sequence else []
        
        # Add the skill to the combat sequence
        self.player.add_to_combat_sequence(test_fireball, 0)
        
        # Verify the skill was added correctly
        self.assertEqual(self.player.combat_sequence[0].id, "test_fireball")
        
    def test_add_to_combat_sequence_by_id(self):
        # Create a heal skill
        heal_data = {
            "name": "Heal",
            "description": "Heals the target",
            "effects": [
                {
                    "type": "heal",
                    "params": {
                        "base_value": 20,
                        "stat_scaling": {"wisdom": 1.5}
                    }
                }
            ]
        }
        
        # Create and learn the heal skill
        self.skill_manager.create_skill("heal", heal_data)
        self.player.learn_skill_by_id("heal")
        
        # Ensure the player has a combat sequence
        basic_attack = self.skill_manager.get_skill("basic_attack")
        if not self.player.combat_sequence and basic_attack:
            self.player.combat_sequence = [basic_attack] * 3
        elif not self.player.combat_sequence:
            # Create a default combat sequence if none exists
            self.player.combat_sequence = []
            
        # Add the heal skill to the combat sequence
        self.player.add_to_combat_sequence_by_id("heal", 1)
        
        # Verify the skill was added correctly
        self.assertTrue(len(self.player.combat_sequence) > 1)
        self.assertEqual(self.player.combat_sequence[1].id, "heal")
        
    def test_buff_application(self):
        buff_skill_data = {
            "name": "Strengthen",
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
        
        buff_skill = self.skill_manager.create_skill("strengthen", buff_skill_data)
        self.player.learn_skill(buff_skill)
        
        dummy_target = Player("Dummy")
        result = buff_skill.use(self.player, self.player)
        
        self.assertIn("strength", self.player.buffs)
        self.assertEqual(self.player.buffs["strength"]["value"], 5)
        self.assertEqual(self.player.buffs["strength"]["duration"], 3)
        
    def test_status_effect_application(self):
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
        self.player.learn_skill(poison_skill)
        
        dummy_target = Player("Dummy")
        result = poison_skill.use(self.player, dummy_target)
        
        self.assertIn("poison", dummy_target.status_effects)
        self.assertEqual(dummy_target.status_effects["poison"]["value"], 3)
        self.assertEqual(dummy_target.status_effects["poison"]["duration"], 3)
        
    def test_update_status_effects(self):
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
        
        dummy_target = Player("Dummy")
        initial_hp = dummy_target.current_hp
        result = poison_skill.use(self.player, dummy_target)
        
        messages = dummy_target.update_status_effects()
        
        self.assertTrue(len(messages) > 0)
        self.assertLess(dummy_target.current_hp, initial_hp)
        self.assertEqual(dummy_target.status_effects["poison"]["duration"], 2)

if __name__ == "__main__":
    unittest.main()
