// Puck - the scoring object
class Puck {
    constructor(scene, x, y) {
        this.scene = scene;
        this.startX = x;
        this.startY = y;
        
        // Create physics body
        this.body = scene.matter.add.circle(x, y, GameConfig.PUCK.RADIUS, {
            label: 'puck',
            friction: GameConfig.PUCK.FRICTION,
            frictionAir: GameConfig.PUCK.FRICTION_AIR,
            restitution: GameConfig.PUCK.RESTITUTION,
            mass: GameConfig.PUCK.MASS,
            collisionFilter: {
                category: GameConfig.CATEGORY.PUCK,
                mask: GameConfig.CATEGORY.STRIKER | GameConfig.CATEGORY.HAMMER | GameConfig.CATEGORY.WALL
            }
        });
        
        // Create graphics
        this.graphics = scene.add.graphics();
        
        this.draw();
    }
    
    draw() {
        this.graphics.clear();
        
        const pos = this.body.position;
        
        // Main puck body
        this.graphics.fillStyle(GameConfig.PUCK.COLOR);
        this.graphics.fillCircle(pos.x, pos.y, GameConfig.PUCK.RADIUS);
        
        // Outline
        this.graphics.lineStyle(2, GameConfig.COLORS.WHITE);
        this.graphics.strokeCircle(pos.x, pos.y, GameConfig.PUCK.RADIUS);
        
        // Inner circle for depth
        this.graphics.lineStyle(1, 0xFFF096);
        this.graphics.strokeCircle(pos.x, pos.y, GameConfig.PUCK.RADIUS - 5);
    }
    
    update() {
        this.draw();
    }
    
    reset() {
        this.scene.matter.body.setPosition(this.body, {
            x: this.startX,
            y: this.startY
        });
        this.scene.matter.body.setVelocity(this.body, { x: 0, y: 0 });
        this.scene.matter.body.setAngularVelocity(this.body, 0);
    }
    
    getPosition() {
        return this.body.position;
    }
    
    destroy() {
        this.scene.matter.world.remove(this.body);
        this.graphics.destroy();
    }
}