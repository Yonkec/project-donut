import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class EnemyDatabase:
    """
    Handles loading and saving enemy data from JSON files.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.enemies_dir = self.data_dir / "enemies"
        self.enemies = {}
        
        # Create directories if they don't exist
        os.makedirs(self.enemies_dir, exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self) -> None:
        """Load all enemy data from JSON files"""
        # Load enemies
        enemies_path = self.enemies_dir / "enemies.json"
        if enemies_path.exists():
            with open(enemies_path, 'r') as f:
                self.enemies = json.load(f)
    
    def save_data(self) -> None:
        """Save all enemy data to JSON files"""
        # Save enemies
        with open(self.enemies_dir / "enemies.json", 'w') as f:
            json.dump(self.enemies, f, indent=2)
    

    
    def get_enemy(self, enemy_id: str) -> Optional[Dict[str, Any]]:
        """Get an enemy definition by ID"""
        return self.enemies.get(enemy_id)
    

    
    def add_enemy(self, enemy_id: str, enemy_data: Dict[str, Any]) -> None:
        """Add or update an enemy"""
        self.enemies[enemy_id] = enemy_data
        self.save_data()
    
    def get_all_enemies(self) -> Dict[str, Any]:
        """Get all enemies"""
        return self.enemies
    

