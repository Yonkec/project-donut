import os
import json

class SaveManager:
    def __init__(self):
        self.save_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "player_save.json")
    
    def save_game(self, player, combat_sequence):
        try:
            save_data = {
                "player": player,
                "combat_sequence": combat_sequence
            }
            
            with open(self.save_file_path, 'w') as f:
                json.dump(save_data, f)
                
            return True, "Game saved successfully!"
                
        except Exception as e:
            error_msg = f"Error saving game: {e}"
            print(error_msg)
            return False, error_msg
    
    def load_game(self):
        if not os.path.exists(self.save_file_path):
            print("No save file found.")
            return False, None, None
            
        try:
            with open(self.save_file_path, 'r') as f:
                save_data = json.load(f)
                
            player = save_data.get("player")
            combat_sequence = save_data.get("combat_sequence")
                
            return True, player, combat_sequence
                
        except Exception as e:
            error_msg = f"Error loading game: {e}"
            print(error_msg)
            return False, None, None
    
    def save_exists(self):
        return os.path.exists(self.save_file_path)
