// Boot scene - initial setup
class BootScene extends Phaser.Scene {
    constructor() {
        super({ key: 'BootScene' });
    }
    
    preload() {
        // Add loading text
        const centerX = this.cameras.main.width / 2;
        const centerY = this.cameras.main.height / 2;
        
        const loadingText = this.add.text(centerX, centerY, 'Loading Chain Hockey...', {
            fontSize: '24px',
            fill: '#ffffff'
        }).setOrigin(0.5);
    }
    
    create() {
        // Start main menu
        this.scene.start('MainMenuScene');
    }
}