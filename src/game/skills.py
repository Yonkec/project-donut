from typing import Dict, Optional
import random

class Skill:
    def __init__(self, name: str, description: str, energy_cost: int = 0, cooldown: int = 0):
        self.name = name
        self.description = description
        self.energy_cost = energy_cost
        self.cooldown = cooldown
        self.current_cooldown = 0
        
    def can_use(self, user) -> bool:
        """Check if the skill can be used"""
        return self.current_cooldown == 0
        
    def use(self, user, target) -> Dict:
        """Use the skill and return result information"""
        self.current_cooldown = self.cooldown
        return {"success": True, "message": f"{user.name} used {self.name}"}
        
    def reset_cooldown(self):
        """Reset the skill cooldown to 0"""
        self.current_cooldown = 0
        
    def update_cooldown(self):
        """Reduce the cooldown by 1 if it's greater than 0"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class BasicAttack(Skill):
    def __init__(self):
        super().__init__("Basic Attack", "A simple weapon attack", 0, 0)
        
    def use(self, user, target) -> Dict:
        super().use(user, target)
        
        # Calculate base damage
        base_damage = 0
        if hasattr(user, 'equipment') and user.equipment.get('weapon'):
            base_damage = user.equipment['weapon'].damage
            
        # Add strength bonus
        if hasattr(user, 'get_stats'):
            stats = user.get_stats()
            strength_bonus = max(0, (stats.get('strength', 10) - 10) // 2)
            base_damage += strength_bonus
            
        # Apply random variance (80% to 120%)
        variance = random.uniform(0.8, 1.2)
        damage = max(1, int(base_damage * variance))
        
        # Apply damage to target
        actual_damage = target.take_damage(damage)
        
        # Return result
        return {
            "success": True,
            "damage": actual_damage,
            "message": f"{user.name} attacks {target.name} for {actual_damage} damage!"
        }

class Defend(Skill):
    def __init__(self):
        super().__init__("Defend", "Take a defensive stance to reduce incoming damage", 0, 1)
        
    def use(self, user, target) -> Dict:
        super().use(user, target)
        
        # Apply defensive buff
        if not hasattr(user, 'defense_buff'):
            user.defense_buff = 0
        user.defense_buff = 3  # Reduce damage by 3
        
        return {
            "success": True,
            "message": f"{user.name} takes a defensive stance!"
        }

class PowerAttack(Skill):
    def __init__(self):
        super().__init__("Power Attack", "A powerful attack with higher damage", 2, 2)
        
    def use(self, user, target) -> Dict:
        super().use(user, target)
        
        # Calculate base damage (higher multiplier than basic attack)
        base_damage = 0
        if hasattr(user, 'equipment') and user.equipment.get('weapon'):
            base_damage = user.equipment['weapon'].damage * 2
            
        # Add strength bonus (higher multiplier)
        if hasattr(user, 'get_stats'):
            stats = user.get_stats()
            strength_bonus = max(0, (stats.get('strength', 10) - 10))  # Full strength bonus
            base_damage += strength_bonus
            
        # Apply random variance (90% to 130%)
        variance = random.uniform(0.9, 1.3)
        damage = max(1, int(base_damage * variance))
        
        # Apply damage to target
        actual_damage = target.take_damage(damage)
        
        # Return result
        return {
            "success": True,
            "damage": actual_damage,
            "message": f"{user.name} unleashes a powerful attack on {target.name} for {actual_damage} damage!"
        }

class HealingSkill(Skill):
    def __init__(self):
        super().__init__("Healing", "Restore some health", 3, 3)
        
    def use(self, user, target) -> Dict:
        super().use(user, target)
        
        # Calculate healing amount
        base_healing = 15
        
        # Add wisdom bonus
        if hasattr(user, 'get_stats'):
            stats = user.get_stats()
            wisdom_bonus = max(0, (stats.get('wisdom', 10) - 10) // 2)
            base_healing += wisdom_bonus
            
        # Apply random variance
        variance = random.uniform(0.9, 1.1)
        healing = max(1, int(base_healing * variance))
        
        # Apply healing
        if hasattr(user, 'heal'):
            actual_healing = user.heal(healing)
            message = f"{user.name} heals for {actual_healing} health!"
        else:
            actual_healing = 0
            message = f"{user.name} tried to heal but couldn't!"
            
        return {
            "success": True,
            "healing": actual_healing,
            "message": message
        }

class QuickStrike(Skill):
    def __init__(self):
        super().__init__("Quick Strike", "A swift attack that has a chance to strike twice", 1, 1)
        
    def use(self, user, target) -> Dict:
        super().use(user, target)
        
        # Calculate base damage (slightly lower than basic attack)
        base_damage = 0
        if hasattr(user, 'equipment') and user.equipment.get('weapon'):
            base_damage = int(user.equipment['weapon'].damage * 0.8)
            
        # Add dexterity bonus instead of strength
        if hasattr(user, 'get_stats'):
            stats = user.get_stats()
            dex_bonus = max(0, (stats.get('dexterity', 10) - 10) // 2)
            base_damage += dex_bonus
            
        # Apply random variance
        variance = random.uniform(0.8, 1.2)
        damage = max(1, int(base_damage * variance))
        
        # Apply damage to target
        actual_damage = target.take_damage(damage)
        
        # Check for second hit (based on dexterity)
        second_hit = False
        second_hit_damage = 0
        if hasattr(user, 'get_stats'):
            stats = user.get_stats()
            dex_bonus = max(0, (stats.get('dexterity', 10) - 10) // 2)
            second_hit_chance = min(0.5, 0.2 + (dex_bonus * 0.03))  # Max 50% chance
            second_hit = random.random() < second_hit_chance
            
        if second_hit:
            # Second hit does less damage
            second_hit_damage = max(1, int(damage * 0.6))
            second_hit_actual = target.take_damage(second_hit_damage)
            actual_damage += second_hit_actual
            message = f"{user.name} strikes quickly at {target.name} for {actual_damage} damage (double hit)!"
        else:
            message = f"{user.name} strikes quickly at {target.name} for {actual_damage} damage!"
            
        return {
            "success": True,
            "damage": actual_damage,
            "second_hit": second_hit,
            "message": message
        }