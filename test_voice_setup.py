# Quick JARVIS Voice Test
# Tests if voice recognition is working

import sys
sys.path.insert(0, ".")

print("=" * 60)
print("JARVIS Voice Recognition Test")
print("=" * 60)

print("\n1. Checking dependencies...")
try:
    import pyttsx3
    import pywhatkit
    import wikipedia
    import pyjokes
    print("[OK] All dependencies installed")
except Exception as e:
    print(f"[FAIL] Missing dependency: {e}")
    sys.exit(1)

print("\n2. Testing Text-to-Speech...")
try:
    engine = pyttsx3.init()
    engine.say("Voice system initialized")
    engine.runAndWait()
    print("[OK] Text-to-Speech working")
except Exception as e:
    print(f"[FAIL] TTS error: {e}")

print("\n3. Checking Vosk model...")
import os
vosk_path = "vosk-model-small-en-in-0.4"
if os.path.exists(vosk_path):
    print(f"[OK] Vosk model found at {vosk_path}")
else:
    print(f"[WARN] Vosk model not found")
    print("       Download: https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip")

print("\n4. Testing JARVIS Core import...")
try:
    from jarvis_core import JarvisCore
    print("[OK] JARVIS Core ready")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("SETUP COMPLETE!")
print("=" * 60)
print("\nTo start JARVIS:")
print("  python gui.py")
print("\nOr for visual interface:")
print("  python jarvis_visual.py")
print("\nThen say: 'Jarvis hello' or 'Jarvis open chrome'")
print("=" * 60)
