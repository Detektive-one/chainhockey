// Touch input manager for mobile controls
class TouchInputManager {
    constructor(scene) {
        this.scene = scene;
        this.activePointers = new Map();
        
        // Touch zones
        this.leftHalfEnd = GameConfig.CENTER_LINE_X;
        this.rightHalfStart = GameConfig.CENTER_LINE_X;
        
        this.setupInput();
    }
    
    setupInput() {
        // Enable multi-touch
        this.scene.input.addPointer(3); // Support up to 4 touches
        
        // Listen to pointer events
        this.scene.input.on('pointerdown', this.onPointerDown, this);
        this.scene.input.on('pointermove', this.onPointerMove, this);
        this.scene.input.on('pointerup', this.onPointerUp, this);
    }
    
    onPointerDown(pointer) {
        const worldPoint = this.scene.cameras.main.getWorldPoint(pointer.x, pointer.y);
        
        // Determine which half of the screen was touched
        if (worldPoint.x < this.leftHalfEnd) {
            // Left half - Player 2
            this.activePointers.set('player2', pointer.id);
        } else if (worldPoint.x >= this.rightHalfStart) {
            // Right half - Player 1
            this.activePointers.set('player1', pointer.id);
        }
    }
    
    onPointerMove(pointer) {
        // Update is handled in update() method
    }
    
    onPointerUp(pointer) {
        // Remove pointer from active list
        if (this.activePointers.get('player1') === pointer.id) {
            this.activePointers.delete('player1');
        }
        if (this.activePointers.get('player2') === pointer.id) {
            this.activePointers.delete('player2');
        }
    }
    
    getPlayer1Input() {
        const pointerId = this.activePointers.get('player1');
        if (pointerId !== undefined) {
            const pointer = this.scene.input.pointers.find(p => p.id === pointerId);
            if (pointer && pointer.isDown) {
                const worldPoint = this.scene.cameras.main.getWorldPoint(pointer.x, pointer.y);
                return { x: worldPoint.x, y: worldPoint.y, active: true };
            }
        }
        return { x: 0, y: 0, active: false };
    }
    
    getPlayer2Input() {
        const pointerId = this.activePointers.get('player2');
        if (pointerId !== undefined) {
            const pointer = this.scene.input.pointers.find(p => p.id === pointerId);
            if (pointer && pointer.isDown) {
                const worldPoint = this.scene.cameras.main.getWorldPoint(pointer.x, pointer.y);
                return { x: worldPoint.x, y: worldPoint.y, active: true };
            }
        }
        return { x: 0, y: 0, active: false };
    }
    
    destroy() {
        this.scene.input.off('pointerdown', this.onPointerDown, this);
        this.scene.input.off('pointermove', this.onPointerMove, this);
        this.scene.input.off('pointerup', this.onPointerUp, this);
        this.activePointers.clear();
    }
}