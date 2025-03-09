import os

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

from .player import Player
from .enemy import Enemy, create_random_enemy, create_goblin, create_orc, create_skeleton
from .items import Item, Equipment, Weapon, Armor, Helmet, Boots, Accessory, Potion
from .skill import Skill
from .skill_manager import SkillManager
from .skill_database import SkillDatabase
from .skill_effects import register_default_effects
from .enemy_manager import EnemyManager
from .enemy_database import EnemyDatabase
from .skills import create_skill_manager
from .combat import CombatManager