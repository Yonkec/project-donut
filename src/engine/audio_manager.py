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
        self.load_audio_files()
        
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
        pygame.mixer.music.play(-1)  # Loop indefinitely
        self.current_music = music_type
    
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
            sound.play()
    
    def play_ui_click(self):
        self.play_sound(SoundType.UI_CLICK)
    
    def play_ui_drop(self):
        self.play_sound(SoundType.UI_DROP)
    
    def play_attack_sound(self):
        self.play_sound(SoundType.ATTACK)
    
    def play_heal_sound(self):
        self.play_sound(SoundType.HEAL)
