// Touch input manager for mobile controls
class TouchInputManager {
    constructor(scene) {
        this.scene = scene;

        // Touch zones based on raw screen midpoint (camera is not zoomed/scrolled,
        // so screen x == world x after the FIT scale is accounted for)
        this.setupInput();
    }

    // Convert raw Phaser pointer screen coords → game-world coords accounting for canvas scale
    _toWorld(pointer) {
        return this.scene.cameras.main.getWorldPoint(pointer.x, pointer.y);
    }

    // Which "half" does this pointer belong to?
    _getZone(pointer) {
        const worldPoint = this._toWorld(pointer);
        if (worldPoint.x < GameConfig.CENTER_LINE_X) {
            return 'player2';
        } else {
            return 'player1';
        }
    }

    setupInput() {
        // Tell Phaser we want 4 simultaneous touch points
        this.scene.input.addPointer(3);

        // Store the live pointer objects (not IDs) for each player zone
        // Map: 'player1' | 'player2'  →  Phaser.Input.Pointer | null
        this.activePointers = {
            player1: null,
            player2: null
        };

        this.scene.input.on('pointerdown', this.onPointerDown, this);
        this.scene.input.on('pointerup', this.onPointerUp, this);
        this.scene.input.on('pointermove', this.onPointerMove, this);
    }

    onPointerDown(pointer) {
        const zone = this._getZone(pointer);

        // Only assign if this zone doesn't already have an active pointer
        if (!this.activePointers[zone]) {
            this.activePointers[zone] = pointer;
        }
    }

    onPointerMove(pointer) {
        // Re-assign zone in case the finger crossed the centre line
        // (optional – comment out if you prefer strict zone locking)
        const zone = this._getZone(pointer);
        const otherZone = zone === 'player1' ? 'player2' : 'player1';

        if (this.activePointers[zone] === pointer) {
            // Already assigned correctly – nothing to do
        } else if (this.activePointers[otherZone] === pointer) {
            // Pointer crossed the centre; re-assign
            this.activePointers[otherZone] = null;
            if (!this.activePointers[zone]) {
                this.activePointers[zone] = pointer;
            }
        }
    }

    onPointerUp(pointer) {
        if (this.activePointers.player1 === pointer) {
            this.activePointers.player1 = null;
        }
        if (this.activePointers.player2 === pointer) {
            this.activePointers.player2 = null;
        }
    }

    _getInputFor(zone) {
        const pointer = this.activePointers[zone];
        if (pointer && pointer.isDown) {
            const worldPoint = this._toWorld(pointer);
            return { x: worldPoint.x, y: worldPoint.y, active: true };
        }
        return { x: 0, y: 0, active: false };
    }

    getPlayer1Input() {
        return this._getInputFor('player1');
    }

    getPlayer2Input() {
        return this._getInputFor('player2');
    }

    destroy() {
        this.scene.input.off('pointerdown', this.onPointerDown, this);
        this.scene.input.off('pointerup', this.onPointerUp, this);
        this.scene.input.off('pointermove', this.onPointerMove, this);
        this.activePointers.player1 = null;
        this.activePointers.player2 = null;
    }
}