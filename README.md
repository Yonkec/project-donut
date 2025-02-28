# Project Donut

An incremental fantasy RPG with semi-autonomous combat, built with Python and Pygame.

## Game Concept

Project Donut is a fantasy RPG where the player sets up their equipment and combat orchestration before entering battle. Once in combat, the predefined sequence of skills plays out automatically against the enemy - the player can't make changes until after the battle is resolved.

## Features

- **Character Progression**: Level up your character, improve stats, and acquire new equipment
- **Equipment System**: Equip weapons, armor, and accessories with different stats and bonuses
- **Skill System**: Learn and configure various combat skills
- **Combat Orchestration**: Set up your skill sequence before battle
- **Auto-Battle**: Watch your strategy play out automatically in combat
- **Enemy Variety**: Battle against different enemy types with unique stats and behaviors

## Getting Started

### Prerequisites

- Python 3.7+
- Pygame

### Installation

1. Clone the repository
```
git clone https://github.com/yourusername/project-donut.git
cd project-donut
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the game
```
python main.py
```

## Game Controls

- **Mouse**: Click on buttons to navigate menus and make selections
- **ESC**: Exit the current screen (when applicable)

## Development

This project uses a modular structure:

- `src/engine/`: Core game engine, UI system, and state management
- `src/game/`: Game mechanics, entities, and systems

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Pygame](https://www.pygame.org/) - The game library used