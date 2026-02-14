# Chain Hockey - Multiplayer Setup Guide

## Server Setup

### Running the Game Server

1. Install server dependencies:
   ```bash
   pip install -r requirements_server.txt
   ```

2. Start the server:
   ```bash
   python server.py
   ```

   The server will run on `ws://localhost:8765` by default.

### For Self-Hosting

1. Update `server.py` to change the host/port if needed
2. Ensure port 8765 (or your chosen port) is open in your firewall
3. Update the server URL in `chainhockey/network_sync.py` if using a remote server

## Client Setup

### Desktop Version

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the game:
   ```bash
   python main.py
   ```

3. Click "Multiplayer" in the main menu
4. Choose "Create Room" or "Join Room"
5. Share the room code with your friend to play together

### Web Version

1. Build for web:
   ```bash
   python build_web.py
   ```

2. Serve the build directory (or use the generated files)
3. Make sure the server URL in the web build points to your server
4. Open in browser and play!

## Network Protocol

See `NETWORK_PROTOCOL.md` for detailed message specifications.

## Troubleshooting

- **Can't connect to server**: Make sure the server is running and the URL is correct
- **Room not found**: Check that the room code is correct (6 characters, case-sensitive)
- **Connection lost**: Check your internet connection and server status
- **Input lag**: This is normal due to network latency. The game uses client-side prediction to minimize this.

