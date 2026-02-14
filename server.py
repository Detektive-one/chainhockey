"""
WebSocket game server for Chain Hockey multiplayer.
Run with: python server.py
"""

import asyncio
import json
import logging
from typing import Dict, Set
from websockets.server import serve
from websockets.exceptions import ConnectionClosed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Game rooms: room_id -> {players: Set[websocket], game_state: dict}
rooms: Dict[str, Dict] = {}

# Player connections: websocket -> {room_id, player_num}
connections: Dict = {}

# Message types
MSG_CREATE_ROOM = "create_room"
MSG_JOIN_ROOM = "join_room"
MSG_PLAYER_INPUT = "player_input"
MSG_GAME_STATE = "game_state"
MSG_PLAYER_CONNECTED = "player_connected"
MSG_PLAYER_DISCONNECTED = "player_disconnected"
MSG_ERROR = "error"
MSG_ROOM_CREATED = "room_created"
MSG_ROOM_JOINED = "room_joined"


def generate_room_id() -> str:
    """Generate a unique room ID"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


async def handle_client(websocket, path):
    """Handle a client WebSocket connection"""
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    logger.info(f"Client connected: {client_id}")
    
    room_id = None
    player_num = None
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == MSG_CREATE_ROOM:
                    # Create a new room
                    room_id = generate_room_id()
                    rooms[room_id] = {
                        'players': {websocket},
                        'game_state': None,
                        'player_assignments': {websocket: 1}
                    }
                    connections[websocket] = {
                        'room_id': room_id,
                        'player_num': 1
                    }
                    player_num = 1
                    
                    # Send room ID to creator
                    await websocket.send(json.dumps({
                        'type': MSG_ROOM_CREATED,
                        'room_id': room_id,
                        'player_num': 1
                    }))
                    logger.info(f"Room created: {room_id} by {client_id}")
                
                elif msg_type == MSG_JOIN_ROOM:
                    # Join an existing room
                    requested_room_id = data.get('room_id')
                    
                    if requested_room_id not in rooms:
                        await websocket.send(json.dumps({
                            'type': MSG_ERROR,
                            'message': 'Room not found'
                        }))
                        continue
                    
                    room = rooms[requested_room_id]
                    
                    if len(room['players']) >= 2:
                        await websocket.send(json.dumps({
                            'type': MSG_ERROR,
                            'message': 'Room is full'
                        }))
                        continue
                    
                    # Add player to room
                    room_id = requested_room_id
                    room['players'].add(websocket)
                    player_num = 2
                    room['player_assignments'][websocket] = 2
                    connections[websocket] = {
                        'room_id': room_id,
                        'player_num': 2
                    }
                    
                    # Notify both players
                    await websocket.send(json.dumps({
                        'type': MSG_ROOM_JOINED,
                        'room_id': room_id,
                        'player_num': 2
                    }))
                    
                    # Notify other player
                    for player_ws in room['players']:
                        if player_ws != websocket:
                            await player_ws.send(json.dumps({
                                'type': MSG_PLAYER_CONNECTED,
                                'player_num': 2
                            }))
                    
                    logger.info(f"Player joined room {room_id}: {client_id} as Player 2")
                
                elif msg_type == MSG_PLAYER_INPUT:
                    # Forward player input to other player in room
                    if room_id and player_num:
                        room = rooms.get(room_id)
                        if room:
                            # Broadcast to other player(s)
                            for player_ws in room['players']:
                                if player_ws != websocket:
                                    await player_ws.send(json.dumps({
                                        'type': MSG_PLAYER_INPUT,
                                        'player_num': player_num,
                                        'input': data.get('input')
                                    }))
                
                elif msg_type == MSG_GAME_STATE:
                    # Update and broadcast game state
                    if room_id:
                        room = rooms.get(room_id)
                        if room:
                            room['game_state'] = data.get('state')
                            # Broadcast to other player
                            for player_ws in room['players']:
                                if player_ws != websocket:
                                    await player_ws.send(json.dumps({
                                        'type': MSG_GAME_STATE,
                                        'state': data.get('state')
                                    }))
            
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'type': MSG_ERROR,
                    'message': 'Invalid JSON'
                }))
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await websocket.send(json.dumps({
                    'type': MSG_ERROR,
                    'message': str(e)
                }))
    
    except ConnectionClosed:
        logger.info(f"Client disconnected: {client_id}")
    finally:
        # Clean up on disconnect
        if websocket in connections:
            conn_info = connections[websocket]
            room_id = conn_info.get('room_id')
            
            if room_id and room_id in rooms:
                room = rooms[room_id]
                room['players'].discard(websocket)
                
                # Notify other player
                for player_ws in room['players']:
                    try:
                        await player_ws.send(json.dumps({
                            'type': MSG_PLAYER_DISCONNECTED,
                            'player_num': conn_info.get('player_num')
                        }))
                    except:
                        pass
                
                # Remove room if empty
                if len(room['players']) == 0:
                    del rooms[room_id]
                    logger.info(f"Room {room_id} removed (empty)")
            
            del connections[websocket]


async def main():
    """Start the WebSocket server"""
    host = "0.0.0.0"  # Listen on all interfaces
    port = 8765
    
    logger.info(f"Starting Chain Hockey game server on {host}:{port}")
    
    async with serve(handle_client, host, port):
        logger.info(f"Server running on ws://{host}:{port}")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")

