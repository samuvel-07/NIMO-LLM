# Quick Voice Test - Check if microphone is being used
import sounddevice as sd
import numpy as np
import sys

print("Testing JARVIS Microphone...")
print("=" * 60)

try:
    # Check default device
    default_device = sd.query_devices(kind='input')
    print(f"Using: {default_device['name']}")
    print()
    
    # Record 3 seconds
    print("Recording 3 seconds... SAY SOMETHING NOW!")
    duration = 3
    sample_rate = 16000
    
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype='int16')
    sd.wait()
    
    # Check audio level
    audio_data = np.array(recording).flatten()
    max_amp = np.max(np.abs(audio_data))
    
    print()
    print("=" * 60)
    print(f"Max Amplitude: {max_amp}")
    
    if max_amp > 1000:
        print("[OK] Microphone is working!")
        print("     JARVIS should be able to hear you.")
    elif max_amp > 100:
        print("[WARNING] Volume low but detectable")
        print("     Increase mic volume in Windows")
    else:
        print("[ERROR] No sound detected!")
        print("     Check:")
        print("     1. Correct microphone selected in Windows")
        print("     2. Microphone volume at 100%")
        print("     3. Microphone not muted")
    
    print("=" * 60)
    
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
