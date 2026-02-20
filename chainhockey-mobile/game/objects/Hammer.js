// Hammer - chain-attached hitting piece
class Hammer {
    constructor(scene, x, y, playerNum) {
        this.scene = scene;
        this.playerNum = playerNum;
        
        // Boundary constraints (same as striker)
        if (playerNum === 1) {
            this.minX = GameConfig.CENTER_LINE_X + GameConfig.HAMMER.RADIUS;
            this.maxX = GameConfig.GAME_WIDTH - GameConfig.HAMMER.RADIUS;
        } else {
            this.minX = GameConfig.HAMMER.RADIUS;
            this.maxX = GameConfig.CENTER_LINE_X - GameConfig.HAMMER.RADIUS;
        }
        this.minY = GameConfig.HAMMER.RADIUS;
        this.maxY = GameConfig.GAME_HEIGHT - GameConfig.HAMMER.RADIUS;
        
        // Create physics body
        this.body = scene.matter.add.circle(x, y, GameConfig.HAMMER.RADIUS, {
            label: `hammer_p${playerNum}`,
            friction: GameConfig.HAMMER.FRICTION,
            frictionAir: 0.02,
            restitution: GameConfig.HAMMER.RESTITUTION,
            mass: GameConfig.HAMMER.MASS,
            collisionFilter: {
                category: GameConfig.CATEGORY.HAMMER,
                mask: GameConfig.CATEGORY.PUCK | GameConfig.CATEGORY.WALL
            }
        });
        
        // Create graphics
        this.graphics = scene.add.graphics();
        
        this.draw();
    }
    
    draw() {
        this.graphics.clear();
        
        const pos = this.body.position;
        
        // Main hammer body
        this.graphics.fillStyle(GameConfig.HAMMER.COLOR);
        this.graphics.fillCircle(pos.x, pos.y, GameConfig.HAMMER.RADIUS);
        
        // White outline
        this.graphics.lineStyle(3, GameConfig.COLORS.WHITE);
        this.graphics.strokeCircle(pos.x, pos.y, GameConfig.HAMMER.RADIUS);
        
        // Inner detail circle
        this.graphics.lineStyle(2, 0xFFB464);
        this.graphics.strokeCircle(pos.x, pos.y, GameConfig.HAMMER.RADIUS - 10);
    }
    
    update() {
        // Constrain to boundaries
        const pos = this.body.position;
        let needsConstraint = false;
        let newX = pos.x;
        let newY = pos.y;
        
        if (pos.x < this.minX) {
            newX = this.minX;
            needsConstraint = true;
        } else if (pos.x > this.maxX) {
            newX = this.maxX;
            needsConstraint = true;
        }
        
        if (pos.y < this.minY) {
            newY = this.minY;
            needsConstraint = true;
        } else if (pos.y > this.maxY) {
            newY = this.maxY;
            needsConstraint = true;
        }
        
        if (needsConstraint) {
            this.scene.matter.body.setPosition(this.body, { x: newX, y: newY });
        }
        
        this.draw();
    }
    
    getPosition() {
        return this.body.position;
    }
    
    destroy() {
        this.scene.matter.world.remove(this.body);
        this.graphics.destroy();
    }
}