// Game over scene
class GameOverScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameOverScene' });
    }
    
    init(data) {
        this.winner = data.winner;
        this.player1Score = data.player1Score;
        this.player2Score = data.player2Score;
    }
    
    create() {
        const centerX = this.cameras.main.width / 2;
        const centerY = this.cameras.main.height / 2;
        
        // Background
        this.add.rectangle(0, 0, this.cameras.main.width, this.cameras.main.height, 0x000000, 0.9).setOrigin(0);
        
        // Game over text
        this.add.text(centerX, centerY - 200, 'GAME OVER', {
            fontSize: '56px',
            fill: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Winner announcement
        let winnerText = '';
        let winnerColor = '#ffffff';
        
        if (this.winner === 1) {
            winnerText = 'Player 1 Wins!';
            winnerColor = '#DC3232'; // Red
        } else if (this.winner === 2) {
            winnerText = 'Player 2 Wins!';
            winnerColor = '#3278DC'; // Blue
        } else {
            winnerText = 'Tie Game!';
            winnerColor = '#FFDC50'; // Yellow
        }
        
        this.add.text(centerX, centerY - 120, winnerText, {
            fontSize: '48px',
            fill: winnerColor,
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Final score
        this.add.text(centerX, centerY - 40, 'Final Score', {
            fontSize: '24px',
            fill: '#aaaaaa'
        }).setOrigin(0.5);
        
        this.add.text(centerX, centerY + 10, `${this.player1Score}  -  ${this.player2Score}`, {
            fontSize: '64px',
            fill: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Play again button
        const playAgainButton = this.add.rectangle(centerX, centerY + 120, 300, 70, 0x32FF64)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => {
                this.scene.start('GameScene');
            })
            .on('pointerover', () => {
                playAgainButton.setFillStyle(0x50FF82);
            })
            .on('pointerout', () => {
                playAgainButton.setFillStyle(0x32FF64);
            });
        
        this.add.text(centerX, centerY + 120, 'PLAY AGAIN', {
            fontSize: '28px',
            fill: '#000000',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Main menu button
        const menuButton = this.add.rectangle(centerX, centerY + 210, 300, 70, 0x646464)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => {
                this.scene.start('MainMenuScene');
            })
            .on('pointerover', () => {
                menuButton.setFillStyle(0x787878);
            })
            .on('pointerout', () => {
                menuButton.setFillStyle(0x646464);
            });
        
        this.add.text(centerX, centerY + 210, 'MAIN MENU', {
            fontSize: '28px',
            fill: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
    }
}