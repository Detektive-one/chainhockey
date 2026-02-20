// Striker - player-controlled piece
class Striker {
    constructor(scene, x, y, playerNum) {
        this.scene = scene;
        this.playerNum = playerNum;
        this.startX = x;
        this.startY = y;
        
        // Boundary constraints
        if (playerNum === 1) {
            // Player 1 - right half
            this.minX = GameConfig.CENTER_LINE_X + GameConfig.STRIKER.RADIUS;
            this.maxX = GameConfig.GAME_WIDTH - GameConfig.STRIKER.RADIUS;
        } else {
            // Player 2 - left half
            this.minX = GameConfig.STRIKER.RADIUS;
            this.maxX = GameConfig.CENTER_LINE_X - GameConfig.STRIKER.RADIUS;
        }
        this.minY = GameConfig.STRIKER.RADIUS;
        this.maxY = GameConfig.GAME_HEIGHT - GameConfig.STRIKER.RADIUS;
        
        // Create physics body
        this.body = scene.matter.add.circle(x, y, GameConfig.STRIKER.RADIUS, {
            label: `striker_p${playerNum}`,
            friction: GameConfig.STRIKER.FRICTION,
            frictionAir: 0.05,
            restitution: GameConfig.STRIKER.RESTITUTION,
            mass: GameConfig.STRIKER.MASS,
            inertia: Infinity, // Prevent rotation
            collisionFilter: {
                category: GameConfig.CATEGORY.STRIKER,
                mask: GameConfig.CATEGORY.PUCK | GameConfig.CATEGORY.WALL
            }
        });
        
        // Color based on player
        this.color = playerNum === 1 ? GameConfig.STRIKER.COLOR_P1 : GameConfig.STRIKER.COLOR_P2;
        
        // Create graphics
        this.graphics = scene.add.graphics();
        
        this.draw();
    }
    
    draw() {
        this.graphics.clear();
        
        const pos = this.body.position;
        
        // Main striker body
        this.graphics.fillStyle(this.color);
        this.graphics.fillCircle(pos.x, pos.y, GameConfig.STRIKER.RADIUS);
        
        // White outline
        this.graphics.lineStyle(2, GameConfig.COLORS.WHITE);
        this.graphics.strokeCircle(pos.x, pos.y, GameConfig.STRIKER.RADIUS);
    }
    
    update() {
        this.draw();
    }
    
    setPosition(x, y) {
        // Constrain to boundaries
        const constrainedX = Phaser.Math.Clamp(x, this.minX, this.maxX);
        const constrainedY = Phaser.Math.Clamp(y, this.minY, this.maxY);
        
        this.scene.matter.body.setPosition(this.body, {
            x: constrainedX,
            y: constrainedY
        });
    }
    
    getPosition() {
        return this.body.position;
    }
    
    destroy() {
        this.scene.matter.world.remove(this.body);
        this.graphics.destroy();
    }
}