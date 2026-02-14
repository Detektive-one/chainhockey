"""
Network synchronization helper for pygame integration.
Handles async websocket operations in a pygame-compatible way.
"""

import threading
import queue
import json
from typing import Optional, Dict, Callable
from .network import NetworkClient, ConnectionState


class NetworkSync:
    """Thread-safe network client wrapper for pygame"""
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.client = NetworkClient(server_url)
        self.message_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.state_queue = queue.Queue()
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.loop = None
    
    def start(self):
        """Start network client in background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_async, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop network client"""
        self.running = False
        if self.client:
            # Signal disconnect
            try:
                import asyncio
                if self.loop:
                    asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
            except:
                pass
    
    def _run_async(self):
        """Run async network client in thread"""
        import asyncio
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Connect
        try:
            self.loop.run_until_complete(self.client.connect())
            
            # Register handlers that put messages in queue
            self.client.register_handler('room_created', lambda d: self.message_queue.put(('room_created', d)))
            self.client.register_handler('room_joined', lambda d: self.message_queue.put(('room_joined', d)))
            self.client.register_handler('player_connected', lambda d: self.message_queue.put(('player_connected', d)))
            self.client.register_handler('player_disconnected', lambda d: self.message_queue.put(('player_disconnected', d)))
            self.client.register_handler('player_input', lambda d: self.input_queue.put(d))
            self.client.register_handler('game_state', lambda d: self.state_queue.put(d))
            self.client.register_handler('error', lambda d: self.message_queue.put(('error', d)))
            
            # Keep running
            while self.running:
                self.loop.run_until_complete(asyncio.sleep(0.1))
        except Exception as e:
            print(f"Network thread error: {e}")
        finally:
            try:
                self.loop.run_until_complete(self.client.disconnect())
            except:
                pass
            self.loop.close()
    
    def create_room(self):
        """Create a room (non-blocking)"""
        if self.loop and self.client.connected:
            import asyncio
            asyncio.run_coroutine_threadsafe(self.client.create_room(), self.loop)
    
    def join_room(self, room_id: str):
        """Join a room (non-blocking)"""
        if self.loop and self.client.connected:
            import asyncio
            asyncio.run_coroutine_threadsafe(self.client.join_room(room_id), self.loop)
    
    def send_input(self, input_data: Dict):
        """Send player input (non-blocking)"""
        if self.loop and self.client.connected:
            import asyncio
            asyncio.run_coroutine_threadsafe(self.client.send_player_input(input_data), self.loop)
    
    def send_state(self, state: Dict):
        """Send game state (non-blocking)"""
        if self.loop and self.client.connected:
            import asyncio
            asyncio.run_coroutine_threadsafe(self.client.send_game_state(state), self.loop)
    
    def poll_messages(self):
        """Poll for messages (call from main thread)"""
        messages = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages
    
    def poll_input(self):
        """Poll for player input (call from main thread)"""
        inputs = []
        while not self.input_queue.empty():
            try:
                inputs.append(self.input_queue.get_nowait())
            except queue.Empty:
                break
        return inputs
    
    def poll_state(self):
        """Poll for game state (call from main thread)"""
        states = []
        while not self.state_queue.empty():
            try:
                states.append(self.state_queue.get_nowait())
            except queue.Empty:
                break
        return states
    
    @property
    def connected(self):
        """Check if connected"""
        return self.client and self.client.connected
    
    @property
    def room_id(self):
        """Get current room ID"""
        return self.client.room_id if self.client else None
    
    @property
    def player_num(self):
        """Get player number"""
        return self.client.player_num if self.client else None

