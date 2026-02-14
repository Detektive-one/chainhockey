"""
Configuration management system for saving and loading game settings.
"""

import json
import os
from dataclasses import dataclass, asdict, field
from typing import Tuple
from .config import (
    STRIKER_RADIUS, STRIKER_COLOR, HAMMER_RADIUS, HAMMER_COLOR,
    STRIKER_MASS, HAMMER_MASS, STRIKER_SPEED,
    CHAIN_SEGMENTS, SEGMENT_LENGTH, CHAIN1_COLOR, CHAIN2_COLOR, CHAIN_THICKNESS,
    DAMPING, GRAVITY, CONSTRAINT_ITERATIONS,
    PUCK_FRICTION, PUCK_WALL_BOUNCE,
    GAME_DURATION_SECONDS, MAX_GOALS
)


@dataclass
class PlayerConfig:
    """Configuration for a single player's striker, chain, and hammer"""
    # Striker properties
    striker_radius: float = STRIKER_RADIUS
    striker_color: Tuple[int, int, int] = field(default_factory=lambda: STRIKER_COLOR)
    striker_mass: float = STRIKER_MASS
    striker_speed: float = STRIKER_SPEED
    
    # Chain properties
    chain_segments: int = CHAIN_SEGMENTS
    segment_length: float = SEGMENT_LENGTH
    chain_color: Tuple[int, int, int] = field(default_factory=lambda: CHAIN1_COLOR)
    chain_thickness: int = CHAIN_THICKNESS
    chain_damping: float = DAMPING
    
    # Hammer properties
    hammer_radius: float = HAMMER_RADIUS
    hammer_color: Tuple[int, int, int] = field(default_factory=lambda: HAMMER_COLOR)
    hammer_mass: float = HAMMER_MASS
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        # Convert color tuples from lists if needed
        for color_key in ['striker_color', 'chain_color', 'hammer_color']:
            if color_key in data and isinstance(data[color_key], list):
                data[color_key] = tuple(data[color_key])
        return cls(**data)


@dataclass
class GameConfig:
    """Complete game configuration"""
    player1: PlayerConfig = field(default_factory=lambda: PlayerConfig(
        chain_color=CHAIN1_COLOR
    ))
    player2: PlayerConfig = field(default_factory=lambda: PlayerConfig(
        striker_color=(50, 120, 220),  # BLUE
        chain_color=CHAIN2_COLOR
    ))
    
    # Global physics
    gravity: float = GRAVITY
    constraint_iterations: int = CONSTRAINT_ITERATIONS
    puck_friction: float = PUCK_FRICTION
    puck_wall_bounce: float = PUCK_WALL_BOUNCE
    
    # Game rules
    game_duration_seconds: int = GAME_DURATION_SECONDS
    max_goals: int = MAX_GOALS
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'player1': self.player1.to_dict(),
            'player2': self.player2.to_dict(),
            'global': {
                'gravity': self.gravity,
                'constraint_iterations': self.constraint_iterations,
                'puck_friction': self.puck_friction,
                'puck_wall_bounce': self.puck_wall_bounce,
                'game_duration_seconds': self.game_duration_seconds,
                'max_goals': self.max_goals
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        player1 = PlayerConfig.from_dict(data.get('player1', {}))
        player2 = PlayerConfig.from_dict(data.get('player2', {}))
        global_data = data.get('global', {})
        
        return cls(
            player1=player1,
            player2=player2,
            gravity=global_data.get('gravity', GRAVITY),
            constraint_iterations=global_data.get('constraint_iterations', CONSTRAINT_ITERATIONS),
            puck_friction=global_data.get('puck_friction', PUCK_FRICTION),
            puck_wall_bounce=global_data.get('puck_wall_bounce', PUCK_WALL_BOUNCE),
            game_duration_seconds=global_data.get('game_duration_seconds', GAME_DURATION_SECONDS),
            max_goals=global_data.get('max_goals', MAX_GOALS)
        )
    
    @classmethod
    def default(cls):
        """Create default configuration"""
        return cls()


class ConfigManager:
    """Manages loading and saving game configurations"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = GameConfig.default()
    
    def load(self):
        """Load configuration from JSON file, fallback to defaults if file doesn't exist"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.config = GameConfig.from_dict(data)
                    return True
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                self.config = GameConfig.default()
                return False
        else:
            # File doesn't exist, use defaults
            self.config = GameConfig.default()
            return False
    
    def save(self):
        """Save current configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self):
        """Get current configuration"""
        return self.config
    
    def set_config(self, config):
        """Set current configuration"""
        self.config = config

