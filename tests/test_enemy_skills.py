#!/usr/bin/env python3
"""
Test script for the updated enemy skill system.
"""
import os
import sys
import random

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.game.player import Player
from src.game.enemy import Enemy, create_goblin, create_orc, create_skeleton

def test_enemy_skills():
    print("\n=== Testing Enemy Skill System ===\n")
    
    player = Player("Hero")
    
    enemy_types = [
        ("Goblin", create_goblin(2)),
        ("Orc", create_orc(2)),
        ("Skeleton", create_skeleton(2))
    ]
    
    for enemy_name, enemy in enemy_types:
        print(f"\n=== Testing {enemy_name} Skills ===\n")
        print(f"Enemy: {enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp})")
        print(f"Skills: {', '.join(skill.name for skill in enemy.skills)}")
        
        for skill in enemy.skills:
            print(f"\nUsing {skill.name}...")
            result = skill.use(enemy, player)
            print(result["message"])
            
            if hasattr(player, 'status_effects') and player.status_effects:
                for status, data in player.status_effects.items():
                    print(f"Status effect applied: {status} ({data['value']}) for {data['duration']} turns")
            
            player.current_hp = player.max_hp
            if hasattr(player, 'status_effects'):
                player.status_effects = {}
    
    print("\n=== Test Complete ===\n")

if __name__ == "__main__":
    test_enemy_skills()
