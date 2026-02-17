# JARVIS Wake Word Test
# Tests if JARVIS can recognize when you say "Jarvis"

import sys
sys.path.insert(0, ".")

from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json
import os

print("=" * 70)
print("JARVIS WAKE WORD TEST")
print("=" * 70)
print()

# Check if Vosk model exists
model_path = "vosk-model-small-en-in-0.4"
if not os.path.exists(model_path):
    print(f"[ERROR] Vosk model not found at: {model_path}")
    print("Please download the model first.")
    sys.exit(1)

print("[1/3] Loading Vosk model...")
try:
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    print("[OK] Model loaded successfully")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    sys.exit(1)

print()
print("[2/3] Testing microphone...")

# Quick mic test
try:
    test_audio = sd.rec(int(1 * 16000), samplerate=16000, channels=1, dtype='int16')
    sd.wait()
    print("[OK] Microphone accessible")
except Exception as e:
    print(f"[ERROR] Microphone error: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("[3/3] WAKE WORD DETECTION TEST")
print("=" * 70)
print()
print("This will listen for 10 seconds.")
print("Say 'JARVIS' clearly (multiple times if you want)")
print()
print("Starting in 2 seconds...")
import time
time.sleep(2)

print()
print("🎤 LISTENING... (Say 'JARVIS' now!)")
print("-" * 70)

# Record and process
duration = 10  # Listen for 10 seconds
sample_rate = 16000
chunk_size = 4000  # Process in chunks

detections = []
transcriptions = []

try:
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16', 
                        blocksize=chunk_size) as stream:
        start_time = time.time()
        
        while time.time() - start_time < duration:
            audio_chunk, _ = stream.read(chunk_size)
            audio_bytes = bytes(audio_chunk)
            
            if recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                
                if text:
                    print(f"  Heard: '{text}'")
                    transcriptions.append(text)
                    
                    # Check for "jarvis" in various forms
                    if "jarvis" in text.lower():
                        detections.append(text)
                        print(f"  ✓ WAKE WORD DETECTED!")
        
        # Get final result
        final_result = json.loads(recognizer.FinalResult())
        final_text = final_result.get("text", "").strip()
        if final_text and final_text not in transcriptions:
            print(f"  Final: '{final_text}'")
            if "jarvis" in final_text.lower():
                detections.append(final_text)
                print(f"  ✓ WAKE WORD DETECTED!")

except KeyboardInterrupt:
    print("\n[STOPPED] Test interrupted")
except Exception as e:
    print(f"\n[ERROR] {e}")

print()
print("=" * 70)
print("TEST RESULTS")
print("=" * 70)
print()

if not transcriptions:
    print("❌ NO SPEECH DETECTED")
    print()
    print("Possible issues:")
    print("  1. Microphone volume still too low")
    print("     → Run test_microphone.py again to check volume")
    print("     → Should show Max Amplitude > 1000")
    print()
    print("  2. Background noise too high")
    print("     → Move to quieter location")
    print()
    print("  3. Speaking too softly")
    print("     → Speak LOUDER and CLEARER")
    print()
    print("ACTION: Increase microphone volume in Windows settings!")
    
elif detections:
    print(f"✅ SUCCESS! Detected 'Jarvis' {len(detections)} time(s)!")
    print()
    print("What was heard:")
    for i, text in enumerate(detections, 1):
        print(f"  {i}. \"{text}\"")
    print()
    print("=" * 70)
    print("🎉 JARVIS IS READY TO USE!")
    print("=" * 70)
    print()
    print("Run the GUI now:")
    print("  .\\jarvis_env\\Scripts\\python.exe gui_simple.py")
    print()
    print("Then click 'Start JARVIS' and say:")
    print("  'Jarvis open chrome'")
    print("  'Jarvis what time is it'")
    print("  'Jarvis tell me a joke'")
    
else:
    print("⚠️ PARTIAL SUCCESS")
    print()
    print(f"Heard speech but didn't detect 'Jarvis':")
    for i, text in enumerate(transcriptions, 1):
        print(f"  {i}. \"{text}\"")
    print()
    print("This means:")
    print("  ✓ Microphone IS working")
    print("  ✓ Voice recognition IS working")
    print("  ❌ Need to say 'Jarvis' more clearly")
    print()
    print("Tips:")
    print("  - Pronounce: 'JAR-vis' (two syllables)")
    print("  - Speak clearly and at normal speed")
    print("  - Make sure you're saying 'Jarvis', not 'service' or similar")
    print()
    print("Try the test again and say 'JARVIS' louder and clearer!")

print()
print("=" * 70)
