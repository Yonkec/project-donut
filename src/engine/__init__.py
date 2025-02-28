# Create directory structure first
import os

# Make sure the package subdirectories exist
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

# Import engine components
from .game import Game, GameState
from .ui import UIManager, Button, Label, ProgressBar, UIElement