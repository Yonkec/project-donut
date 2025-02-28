# Create directory structure first
import os

# Make sure the package subdirectories exist
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

# Import common classes for easier access
from .player import Player
from .enemy import Enemy, create_random_enemy, create_goblin, create_orc, create_skeleton
from .items import Item, Equipment, Weapon, Armor, Helmet, Boots, Accessory, Potion
from .skills import Skill, BasicAttack, Defend, PowerAttack, HealingSkill, QuickStrike
from .combat import CombatManager