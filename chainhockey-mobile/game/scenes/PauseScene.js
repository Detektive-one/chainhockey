// Pause scene overlay
class PauseScene extends Phaser.Scene {
    constructor() {
        super({ key: 'PauseScene' });
    }
    
    create() {
        const centerX = this.cameras.main.width / 2;
        const centerY = this.cameras.main.height / 2;
        
        // Semi-transparent overlay
        this.add.rectangle(0, 0, this.cameras.main.width, this.cameras.main.height, 0x000000, 0.7).setOrigin(0);
        
        // Paused text
        this.add.text(centerX, centerY - 100, 'PAUSED', {
            fontSize: '64px',
            fill: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Resume button
        const resumeButton = this.add.rectangle(centerX, centerY, 300, 70, 0x32FF64)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => {
                this.scene.stop();
                this.scene.resume('GameScene');
            })
            .on('pointerover', () => {
                resumeButton.setFillStyle(0x50FF82);
            })
            .on('pointerout', () => {
                resumeButton.setFillStyle(0x32FF64);
            });
        
        this.add.text(centerX, centerY, 'RESUME', {
            fontSize: '28px',
            fill: '#000000',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Restart button
        const restartButton = this.add.rectangle(centerX, centerY + 90, 300, 70, 0xFFDC50)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => {
                this.scene.stop();
                this.scene.stop('GameScene');
                this.scene.start('GameScene');
            })
            .on('pointerover', () => {
                restartButton.setFillStyle(0xFFEC70);
            })
            .on('pointerout', () => {
                restartButton.setFillStyle(0xFFDC50);
            });
        
        this.add.text(centerX, centerY + 90, 'RESTART', {
            fontSize: '28px',
            fill: '#000000',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Main menu button
        const menuButton = this.add.rectangle(centerX, centerY + 180, 300, 70, 0xDC3232)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => {
                this.scene.stop();
                this.scene.stop('GameScene');
                this.scene.start('MainMenuScene');
            })
            .on('pointerover', () => {
                menuButton.setFillStyle(0xEC4242);
            })
            .on('pointerout', () => {
                menuButton.setFillStyle(0xDC3232);
            });
        
        this.add.text(centerX, centerY + 180, 'MAIN MENU', {
            fontSize: '28px',
            fill: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
    }
}