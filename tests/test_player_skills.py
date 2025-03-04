#!/usr/bin/env python3
"""
Test script for the updated player skill system.
"""
import os
import sys
import random

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.game.player import Player
from src.game.skill_manager import SkillManager
from src.game.skill_database import SkillDatabase

class Enemy:
    """Simple enemy class for testing skills"""
    def __init__(self, name, hp=50):
        self.name = name
        self.max_hp = hp
        self.current_hp = hp
        self.buffs = {}
        self.status_effects = {}
        
    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)
        return amount
        
    def heal(self, amount):
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
        
    def get_stats(self):
        return {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10
        }
        
    def update_status_effects(self):
        messages = []
        
        # Update buffs
        if hasattr(self, 'buffs'):
            buffs_to_remove = []
            for buff_type, buff_data in self.buffs.items():
                buff_data['duration'] -= 1
                if buff_data['duration'] <= 0:
                    buffs_to_remove.append(buff_type)
                    messages.append(f"{self.name}'s {buff_type} buff has expired.")
            
            for buff_type in buffs_to_remove:
                del self.buffs[buff_type]
        
        # Update status effects
        if hasattr(self, 'status_effects'):
            statuses_to_remove = []
            for status_type, status_data in self.status_effects.items():
                if status_type == 'poison':
                    damage = status_data['value']
                    self.current_hp = max(0, self.current_hp - damage)
                    messages.append(f"{self.name} takes {damage} poison damage.")
                
                status_data['duration'] -= 1
                if status_data['duration'] <= 0:
                    statuses_to_remove.append(status_type)
                    messages.append(f"{self.name} is no longer affected by {status_type}.")
            
            for status_type in statuses_to_remove:
                del self.status_effects[status_type]
                
        return messages

def test_player_skills():
    """Test the player's skill system"""
    print("\n=== Testing Player Skill System ===\n")
    
    # Create a player
    player = Player("Hero")
    
    # Create an enemy
    enemy = Enemy("Goblin")
    
    print(f"Player: {player.name} (HP: {player.current_hp}/{player.max_hp})")
    print(f"Enemy: {enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp})")
    print("\n=== Basic Skills ===\n")
    
    # Test basic attack
    basic_attack = player.skill_manager.get_skill("basic_attack")
    if basic_attack:
        print(f"Using {basic_attack.name}...")
        result = basic_attack.use(player, enemy)
        print(result["message"])
        print(f"Enemy HP: {enemy.current_hp}/{enemy.max_hp}")
    
    # Test defend
    defend = player.skill_manager.get_skill("defend")
    if defend:
        print(f"\nUsing {defend.name}...")
        result = defend.use(player, player)
        print(result["message"])
        
        # Show buff status
        if hasattr(player, 'buffs') and 'defense' in player.buffs:
            print(f"Defense buff: +{player.buffs['defense']['value']} for {player.buffs['defense']['duration']} turns")
    
    print("\n=== Learning New Skills ===\n")
    
    # Learn a new skill by ID
    new_skills = ["power_attack", "healing", "fireball", "poison_dart"]
    for skill_id in new_skills:
        if player.learn_skill_by_id(skill_id):
            skill = player.skill_manager.get_skill(skill_id)
            print(f"Learned new skill: {skill.name} - {skill.description}")
    
    print("\n=== Testing Advanced Skills ===\n")
    
    # Test power attack
    power_attack = player.skill_manager.get_skill("power_attack")
    if power_attack:
        print(f"Using {power_attack.name}...")
        result = power_attack.use(player, enemy)
        print(result["message"])
        print(f"Enemy HP: {enemy.current_hp}/{enemy.max_hp}")
    
    # Test healing
    healing = player.skill_manager.get_skill("healing")
    if healing and player.current_hp < player.max_hp:
        # Damage player first
        player.current_hp = player.max_hp // 2
        print(f"\nPlayer damaged! HP: {player.current_hp}/{player.max_hp}")
        
        print(f"Using {healing.name}...")
        result = healing.use(player, player)
        print(result["message"])
        print(f"Player HP: {player.current_hp}/{player.max_hp}")
    
    # Test poison dart
    poison_dart = player.skill_manager.get_skill("poison_dart")
    if poison_dart:
        print(f"\nUsing {poison_dart.name}...")
        result = poison_dart.use(player, enemy)
        print(result["message"])
        
        # Check if poison was applied
        if hasattr(enemy, 'status_effects') and 'poison' in enemy.status_effects:
            poison = enemy.status_effects['poison']
            print(f"Poison applied: {poison['value']} damage for {poison['duration']} turns")
        
        # Simulate a few turns to see poison effect
        print("\n=== Simulating Turns ===\n")
        for turn in range(1, 4):
            print(f"Turn {turn}:")
            
            messages = enemy.update_status_effects()
            for msg in messages:
                print(msg)
            
            print(f"Enemy HP: {enemy.current_hp}/{enemy.max_hp}")
            
            messages = player.update_status_effects()
            for msg in messages:
                print(msg)
    
    print("\n=== Combat Sequence ===\n")
    
    # Set up a combat sequence
    player.combat_sequence = []
    for i, skill_id in enumerate(["basic_attack", "power_attack", "poison_dart"]):
        player.add_to_combat_sequence_by_id(skill_id, i)
    
    print("Combat sequence:")
    for i, skill in enumerate(player.combat_sequence):
        print(f"{i+1}. {skill.name}")
    
    print("\n=== Test Complete ===\n")

if __name__ == "__main__":
    test_player_skills()
