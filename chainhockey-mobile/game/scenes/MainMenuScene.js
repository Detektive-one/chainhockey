// Main menu scene
class MainMenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MainMenuScene' });
    }
    
    create() {
        const centerX = this.cameras.main.width / 2;
        const centerY = this.cameras.main.height / 2;
        
        // Background
        this.add.rectangle(0, 0, this.cameras.main.width, this.cameras.main.height, 0x000000).setOrigin(0);
        
        // Title
        this.add.text(centerX, centerY - 150, 'CHAIN HOCKEY', {
            fontSize: '64px',
            fill: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Subtitle
        this.add.text(centerX, centerY - 80, 'Meteor Hammer Edition', {
            fontSize: '24px',
            fill: '#32C8C8'
        }).setOrigin(0.5);
        
        // Start button
        const startButton = this.add.rectangle(centerX, centerY + 50, 300, 80, 0x32FF64)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => {
                this.scene.start('GameScene');
            })
            .on('pointerover', () => {
                startButton.setFillStyle(0x50FF82);
            })
            .on('pointerout', () => {
                startButton.setFillStyle(0x32FF64);
            });
        
        this.add.text(centerX, centerY + 50, 'START GAME', {
            fontSize: '32px',
            fill: '#000000',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Instructions
        const instructions = [
            'Touch and drag to move your striker',
            'Player 1 (Red): Right side',
            'Player 2 (Blue): Left side',
            'First to 10 goals or most goals in 5 minutes wins!'
        ];
        
        let yOffset = centerY + 180;
        instructions.forEach(text => {
            this.add.text(centerX, yOffset, text, {
                fontSize: '18px',
                fill: '#aaaaaa'
            }).setOrigin(0.5);
            yOffset += 30;
        });
    }
}