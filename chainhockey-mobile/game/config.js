// Game configuration and constants
const GameConfig = {
    // Screen dimensions
    GAME_WIDTH: 1200,
    GAME_HEIGHT: 700,
    
    // Colors
    COLORS: {
        BLACK: 0x000000,
        WHITE: 0xFFFFFF,
        RED: 0xDC3232,
        BLUE: 0x3278DC,
        CYAN: 0x32C8C8,
        PURPLE: 0xC896FF,
        ORANGE: 0xFF8C32,
        GRAY: 0x646464,
        YELLOW: 0xFFDC50,
        GREEN: 0x32FF64
    },
    
    // Physics
    GRAVITY: 0,
    
    // Striker properties
    STRIKER: {
        RADIUS: 20,
        MASS: 5.0,
        FRICTION: 0.1,
        RESTITUTION: 0.4,
        SPEED: 5.0,
        COLOR_P1: 0xDC3232, // Red
        COLOR_P2: 0x3278DC  // Blue
    },
    
    // Hammer properties
    HAMMER: {
        RADIUS: 35,
        MASS: 10.0,
        FRICTION: 0.1,
        RESTITUTION: 1.2,
        COLOR: 0xFF8C32 // Orange
    },
    
    // Puck properties
    PUCK: {
        RADIUS: 15,
        MASS: 1.0,
        FRICTION: 0.02,
        RESTITUTION: 0.85,
        FRICTION_AIR: 0.015, // Air resistance
        COLOR: 0xFFDC50 // Yellow
    },
    
    // Chain properties
    CHAIN: {
        SEGMENTS: 8,
        SEGMENT_LENGTH: 20,
        STIFFNESS: 0.7,
        DAMPING: 0.05,
        THICKNESS: 3,
        COLOR_P1: 0x32C8C8, // Cyan
        COLOR_P2: 0xC896FF  // Purple
    },
    
    // Goal properties
    GOAL: {
        WIDTH: 20,
        HEIGHT: 200,
        COLOR: 0x32FF64 // Green
    },
    
    // Game rules
    GAME_DURATION_SECONDS: 300, // 5 minutes
    MAX_GOALS: 10,
    GOAL_DELAY_FRAMES: 60, // 1 second at 60 FPS
    
    // Player spawn positions
    PLAYER1_SPAWN_X: 900,  // Right side (75%)
    PLAYER2_SPAWN_X: 300,  // Left side (25%)
    PLAYER_SPAWN_Y: 350,   // Middle
    CENTER_LINE_X: 600,    // Middle of screen
    
    // Collision categories
    CATEGORY: {
        PUCK: 0x0001,
        STRIKER: 0x0002,
        HAMMER: 0x0004,
        WALL: 0x0008,
        GOAL: 0x0010,
        CHAIN: 0x0020
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GameConfig;
}