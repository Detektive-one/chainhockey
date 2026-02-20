// Chain system connecting striker to hammer
class ChainSystem {
    constructor(scene, striker, hammer, playerNum) {
        this.scene = scene;
        this.striker = striker;
        this.hammer = hammer;
        this.playerNum = playerNum;
        
        // Chain color based on player
        this.color = playerNum === 1 ? GameConfig.CHAIN.COLOR_P1 : GameConfig.CHAIN.COLOR_P2;
        
        // Create chain segments
        this.segments = [];
        this.constraints = [];
        
        this.createChain();
        
        // Graphics for rendering
        this.graphics = scene.add.graphics();
    }
    
    createChain() {
        const strikerPos = this.striker.getPosition();
        const hammerPos = this.hammer.getPosition();
        
        const numSegments = GameConfig.CHAIN.SEGMENTS;
        const dx = (hammerPos.x - strikerPos.x) / (numSegments + 1);
        const dy = (hammerPos.y - strikerPos.y) / (numSegments + 1);
        
        // Create segment bodies
        for (let i = 0; i < numSegments; i++) {
            const x = strikerPos.x + dx * (i + 1);
            const y = strikerPos.y + dy * (i + 1);
            
            const segment = this.scene.matter.add.circle(x, y, 3, {
                label: `chain_segment_p${this.playerNum}_${i}`,
                friction: 0.1,
                frictionAir: 0.05,
                mass: 0.1,
                collisionFilter: {
                    category: GameConfig.CATEGORY.CHAIN,
                    mask: 0 // No collisions
                }
            });
            
            this.segments.push(segment);
        }
        
        // Create constraints
        // Connect striker to first segment
        const firstConstraint = this.scene.matter.add.constraint(
            this.striker.body,
            this.segments[0],
            GameConfig.CHAIN.SEGMENT_LENGTH,
            GameConfig.CHAIN.STIFFNESS,
            {
                damping: GameConfig.CHAIN.DAMPING
            }
        );
        this.constraints.push(firstConstraint);
        
        // Connect segments to each other
        for (let i = 0; i < this.segments.length - 1; i++) {
            const constraint = this.scene.matter.add.constraint(
                this.segments[i],
                this.segments[i + 1],
                GameConfig.CHAIN.SEGMENT_LENGTH,
                GameConfig.CHAIN.STIFFNESS,
                {
                    damping: GameConfig.CHAIN.DAMPING
                }
            );
            this.constraints.push(constraint);
        }
        
        // Connect last segment to hammer
        const lastConstraint = this.scene.matter.add.constraint(
            this.segments[this.segments.length - 1],
            this.hammer.body,
            GameConfig.CHAIN.SEGMENT_LENGTH,
            GameConfig.CHAIN.STIFFNESS,
            {
                damping: GameConfig.CHAIN.DAMPING
            }
        );
        this.constraints.push(lastConstraint);
    }
    
    draw() {
        this.graphics.clear();
        
        // Draw chain as connected lines
        this.graphics.lineStyle(GameConfig.CHAIN.THICKNESS, this.color);
        
        // Draw from striker to first segment
        const strikerPos = this.striker.getPosition();
        if (this.segments.length > 0) {
            this.graphics.beginPath();
            this.graphics.moveTo(strikerPos.x, strikerPos.y);
            this.graphics.lineTo(this.segments[0].position.x, this.segments[0].position.y);
            this.graphics.strokePath();
        }
        
        // Draw between segments
        for (let i = 0; i < this.segments.length - 1; i++) {
            this.graphics.beginPath();
            this.graphics.moveTo(this.segments[i].position.x, this.segments[i].position.y);
            this.graphics.lineTo(this.segments[i + 1].position.x, this.segments[i + 1].position.y);
            this.graphics.strokePath();
        }
        
        // Draw from last segment to hammer
        if (this.segments.length > 0) {
            const hammerPos = this.hammer.getPosition();
            const lastSegment = this.segments[this.segments.length - 1];
            this.graphics.beginPath();
            this.graphics.moveTo(lastSegment.position.x, lastSegment.position.y);
            this.graphics.lineTo(hammerPos.x, hammerPos.y);
            this.graphics.strokePath();
        }
        
        // Draw small circles at each segment
        this.graphics.fillStyle(this.color);
        for (const segment of this.segments) {
            this.graphics.fillCircle(segment.position.x, segment.position.y, 3);
        }
    }
    
    update() {
        this.draw();
    }
    
    destroy() {
        // Remove constraints
        for (const constraint of this.constraints) {
            this.scene.matter.world.removeConstraint(constraint);
        }
        
        // Remove segments
        for (const segment of this.segments) {
            this.scene.matter.world.remove(segment);
        }
        
        this.graphics.destroy();
    }
}