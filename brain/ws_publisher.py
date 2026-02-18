import asyncio
import json
import websockets

class WebSocketPublisher:

    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None

    async def start_server(self):
        # Prevent starting twice
        if self.server:
            return

        print(f"Starting WebSocket Server on ws://{self.host}:{self.port}")
        async def handler(websocket):
            self.clients.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                self.clients.remove(websocket)

        self.server = await websockets.serve(handler, self.host, self.port)

    async def broadcast(self, event_type, payload):
        if not self.clients:
            return

        message = json.dumps({
            "type": event_type,
            "payload": payload
        })

        # Send to all connected clients
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )

    async def subscriber(self, event):
        """
        Subscriber callback matching EventBus signature.
        Expects event dict with 'type' and 'payload'.
        """
        await self.broadcast(event["type"], event["payload"])
