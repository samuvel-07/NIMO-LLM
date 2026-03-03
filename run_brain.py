import asyncio
import sys
import os
import threading
import signal

# Load environment variables from .env (must happen before brain imports)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator
from brain.input.voice_pipeline import VoicePipeline # 2056 Pipeline
from brain.utils.tts import init_tts  # type: ignore

# Initialize TTS engine once at startup
init_tts()


def force_shutdown():
    """Nuclear shutdown — kills Electron and exits instantly."""
    print("\n[FORCE SHUTDOWN] Terminating JARVIS...")
    try:
        os.system("taskkill /F /IM electron.exe 2>nul")
    except Exception:
        pass
    os._exit(0)


def keyboard_monitor():
    """Background thread: press S + Enter to force-kill everything."""
    while True:
        try:
            key = input().strip().lower()
            if key == "s":
                force_shutdown()
        except EOFError:
            break
        except Exception:
            break


async def main():
    print("----------------------------------------------------------------")
    print("   JARVIS BRAIN - NEURAL CORE v4.0")
    print("----------------------------------------------------------------")
    print("   [+] Initializing Orchestrator...")

    orchestrator = Orchestrator()
    await orchestrator.start()

    print("   [+] WebSocket Server Running on ws://localhost:8765")

    # Initialize Voice Pipeline
    print("   [+] Initializing Advanced Voice Pipeline...")
    voice_pipeline = VoicePipeline(orchestrator)

    # Wire pipeline into ws_publisher for clean shutdown via UI
    orchestrator.ws_publisher.set_voice_pipeline(voice_pipeline)

    print("   [+] Brain is ACTIVE and LISTENING (Wake Word: 'Jarvis', 'Alexa').")
    print("----------------------------------------------------------------")
    print("   Press Ctrl+C to stop. Type 's' + Enter for force shutdown.")

    # Signal the Batch Launcher that GUI is safe to spawn
    with open(os.path.join(os.path.dirname(__file__), ".jarvis_ready"), "w") as f:
        f.write("ready")

    # Start keyboard monitor (daemon thread — dies with main process)
    threading.Thread(target=keyboard_monitor, daemon=True).start()

    # Keep alive and run voice loop
    try:
        await asyncio.gather(
            voice_pipeline.run(),
            asyncio.Event().wait()
        )
    except asyncio.CancelledError:
        print("\n[!] Stopping Brain...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] KeyboardInterrupt received. Exiting.")
        force_shutdown()
