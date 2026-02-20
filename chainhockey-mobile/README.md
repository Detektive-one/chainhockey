# Chain Hockey Mobile

A physics-based air hockey game with chain-connected hammers, optimized for mobile devices.

## 🎮 Features

- **Physics-Based Chain Mechanics**: Strikers connected to hammers via realistic chain physics
- **2-Player Local Multiplayer**: Play with a friend on the same device
- **Touch Controls**: Direct touch-and-drag controls for each player
- **Mobile Optimized**: Responsive design that works on any screen size
- **Complete Game Rules**: 5-minute timer, first to 10 goals wins

## 🎯 How to Play

### Controls
- **Player 1 (Red)**: Touch and drag anywhere on the RIGHT half of the screen
- **Player 2 (Blue)**: Touch and drag anywhere on the LEFT half of the screen

### Game Rules
- Score by getting the puck (yellow) into your opponent's goal (green zones)
- Control your striker (small circle) by touching and dragging
- Your hammer (large circle) follows via the chain and hits harder
- First player to 10 goals wins
- If time runs out (5 minutes), player with most goals wins
- Ties are possible!

### Game Elements
- **Striker** (Small circle): Controlled directly, lower bounce
- **Hammer** (Large circle): Connected via chain, powerful hits
- **Chain** (Colored line): Physics-based connection between striker and hammer
- **Puck** (Yellow circle): The object you're trying to score with
- **Goals** (Green rectangles): Score zones on each side

## 🚀 Running the Game

### Option 1: Simple HTTP Server (Recommended)

```bash
cd chainhockey-mobile
python3 -m http.server 8080
```

Then open your browser to: `http://localhost:8080`

### Option 2: Node.js HTTP Server

```bash
cd chainhockey-mobile
npx http-server -p 8080
```

Then open your browser to: `http://localhost:8080`

### Option 3: Use the included server script

```bash
cd chainhockey-mobile
node server.js
```

Then open your browser to: `http://localhost:3000`

## 📱 Testing on Mobile

1. Start the server on your computer
2. Find your computer's local IP address:
   - **Mac/Linux**: Run `ifconfig | grep inet`
   - **Windows**: Run `ipconfig`
3. On your mobile device, navigate to: `http://YOUR_IP:8080`
4. Add to home screen for full-screen experience

### For Best Mobile Experience
- Use landscape orientation
- Add to home screen (iOS/Android)
- Use full-screen mode
- Disable browser zoom

## 🛠 Technology Stack

- **Game Engine**: Phaser 3 (v3.80+)
- **Physics**: Matter.js (integrated with Phaser)
- **Graphics**: HTML5 Canvas
- **No Build Required**: Pure HTML/JS, runs directly in browser

## 📁 Project Structure

```
chainhockey-mobile/
├── index.html              # Main HTML file
├── game/
│   ├── config.js          # Game constants and configuration
│   ├── main.js            # Phaser initialization
│   ├── managers/
│   │   └── TouchInputManager.js   # Touch input handling
│   ├── objects/
│   │   ├── Puck.js        # Puck game object
│   │   ├── Striker.js     # Player striker
│   │   ├── Hammer.js      # Chain-attached hammer
│   │   ├── ChainSystem.js # Chain physics
│   │   └── Goal.js        # Goal zones
│   └── scenes/
│       ├── BootScene.js   # Initial loading
│       ├── MainMenuScene.js   # Start menu
│       ├── GameScene.js   # Main gameplay
│       ├── PauseScene.js  # Pause overlay
│       └── GameOverScene.js   # End game screen
├── server.js              # Optional Node.js server
└── README.md             # This file
```

## 🎨 Customization

All game constants can be modified in `game/config.js`:

- Physics values (friction, restitution, mass)
- Game rules (timer duration, max goals)
- Visual properties (colors, sizes)
- Chain properties (segments, stiffness)

## 🔧 Troubleshooting

### Game doesn't load
- Make sure you're serving via HTTP (not file://)
- Check browser console for errors
- Ensure you have internet connection (Phaser loads from CDN)

### Touch controls not working
- Make sure you're touching the correct half of the screen
- Try refreshing the page
- Check if browser allows touch events

### Physics feels off
- Adjust values in `game/config.js`
- Modify chain stiffness/damping
- Change mass/restitution values

## 📦 Packaging as Mobile App

To convert to a native mobile app, use:

- **Capacitor**: `npm install @capacitor/core @capacitor/cli`
- **Cordova**: `cordova create` and add www files
- **Electron**: For desktop versions

## 🎮 Game Tips

- Use your striker for controlled hits
- Swing your hammer for powerful shots
- The chain adds momentum to your hammer
- Defend your goal while attacking
- Time your swings for maximum power

## 📝 Original Game

This is a mobile recreation of the Python/Pygame "Chain Hockey" game. The original featured:
- Desktop controls (mouse + WASD)
- Network multiplayer
- Verlet integration physics

This version preserves all core gameplay while optimizing for mobile touch controls.

## 🤝 Credits

Based on the original Chain Hockey Python game with Pygame.

## 📄 License

Open source - feel free to modify and distribute!

---

**Enjoy playing Chain Hockey!** 🏒⛓️
