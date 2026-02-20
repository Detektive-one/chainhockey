// Main Phaser game configuration and initialization
const phaserConfig = {
    type: Phaser.AUTO,
    width: GameConfig.GAME_WIDTH,
    height: GameConfig.GAME_HEIGHT,
    parent: 'game-container',
    backgroundColor: '#000000',
    physics: {
        default: 'matter',
        matter: {
            gravity: {
                x: 0,
                y: GameConfig.GRAVITY
            },
            debug: false, // Set to true to see physics bodies
            enableSleeping: false
        }
    },
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    },
    scene: [
        BootScene,
        MainMenuScene,
        GameScene,
        PauseScene,
        GameOverScene
    ]
};

// Initialize the game when DOM is ready
window.addEventListener('load', () => {
    // Create game and store globally
    window.game = new Phaser.Game(phaserConfig);
    
    // Prevent default touch behaviors
    document.addEventListener('touchmove', (e) => {
        e.preventDefault();
    }, { passive: false });
    
    // Lock to landscape on mobile
    if (screen.orientation && screen.orientation.lock) {
        screen.orientation.lock('landscape').catch((err) => {
            console.log('Orientation lock not supported:', err);
        });
    }
});
