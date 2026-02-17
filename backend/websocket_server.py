# JARVIS WebSocket Server - State Broadcaster
# Sends visual states to Three.js frontend

import asyncio
import websockets
import json
import time

# Connected clients
connected_clients = set()

async def handler(websocket):
    """Handle WebSocket connection"""
    # 💎 Extra Professional Improvement: Enforce Single Client
    if len(connected_clients) >= 1:
        print("[System] Rejecting duplicate connection request")
        await websocket.close()
        return

    connected_clients.add(websocket)
    print(f"Client connected. Total clients: {len(connected_clients)}")
    
    try:
        async for message in websocket:
            # Can receive commands from frontend if needed
            print(f"Received: {message}")
    except Exception:
        pass # Normal disconnect handling
    finally:
        connected_clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(connected_clients)}")

async def broadcast_state(state, audio_level=0.0):
    """Broadcast visual state to all connected clients"""
    if connected_clients:
        message = json.dumps({
            "state": state,
            "audio": audio_level,
            "timestamp": time.time()
        })
        
        # Send to all clients
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True
        )

async def demo_state_cycle():
    """Demo: Cycle through states automatically"""
    print("\n=== JARVIS Visual State Demo ===")
    print("States will cycle automatically")
    print("Open visual/index.html in browser to see visualization\n")
    
    while True:
        # IDLE
        print("State: IDLE")
        for _ in range(40):  # 4 seconds
            await broadcast_state("IDLE", 0.0)
            await asyncio.sleep(0.1)
        
        # LISTENING
        print("State: LISTENING")
        for _ in range(30):  # 3 seconds
            await broadcast_state("LISTENING", 0.1)
            await asyncio.sleep(0.1)
        
        # PROCESSING
        print("State: PROCESSING")
        for _ in range(20):  # 2 seconds
            await broadcast_state("PROCESSING", 0.05)
            await asyncio.sleep(0.1)
        
        # RESPONDING (with varying audio)
        print("State: RESPONDING (audio reactive)")
        for i in range(30):  # 3 seconds
            audio = 0.3 + (i % 10) * 0.05  # Simulate audio
            await broadcast_state("RESPONDING", audio)
            await asyncio.sleep(0.1)

async def main():
    """Start WebSocket server and demo"""
    # Start server
    server = await websockets.serve(handler, "localhost", 8765)
    print("=" * 60)
    print("JARVIS WebSocket Server Running")
    print("=" * 60)
    print(f"Server: ws://localhost:8765")
    print("Waiting for visual frontend to connect...")
    print("=" * 60)
    
    # Start demo state cycling
    demo_task = asyncio.create_task(demo_state_cycle())
    
    # Keep running
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutting down JARVIS server...")
        print("Goodbye.")
