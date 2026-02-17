import asyncio
import time
import threading
from backend.websocket_server import handler as ws_handler, connected_clients
from backend.audio_input import AudioInput
from backend.tts_player import TTSPlayer
from llm_handler import LLMHandler
import websockets
import json

# Global State
current_visual_state = "IDLE"

async def broadcast_visual(state, audio_level=0.0):
    """Send state updates to the Desktop Frontend"""
    if connected_clients:
        msg = json.dumps({"state": state, "audio": audio_level})
        await asyncio.gather(*[c.send(msg) for c in connected_clients], return_exceptions=True)

class JarvisOrchestrator:
    def __init__(self):
        self.llm = LLMHandler()
        
        # Audio Output (TTS)
        self.tts = TTSPlayer(visual_callback=self.on_tts_amplitude)
        
        # Audio Input (Mic)
        # Threshold: 0.015 for float32 (approx equivalent to 500 for int16)
        self.mic = AudioInput(threshold=0.015) 
        self.mic.on_speech_start = self.on_speech_start
        self.mic.on_speech_end = self.on_speech_end
        
        self.loop = asyncio.new_event_loop()
        
    def start(self):
        """Start all systems"""
        print("[System] Starting JARVIS Orchestrator...")
        
        # Start WebSocket Server in separate thread
        server_thread = threading.Thread(target=self._run_ws_server, daemon=True)
        server_thread.start()
        
        # Start Mic
        self.mic.start()
        
        # Start Main Async Loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run_ws_server(self):
        async def runner():
            # Modern websockets server loop
            async with websockets.serve(ws_handler, "localhost", 8765):
                print("[System] WebSocket Server Running on 8765")
                await asyncio.Future() # Run forever
                
        try:
            asyncio.run(runner())
        except Exception as e:
            print(f"[System] WebSocket Error: {e}")

    # --- Events ---

    def on_speech_start(self):
        """User started speaking -> Visual: LISTENING"""
        print("[Event] User Speaking...")
        self.update_visual("LISTENING", 0.1)

    def on_speech_end(self):
        """User stopped speaking -> Processing -> LLM"""
        print("[Event] User Silence. Processing...")
        self.update_visual("PROCESSING", 0.05)
        
        # Determine intent (Mock for now, or connect STT)
        # For prototype, we'll trigger a dummy LLM response or basic chat
        # In real fallback, would call VOSK/Whisper here.
        # Let's direct to LLM demo logic:
        
        threading.Thread(target=self.process_llm_cycle).start()

    def process_llm_cycle(self):
        """Simulate Full Interaction Cycle"""
        # 1. Processing (Visual already set)
        time.sleep(0.5) 
        
        # 2. Generate Response (Mock or Real)
        # user_text = "Hello JARVIS"
        # response = self.llm.generate_response(user_text)
        response = "I am online and systems are fully operational, sir."
        
        # 3. Speak Response
        self.update_visual("RESPONDING", 0.2)
        self.tts.speak(response)
        
        # 4. Return to IDLE
        self.update_visual("IDLE", 0.0)

    def on_tts_amplitude(self, amplitude):
        """Real-time TTS Amplitude -> Visual: RESPONDING"""
        # This is called ~30 times/sec from TTSPlayer thread
        # We need to broadcast this to WebSocket
        asyncio.run_coroutine_threadsafe(
            broadcast_visual("RESPONDING", amplitude), 
            self.loop
        )

    def update_visual(self, state, audio=0.0):
        """Helper to safely broadcast from any thread"""
        asyncio.run_coroutine_threadsafe(
            broadcast_visual(state, audio), 
            self.loop
        )

if __name__ == "__main__":
    jarvis = JarvisOrchestrator()
    jarvis.start()
