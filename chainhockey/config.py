"""
Configuration constants for Chain Hockey game.
"""

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (50, 120, 220)
CYAN = (50, 200, 200)
ORANGE = (255, 140, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 220, 80)

# Striker properties
STRIKER_RADIUS = 20
HAMMER_RADIUS = 35
STRIKER_COLOR = RED
HAMMER_COLOR = ORANGE
STRIKER_MASS = 5.0
HAMMER_MASS = 10.0

# Puck properties
PUCK_RADIUS = 15
PUCK_COLOR = YELLOW
PUCK_MASS = 1
PUCK_FRICTION = 0.985
PUCK_WALL_BOUNCE = 0.85

# Chain properties
CHAIN_LENGTH = 30
CHAIN_SEGMENTS = 10
SEGMENT_LENGTH = 15
CHAIN_COLOR = CYAN
CHAIN1_COLOR = CYAN  # Player 1 chain color
CHAIN2_COLOR = (200, 150, 255)  # Player 2 chain color (purple)
CHAIN_THICKNESS = 3

# Physics
GRAVITY = 0.0
DAMPING = 0.80
CONSTRAINT_ITERATIONS = 15
CHAIN_SEGMENT_RADIUS = 2

# Goal properties
GOAL_WIDTH = 20
GOAL_HEIGHT = 200
GOAL_COLOR = (50, 255, 100)  # Green
GOAL_LEFT_X = 0
GOAL_RIGHT_X = SCREEN_WIDTH - GOAL_WIDTH
GOAL_Y = (SCREEN_HEIGHT - GOAL_HEIGHT) // 2

# Player properties
PLAYER1_COLOR = RED  # Right side player
PLAYER2_COLOR = BLUE  # Left side player
PLAYER1_SPAWN_X = SCREEN_WIDTH * 0.75  # Right half
PLAYER2_SPAWN_X = SCREEN_WIDTH * 0.25  # Left half
PLAYER_SPAWN_Y = SCREEN_HEIGHT // 2
CENTER_LINE_X = SCREEN_WIDTH // 2

# Movement speed for keyboard controls
STRIKER_SPEED = 5.0

# Game rules
GAME_DURATION_SECONDS = 300  # 5 minutes
MAX_GOALS = 10  # First to 10 goals wins

# Default configuration dictionary for fallback
DEFAULT_CONFIG = {
    'player1': {
        'striker_radius': STRIKER_RADIUS,
        'striker_color': STRIKER_COLOR,
        'striker_mass': STRIKER_MASS,
        'striker_speed': STRIKER_SPEED,
        'chain_segments': CHAIN_SEGMENTS,
        'segment_length': SEGMENT_LENGTH,
        'chain_color': CHAIN1_COLOR,
        'chain_thickness': CHAIN_THICKNESS,
        'chain_damping': DAMPING,
        'hammer_radius': HAMMER_RADIUS,
        'hammer_color': HAMMER_COLOR,
        'hammer_mass': HAMMER_MASS
    },
    'player2': {
        'striker_radius': STRIKER_RADIUS,
        'striker_color': PLAYER2_COLOR,
        'striker_mass': STRIKER_MASS,
        'striker_speed': STRIKER_SPEED,
        'chain_segments': CHAIN_SEGMENTS,
        'segment_length': SEGMENT_LENGTH,
        'chain_color': CHAIN2_COLOR,
        'chain_thickness': CHAIN_THICKNESS,
        'chain_damping': DAMPING,
        'hammer_radius': HAMMER_RADIUS,
        'hammer_color': HAMMER_COLOR,
        'hammer_mass': HAMMER_MASS
    },
    'global': {
        'gravity': GRAVITY,
        'constraint_iterations': CONSTRAINT_ITERATIONS,
        'puck_friction': PUCK_FRICTION,
        'puck_wall_bounce': PUCK_WALL_BOUNCE,
        'game_duration_seconds': GAME_DURATION_SECONDS,
        'max_goals': MAX_GOALS
    }
}

