# JARVIS Core Integration - WebSocket Visual State Broadcaster
# Connects voice JARVIS to Three.js visualization

import asyncio
import websockets
import json
import threading
from typing import Optional

class VisualStateBroadcaster:
    """Broadcasts JARVIS states to WebSocket clients for visualization"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self.current_state = "IDLE"
        self.current_audio = 0.0
        self.server = None
        self.loop = None
        self.thread = None
        
    async def _handler(self, websocket):
        """Handle WebSocket connection"""
        self.connected_clients.add(websocket)
        print(f"[Visual] Client connected. Total: {len(self.connected_clients)}")
        
        try:
            # Send current state immediately
            await self._send_state(websocket, self.current_state, self.current_audio)
            
            async for message in websocket:
                # Can receive commands from frontend if needed
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            print(f"[Visual] Client disconnected. Total: {len(self.connected_clients)}")
    
    async def _send_state(self, websocket, state, audio):
        """Send state to a single client"""
        try:
            message = json.dumps({
                "state": state,
                "audio": audio,
                "timestamp": asyncio.get_event_loop().time()
            })
            await websocket.send(message)
        except Exception as e:
            print(f"[Visual] Error sending to client: {e}")
    
    async def _broadcast_state(self, state, audio):
        """Broadcast state to all connected clients"""
        if self.connected_clients:
            self.current_state = state
            self.current_audio = audio
            
            # Send to all clients
            await asyncio.gather(
                *[self._send_state(client, state, audio) for client in self.connected_clients],
                return_exceptions=True
            )
    
    def _run_server(self):
        """Run WebSocket server in background thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        async def start_server():
            self.server = await websockets.serve(self._handler, self.host, self.port)
            print(f"[Visual] WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
        
        self.loop.run_until_complete(start_server())
    
    def start(self):
        """Start the WebSocket server in a background thread"""
        if self.thread is None:
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
            print("[Visual] WebSocket broadcaster started")
    
    def set_state(self, state: str, audio_level: float = 0.0):
        """
        Set visual state (thread-safe)
        
        States:
        - IDLE: Calm, slow rotation
        - LISTENING: Expanded, blue glow (after wake word)
        - PROCESSING: Subtle motion (analyzing command)
        - RESPONDING: Audio-reactive (speaking response)
        """
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(
                self._broadcast_state(state, audio_level),
                self.loop
            )
    
    def stop(self):
        """Stop the WebSocket server"""
        if self.server:
            self.server.close()
        if self.loop:
            self.loop.stop()
        print("[Visual] WebSocket broadcaster stopped")


# Global instance
_visual_broadcaster: Optional[VisualStateBroadcaster] = None

def get_visual_broadcaster() -> VisualStateBroadcaster:
    """Get or create the global visual broadcaster"""
    global _visual_broadcaster
    if _visual_broadcaster is None:
        _visual_broadcaster = VisualStateBroadcaster()
        _visual_broadcaster.start()
    return _visual_broadcaster

def set_visual_state(state: str, audio_level: float = 0.0):
    """Convenience function to set visual state"""
    broadcaster = get_visual_broadcaster()
    broadcaster.set_state(state, audio_level)


# Example usage in jarvis_core.py:
"""
from visual_integration import set_visual_state

# In __init__:
set_visual_state("IDLE")

# On wake word detected:
set_visual_state("LISTENING")

# On processing command:
set_visual_state("PROCESSING")

# During TTS (with audio amplitude):
set_visual_state("RESPONDING", audio_amplitude)

# After response complete:
set_visual_state("IDLE")
"""
