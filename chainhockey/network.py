"""
Network protocol and WebSocket client for multiplayer.
"""

import json
import asyncio
from typing import Optional, Callable, Dict, Any
from enum import Enum

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None


class ConnectionState(Enum):
    """WebSocket connection state"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    IN_ROOM = "in_room"
    ERROR = "error"


class NetworkClient:
    """WebSocket client for multiplayer game"""
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.websocket: Optional[Any] = None
        self.state = ConnectionState.DISCONNECTED
        self.room_id: Optional[str] = None
        self.player_num: Optional[int] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.connected = False
        
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
    
    async def connect(self):
        """Connect to the game server"""
        if not WEBSOCKETS_AVAILABLE:
            print("Warning: websockets library not available. Multiplayer disabled.")
            return False
        
        try:
            self.state = ConnectionState.CONNECTING
            self.websocket = await websockets.connect(self.server_url)
            self.state = ConnectionState.CONNECTED
            self.connected = True
            
            # Start listening for messages
            asyncio.create_task(self._listen())
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.state = ConnectionState.ERROR
            return False
    
    async def disconnect(self):
        """Disconnect from the server"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.connected = False
        self.state = ConnectionState.DISCONNECTED
        self.room_id = None
        self.player_num = None
    
    async def create_room(self):
        """Create a new game room"""
        if not self.connected:
            return False
        
        message = {
            'type': 'create_room'
        }
        await self._send(message)
        return True
    
    async def join_room(self, room_id: str):
        """Join an existing game room"""
        if not self.connected:
            return False
        
        message = {
            'type': 'join_room',
            'room_id': room_id
        }
        await self._send(message)
        return True
    
    async def send_player_input(self, input_data: Dict):
        """Send player input to server"""
        if not self.connected or not self.room_id:
            return False
        
        message = {
            'type': 'player_input',
            'input': input_data
        }
        await self._send(message)
        return True
    
    async def send_game_state(self, state: Dict):
        """Send game state update to server"""
        if not self.connected or not self.room_id:
            return False
        
        message = {
            'type': 'game_state',
            'state': state
        }
        await self._send(message)
        return True
    
    async def _send(self, message: Dict):
        """Send a message to the server"""
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                print(f"Error sending message: {e}")
                self.connected = False
    
    async def _listen(self):
        """Listen for messages from the server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    # Handle room creation/joining
                    if msg_type == 'room_created':
                        self.room_id = data.get('room_id')
                        self.player_num = data.get('player_num')
                        self.state = ConnectionState.IN_ROOM
                    
                    elif msg_type == 'room_joined':
                        self.room_id = data.get('room_id')
                        self.player_num = data.get('player_num')
                        self.state = ConnectionState.IN_ROOM
                    
                    # Call registered handler
                    if msg_type in self.message_handlers:
                        self.message_handlers[msg_type](data)
                
                except json.JSONDecodeError:
                    print("Invalid JSON received from server")
                except Exception as e:
                    print(f"Error handling message: {e}")
        
        except Exception as e:
            print(f"Connection lost: {e}")
            self.connected = False
            self.state = ConnectionState.DISCONNECTED

