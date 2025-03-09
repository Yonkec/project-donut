import os
import pygame
from enum import Enum, auto

class MusicType(Enum):
    MENU = auto()
    TOWN = auto()
    BATTLE = auto()
    AFTER_COMBAT = auto()

class SoundType(Enum):
    UI_CLICK = auto()
    UI_DROP = auto()
    ATTACK = auto()
    HEAL = auto()

class AudioManager:
    def __init__(self):
        # Initialize pygame mixer if it hasn't been already
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.sounds = {}
        self.current_music = None
        self.music_paths = {}
        
        # Volume settings (0.0 to 1.0)
        self.master_volume = 1.0
        self.music_volume = 0.7
        self.ui_volume = 0.8
        self.sfx_volume = 0.9
        
        self.load_audio_files()
        self.load_settings()
        
    def load_audio_files(self):
        # Get paths to audio files
        audio_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "audio")
        
        # Music paths
        self.music_paths[MusicType.MENU] = os.path.join(audio_folder, "Project Donut.mp3")
        self.music_paths[MusicType.TOWN] = os.path.join(audio_folder, "Town Music.mp3")
        self.music_paths[MusicType.BATTLE] = os.path.join(audio_folder, "Battle Music 1.mp3")
        self.music_paths[MusicType.AFTER_COMBAT] = os.path.join(audio_folder, "After Combat.mp3")
        
        # Sound effect paths
        sound_paths = {
            SoundType.UI_CLICK: os.path.join(audio_folder, "ui_click.wav"),
            SoundType.UI_DROP: os.path.join(audio_folder, "ui_click2.mp3"),
            SoundType.ATTACK: os.path.join(audio_folder, "attack.wav"),
            SoundType.HEAL: os.path.join(audio_folder, "heal.wav")
        }
        
        # Load sound effects
        try:
            for sound_type, path in sound_paths.items():
                if os.path.exists(path):
                    self.sounds[sound_type] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Error loading sounds: {e}")
    
    def play_music(self, music_type):
        path = self.music_paths.get(music_type)
        if not path or not os.path.exists(path) or self.current_music == music_type:
            return
            
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        self.update_music_volume()
        pygame.mixer.music.play(-1)  # Loop indefinitely
        self.current_music = music_type
        
    def update_music_volume(self):
        effective_volume = self.master_volume * self.music_volume
        pygame.mixer.music.set_volume(effective_volume)
    
    def play_menu_music(self):
        self.play_music(MusicType.MENU)
    
    def play_town_music(self):
        self.play_music(MusicType.TOWN)
    
    def play_battle_music(self):
        self.play_music(MusicType.BATTLE)
    
    def play_after_combat_music(self):
        self.play_music(MusicType.AFTER_COMBAT)
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
    
    def play_sound(self, sound_type):
        sound = self.sounds.get(sound_type)
        if sound:
            # Apply appropriate volume based on sound type
            if sound_type in [SoundType.UI_CLICK, SoundType.UI_DROP]:
                effective_volume = self.master_volume * self.ui_volume
            else:
                effective_volume = self.master_volume * self.sfx_volume
                
            sound.set_volume(effective_volume)
            sound.play()
    
    def play_ui_click(self):
        self.play_sound(SoundType.UI_CLICK)
    
    def play_ui_drop(self):
        self.play_sound(SoundType.UI_DROP)
    
    def play_attack_sound(self):
        self.play_sound(SoundType.ATTACK)
    
    def play_heal_sound(self):
        self.play_sound(SoundType.HEAL)
        
    def set_master_volume(self, volume):
        self.master_volume = max(0.0, min(1.0, volume))
        self.update_music_volume()
        self.save_settings()
        
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        self.update_music_volume()
        self.save_settings()
        
    def set_ui_volume(self, volume):
        self.ui_volume = max(0.0, min(1.0, volume))
        self.save_settings()
        
    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        self.save_settings()
        
    def save_settings(self):
        import json
        import os
        
        settings = {
            "master_volume": self.master_volume,
            "music_volume": self.music_volume,
            "ui_volume": self.ui_volume,
            "sfx_volume": self.sfx_volume
        }
        
        settings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        os.makedirs(settings_dir, exist_ok=True)
        
        settings_path = os.path.join(settings_dir, "audio_settings.json")
        
        try:
            with open(settings_path, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving audio settings: {e}")
            
    def load_settings(self):
        import json
        import os
        
        settings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        settings_path = os.path.join(settings_dir, "audio_settings.json")
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    
                self.master_volume = settings.get("master_volume", self.master_volume)
                self.music_volume = settings.get("music_volume", self.music_volume)
                self.ui_volume = settings.get("ui_volume", self.ui_volume)
                self.sfx_volume = settings.get("sfx_volume", self.sfx_volume)
                
                self.update_music_volume()
            except Exception as e:
                print(f"Error loading audio settings: {e}")
