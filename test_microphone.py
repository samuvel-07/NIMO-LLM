# Microphone Test for JARVIS
# Tests if your microphone is working and can be heard

import sounddevice as sd
import numpy as np
import sys

print("=" * 70)
print("JARVIS MICROPHONE TEST")
print("=" * 70)
print()

# List all audio devices
print("Available Audio Devices:")
print("-" * 70)
devices = sd.query_devices()
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:  # Input devices only
        print(f"  [{i}] {device['name']}")
        print(f"      Channels: {device['max_input_channels']}, Sample Rate: {device['default_samplerate']} Hz")
print()

# Get default input device
default_device = sd.query_devices(kind='input')
print(f"Default Input Device: {default_device['name']}")
print()

# Test recording
print("=" * 70)
print("RECORDING TEST")
print("=" * 70)
print()
print("Recording 5 seconds... SPEAK NOW!")
print("Say 'Jarvis hello' or any command loudly and clearly...")
print()

try:
    # Record 5 seconds
    duration = 5  # seconds
    sample_rate = 16000
    
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype='int16')
    sd.wait()  # Wait until recording is finished
    
    print("Recording complete!")
    print()
    
    # Analyze recording
    audio_data = np.array(recording).flatten()
    max_amplitude = np.max(np.abs(audio_data))
    avg_amplitude = np.mean(np.abs(audio_data))
    
    print("=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    print(f"Max Amplitude: {max_amplitude}")
    print(f"Average Amplitude: {avg_amplitude}")
    print()
    
    if max_amplitude < 100:
        print("[WARNING] Very low volume detected!")
        print("  - Check if microphone is connected")
        print("  - Check microphone volume in Windows settings")
        print("  - Try speaking louder")
    elif max_amplitude < 1000:
        print("[WARNING] Low volume detected")
        print("  - Microphone is working but very quiet")
        print("  - Increase microphone volume in Windows")
        print("  - Speak closer to microphone")
    else:
        print("[OK] Good volume detected!")
        print("  - Microphone is working properly")
        print("  - Volume level is good for voice recognition")
    
    print()
    print("=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    
    if max_amplitude >= 1000:
        print("[PASS] Your microphone is ready for JARVIS!")
        print()
        print("Try running JARVIS now:")
        print("  .\\jarvis_env\\Scripts\\python.exe gui_simple.py")
    else:
        print("[ACTION NEEDED] Fix microphone settings:")
        print()
        print("1. Right-click speaker icon in taskbar")
        print("2. Open Sound Settings")
        print("3. Go to Input settings")
        print("4. Select correct microphone")
        print("5. Test microphone and adjust volume slider")
        print("6. Run this test again")
    
    print()
    
except Exception as e:
    print(f"[ERROR] Microphone test failed: {e}")
    print()
    print("Possible issues:")
    print("  - No microphone connected")
    print("  - Microphone permissions denied")
    print("  - Audio drivers not working")
    sys.exit(1)

print("=" * 70)
