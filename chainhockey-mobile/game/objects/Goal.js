// Goal zones for scoring
class Goal {
    constructor(scene, side) {
        this.scene = scene;
        this.side = side; // 'left' or 'right'
        
        // Position based on side
        if (side === 'left') {
            this.x = GameConfig.GOAL.WIDTH / 2;
        } else {
            this.x = GameConfig.GAME_WIDTH - GameConfig.GOAL.WIDTH / 2;
        }
        
        this.y = GameConfig.GAME_HEIGHT / 2;
        this.width = GameConfig.GOAL.WIDTH;
        this.height = GameConfig.GOAL.HEIGHT;
        
        // Create sensor (trigger, no physical collision)
        this.body = scene.matter.add.rectangle(
            this.x,
            this.y,
            this.width,
            this.height,
            {
                label: `goal_${side}`,
                isStatic: true,
                isSensor: true,
                collisionFilter: {
                    category: GameConfig.CATEGORY.GOAL,
                    mask: GameConfig.CATEGORY.PUCK
                }
            }
        );
        
        // Graphics
        this.graphics = scene.add.graphics();
        this.draw();
    }
    
    draw() {
        this.graphics.clear();
        
        // Draw goal area
        this.graphics.fillStyle(GameConfig.GOAL.COLOR, 0.5);
        this.graphics.fillRect(
            this.x - this.width / 2,
            this.y - this.height / 2,
            this.width,
            this.height
        );
        
        // Outline
        this.graphics.lineStyle(2, GameConfig.GOAL.COLOR);
        this.graphics.strokeRect(
            this.x - this.width / 2,
            this.y - this.height / 2,
            this.width,
            this.height
        );
    }
    
    destroy() {
        this.scene.matter.world.remove(this.body);
        this.graphics.destroy();
    }
}