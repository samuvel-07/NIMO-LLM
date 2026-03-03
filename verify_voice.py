
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing Voice Pipeline Imports...")

try:
    import numpy as np # type: ignore
    print("[OK] numpy imported")
except ImportError as e:
    print(f"[FAIL] numpy import failed: {e}")

try:
    import pvporcupine # type: ignore
    print(f"[OK] pvporcupine imported (Version: {pvporcupine.__version__ if hasattr(pvporcupine, '__version__') else 'Unknown'})")
except ImportError as e:
    print(f"[FAIL] pvporcupine import failed: {e}")

try:
    from brain.input.wake_word import WakeWordEngine # type: ignore
    print("[OK] WakeWordEngine imported")
    
    # Test Instantiation (Mocking key if needed, but we have real one)
    # We won't test full init without key in code, but we can check class existence
    print("[OK] WakeWordEngine class available")

except ImportError as e:
    print(f"[FAIL] WakeWordEngine import failed: {e}")

try:
    from brain.input.voice_pipeline import VoicePipeline # type: ignore
    print("[OK] VoicePipeline imported")
except ImportError as e:
    print(f"[FAIL] VoicePipeline import failed: {e}")

print("-" * 30)
print("Testing StreamHandler...")
try:
    from brain.input.stream_handler import StreamHandler # type: ignore
    print("[OK] StreamHandler imported")
    
    # Test Instantiation
    try:
        sh = StreamHandler()
        print(f"[OK] StreamHandler instantiated (Rate: {sh.sample_rate})")
        
        # Test Start/Stop
        print("Testing StreamHandler Start/Stop...")
        sh.start_stream()
        if sh.running:
             print("[OK] Stream started")
        else:
             print("[WARN] Stream failed to start (likely no mic)")
        
        sh.stop_stream()
        print("[OK] Stream stopped")
        
    except Exception as e:
        print(f"[FAIL] StreamHandler runtime error: {e}")

except ImportError as e:
    print(f"[FAIL] StreamHandler import failed: {e}")
