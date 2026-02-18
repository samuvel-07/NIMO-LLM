import asyncio
import sys
import os
import signal

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator
from brain.voice_adapter import VoiceAdapter

async def main():
    print("----------------------------------------------------------------")
    print("   JARVIS BRAIN - NEURAL CORE v3.0")
    print("----------------------------------------------------------------")
    print("   [+] Initializing Orchestrator...")
    
    orchestrator = Orchestrator()
    await orchestrator.start()
    
    print("   [+] WebSocket Server Running on ws://localhost:8765")
    
    # Initialize Voice
    # We share a context object? Or does handle_input manage it?
    # Orchestrator manages context internally usually, but handle_input takes a context dict.
    # In test_telemetry we passed {}, let's pass a persistent global context for the session.
    session_context = {}
    voice = VoiceAdapter(orchestrator, session_context)
    
    print("   [+] Voice System Active.")
    print("   [+] Brain is ACTIVE and LISTENING.")
    print("----------------------------------------------------------------")
    print("   Press Ctrl+C to stop.")

    # Keep alive and run voice loop
    try:
        await asyncio.gather(
            voice.listen_loop(),
            asyncio.Event().wait() # Keep alive forever
        )
    except asyncio.CancelledError:
        print("\n[!] Stopping Brain...")

if __name__ == "__main__":
    try:
        # Windows-compatible run
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] KeyboardInterrupt received. Exiting.")
