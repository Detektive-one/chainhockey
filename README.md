# Chain Hockey

A physics-based air hockey game built with Pygame, featuring a unique chain-connected hammer mechanic.

## Overview

Chain Hockey is an innovative take on air hockey where you control a striker that's connected via a physics-based chain to a hammer. Use your mouse to move the striker, and watch as the chain physics dynamically moves the hammer to hit the puck into your opponent's goal!

## Features

- **Physics-based chain simulation** using Verlet integration
- **Realistic collision physics** with mass-based momentum transfer
- **Two-player scoring system** (left vs right goals)
- **Smooth gameplay** with 60 FPS rendering
- **Interactive controls** - mouse movement controls the striker

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

Simply run:
```bash
python main.py
```

## Controls

- **Mouse Movement**: Control the striker position
- **SPACE**: Reset the puck to center
- **ESC**: Quit the game

## Game Mechanics

- **Striker** (Red): Your mouse-controlled piece. Has low bounce for controlled hits.
- **Hammer** (Orange): Connected to the striker via a chain. Has high bounce for powerful hits.
- **Puck** (Yellow): The object you're trying to score with. Moves with realistic friction and physics.
- **Goals**: Score by getting the puck into the green goal areas on either side.

## Project Structure

```
chainhockey/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── chainhockey/           # Main package
    ├── __init__.py        # Package initialization
    ├── config.py          # Game configuration constants
    ├── chain.py           # Chain physics (ChainSegment, Chain)
    ├── game_objects.py    # Game entities (Striker, Hammer, Puck)
    ├── physics.py         # Collision detection and resolution
    └── game.py            # Main game loop and state management
```

## Technical Details

- **Physics Engine**: Custom Verlet integration for chain simulation
- **Collision System**: Elastic collision physics with configurable restitution
- **Frame Rate**: 60 FPS with delta time-based physics updates
- **Chain Constraints**: Multi-iteration constraint solver for stable chain physics

## License

This project is open source and available for modification and distribution.

