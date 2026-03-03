import asyncio
import json
import sys
import os
import websockets # type: ignore


class WebSocketPublisher:

    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None
        self._voice_pipeline = None  # Set after init for shutdown access

    def set_voice_pipeline(self, pipeline):
        """Called by run_brain.py to give shutdown access to the pipeline."""
        self._voice_pipeline = pipeline

    async def start_server(self):
        if self.server:
            return

        print(f"Starting WebSocket Server on ws://{self.host}:{self.port}")

        async def handler(websocket):
            self.clients.add(websocket)
            try:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("type") == "SHUTDOWN":
                            print("[SHUTDOWN] Received from UI")
                            await self._clean_shutdown()
                        elif data.get("type") == "FORCE_LISTEN":
                            print("[FORCE] Listen triggered from UI (Key 2)")
                            if self._voice_pipeline:
                                await self._voice_pipeline.force_listen()
                    except json.JSONDecodeError:
                        pass
            except Exception:
                print("[WS] Client disconnected cleanly.")
            finally:
                self.clients.discard(websocket)

        self.server = await websockets.serve(handler, self.host, self.port)

    async def _clean_shutdown(self):
        """Clean shutdown: stop voice, close server, exit."""
        print("[SHUTDOWN] Stopping voice pipeline...")
        try:
            if self._voice_pipeline:
                self._voice_pipeline.stop()  # type: ignore
        except Exception as e:
            print(f"[SHUTDOWN] Voice stop error (ok): {e}")

        print("[SHUTDOWN] Closing WebSocket server...")
        try:
            if self.server:
                self.server.close()  # type: ignore
                await self.server.wait_closed()  # type: ignore
        except Exception as e:
            print(f"[SHUTDOWN] Server close error (ok): {e}")

        print("[SHUTDOWN] Killing Electron...")
        try:
            os.system("taskkill /F /IM electron.exe 2>nul")
        except Exception:
            pass

        print("[SHUTDOWN] All services stopped. Goodbye.")
        os._exit(0)

    async def broadcast(self, event_type, payload):
        if not self.clients:
            return

        message = json.dumps({
            "type": event_type,
            "payload": payload
        })

        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )

    async def subscriber(self, event):
        """Subscriber callback matching EventBus signature."""
        await self.broadcast(event["type"], event["payload"])
