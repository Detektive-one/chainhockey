// Main game scene
class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }
    
    create() {
        // Initialize game state
        this.player1Score = 0;
        this.player2Score = 0;
        this.gameTime = GameConfig.GAME_DURATION_SECONDS;
        this.gameOver = false;
        this.goalDelay = 0;
        this.winner = null;
        
        // Setup physics world
        this.setupPhysics();
        
        // Create game objects
        this.createWalls();
        this.createGoals();
        this.createPuck();
        this.createPlayers();
        this.createChains();
        
        // Setup input
        this.touchInput = new TouchInputManager(this);
        
        // Setup UI
        this.createUI();
        
        // Setup collision detection
        this.setupCollisions();
        
        // Start timer
        this.startTime = this.time.now;
        this.timerEvent = this.time.addEvent({
            delay: 1000,
            callback: this.updateTimer,
            callbackScope: this,
            loop: true
        });
    }
    
    setupPhysics() {
        this.matter.world.setBounds(0, 0, GameConfig.GAME_WIDTH, GameConfig.GAME_HEIGHT);
        this.matter.world.setGravity(0, GameConfig.GRAVITY);
    }
    
    createWalls() {
        // Top wall
        this.matter.add.rectangle(
            GameConfig.GAME_WIDTH / 2,
            -10,
            GameConfig.GAME_WIDTH,
            20,
            {
                isStatic: true,
                label: 'wall_top',
                collisionFilter: {
                    category: GameConfig.CATEGORY.WALL
                }
            }
        );
        
        // Bottom wall
        this.matter.add.rectangle(
            GameConfig.GAME_WIDTH / 2,
            GameConfig.GAME_HEIGHT + 10,
            GameConfig.GAME_WIDTH,
            20,
            {
                isStatic: true,
                label: 'wall_bottom',
                collisionFilter: {
                    category: GameConfig.CATEGORY.WALL
                }
            }
        );
        
        // Left wall (with gap for goal)
        const goalY = GameConfig.GAME_HEIGHT / 2;
        const goalHalfHeight = GameConfig.GOAL.HEIGHT / 2;
        
        // Top part of left wall
        this.matter.add.rectangle(
            -10,
            (goalY - goalHalfHeight) / 2,
            20,
            goalY - goalHalfHeight,
            {
                isStatic: true,
                label: 'wall_left_top',
                collisionFilter: {
                    category: GameConfig.CATEGORY.WALL
                }
            }
        );
        
        // Bottom part of left wall
        this.matter.add.rectangle(
            -10,
            goalY + goalHalfHeight + (GameConfig.GAME_HEIGHT - goalY - goalHalfHeight) / 2,
            20,
            GameConfig.GAME_HEIGHT - goalY - goalHalfHeight,
            {
                isStatic: true,
                label: 'wall_left_bottom',
                collisionFilter: {
                    category: GameConfig.CATEGORY.WALL
                }
            }
        );
        
        // Right wall (with gap for goal)
        // Top part of right wall
        this.matter.add.rectangle(
            GameConfig.GAME_WIDTH + 10,
            (goalY - goalHalfHeight) / 2,
            20,
            goalY - goalHalfHeight,
            {
                isStatic: true,
                label: 'wall_right_top',
                collisionFilter: {
                    category: GameConfig.CATEGORY.WALL
                }
            }
        );
        
        // Bottom part of right wall
        this.matter.add.rectangle(
            GameConfig.GAME_WIDTH + 10,
            goalY + goalHalfHeight + (GameConfig.GAME_HEIGHT - goalY - goalHalfHeight) / 2,
            20,
            GameConfig.GAME_HEIGHT - goalY - goalHalfHeight,
            {
                isStatic: true,
                label: 'wall_right_bottom',
                collisionFilter: {
                    category: GameConfig.CATEGORY.WALL
                }
            }
        );
    }
    
    createGoals() {
        this.goalLeft = new Goal(this, 'left');
        this.goalRight = new Goal(this, 'right');
    }
    
    createPuck() {
        this.puck = new Puck(
            this,
            GameConfig.GAME_WIDTH / 2,
            GameConfig.GAME_HEIGHT / 2
        );
    }
    
    createPlayers() {
        // Player 1 (right side, red)
        this.striker1 = new Striker(
            this,
            GameConfig.PLAYER1_SPAWN_X,
            GameConfig.PLAYER_SPAWN_Y,
            1
        );
        
        this.hammer1 = new Hammer(
            this,
            GameConfig.PLAYER1_SPAWN_X + 100,
            GameConfig.PLAYER_SPAWN_Y,
            1
        );
        
        // Player 2 (left side, blue)
        this.striker2 = new Striker(
            this,
            GameConfig.PLAYER2_SPAWN_X,
            GameConfig.PLAYER_SPAWN_Y,
            2
        );
        
        this.hammer2 = new Hammer(
            this,
            GameConfig.PLAYER2_SPAWN_X - 100,
            GameConfig.PLAYER_SPAWN_Y,
            2
        );
    }
    
    createChains() {
        this.chain1 = new ChainSystem(this, this.striker1, this.hammer1, 1);
        this.chain2 = new ChainSystem(this, this.striker2, this.hammer2, 2);
    }
    
    createUI() {
        // Background
        this.add.rectangle(0, 0, GameConfig.GAME_WIDTH, GameConfig.GAME_HEIGHT, 0x000000).setOrigin(0).setDepth(-1);
        
        // Center line
        this.add.line(
            0, 0,
            GameConfig.CENTER_LINE_X, 0,
            GameConfig.CENTER_LINE_X, GameConfig.GAME_HEIGHT,
            GameConfig.COLORS.GRAY
        ).setOrigin(0).setLineWidth(2).setDepth(-1);
        
        // Border
        const border = this.add.graphics();
        border.lineStyle(4, GameConfig.COLORS.WHITE);
        border.strokeRect(0, 0, GameConfig.GAME_WIDTH, GameConfig.GAME_HEIGHT);
        border.setDepth(10);
        
        // Score text
        this.scoreText = this.add.text(
            GameConfig.GAME_WIDTH / 2,
            40,
            '0  -  0',
            {
                fontSize: '48px',
                fill: '#ffffff',
                fontStyle: 'bold'
            }
        ).setOrigin(0.5).setDepth(10);
        
        // Timer text
        this.timerText = this.add.text(
            GameConfig.GAME_WIDTH / 2,
            90,
            '05:00',
            {
                fontSize: '36px',
                fill: '#ffffff'
            }
        ).setOrigin(0.5).setDepth(10);
        
        // Pause button
        const pauseButton = this.add.rectangle(
            GameConfig.GAME_WIDTH - 50,
            40,
            80,
            40,
            0x646464
        ).setInteractive({ useHandCursor: true }).setDepth(10);
        
        this.add.text(
            GameConfig.GAME_WIDTH - 50,
            40,
            'PAUSE',
            {
                fontSize: '16px',
                fill: '#ffffff'
            }
        ).setOrigin(0.5).setDepth(10);
        
        pauseButton.on('pointerdown', () => {
            this.scene.pause();
            this.scene.launch('PauseScene');
        });
        
        // Instructions (faded)
        this.add.text(
            10,
            10,
            'Touch and drag your side to play',
            {
                fontSize: '16px',
                fill: '#666666'
            }
        ).setDepth(10);
    }
    
    setupCollisions() {
        // Listen for collision events with goals
        this.matter.world.on('collisionstart', (event) => {
            event.pairs.forEach((pair) => {
                const { bodyA, bodyB } = pair;
                
                // Check if puck scored in left goal (Player 2 scores)
                if ((bodyA.label === 'puck' && bodyB.label === 'goal_left') ||
                    (bodyB.label === 'puck' && bodyA.label === 'goal_left')) {
                    this.onGoalScored('left');
                }
                
                // Check if puck scored in right goal (Player 1 scores)
                if ((bodyA.label === 'puck' && bodyB.label === 'goal_right') ||
                    (bodyB.label === 'puck' && bodyA.label === 'goal_right')) {
                    this.onGoalScored('right');
                }
            });
        });
    }
    
    onGoalScored(side) {
        if (this.goalDelay > 0 || this.gameOver) return;
        
        // Update score
        if (side === 'left') {
            this.player2Score++;
        } else {
            this.player1Score++;
        }
        
        // Update UI
        this.updateScoreDisplay();
        
        // Reset puck
        this.puck.reset();
        
        // Set delay
        this.goalDelay = GameConfig.GOAL_DELAY_FRAMES;
        
        // Check win condition
        this.checkWinCondition();
    }
    
    updateScoreDisplay() {
        this.scoreText.setText(`${this.player1Score}  -  ${this.player2Score}`);
    }
    
    updateTimer() {
        if (this.gameOver) return;
        
        this.gameTime--;
        
        if (this.gameTime <= 0) {
            this.gameTime = 0;
            this.checkWinCondition();
        }
        
        // Format time as MM:SS
        const minutes = Math.floor(this.gameTime / 60);
        const seconds = this.gameTime % 60;
        this.timerText.setText(
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
        );
    }
    
    checkWinCondition() {
        if (this.gameOver) return;
        
        // Check if someone reached max goals
        if (this.player1Score >= GameConfig.MAX_GOALS) {
            this.endGame(1);
            return;
        }
        
        if (this.player2Score >= GameConfig.MAX_GOALS) {
            this.endGame(2);
            return;
        }
        
        // Check if time is up
        if (this.gameTime <= 0) {
            if (this.player1Score > this.player2Score) {
                this.endGame(1);
            } else if (this.player2Score > this.player1Score) {
                this.endGame(2);
            } else {
                this.endGame(0); // Tie
            }
        }
    }
    
    endGame(winner) {
        this.gameOver = true;
        this.winner = winner;
        
        // Stop timer
        if (this.timerEvent) {
            this.timerEvent.remove();
        }
        
        // Transition to game over scene
        this.time.delayedCall(1000, () => {
            this.scene.start('GameOverScene', {
                winner: this.winner,
                player1Score: this.player1Score,
                player2Score: this.player2Score
            });
        });
    }
    
    update() {
        if (this.gameOver) return;
        
        // Update goal delay
        if (this.goalDelay > 0) {
            this.goalDelay--;
        }
        
        // Handle touch input for Player 1
        const p1Input = this.touchInput.getPlayer1Input();
        if (p1Input.active) {
            this.striker1.setPosition(p1Input.x, p1Input.y);
        }
        
        // Handle touch input for Player 2
        const p2Input = this.touchInput.getPlayer2Input();
        if (p2Input.active) {
            this.striker2.setPosition(p2Input.x, p2Input.y);
        }
        
        // Update game objects
        this.puck.update();
        this.striker1.update();
        this.striker2.update();
        this.hammer1.update();
        this.hammer2.update();
        this.chain1.update();
        this.chain2.update();
    }
}
