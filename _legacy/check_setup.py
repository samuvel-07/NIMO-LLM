# Quick Setup Script for JARVIS
# Run this to check if everything is ready

import os
import sys

print("=" * 60)
print("JARVIS Smart Assistant - Setup Checker")
print("=" * 60)

# Check Python version
print("\n1. Python Version:")
print(f"   ✓ {sys.version}")

# Check required modules
print("\n2. Checking Smart Modules:")
required_modules = [
    "intent_classifier.py",
    "context_manager.py",
    "response_generator.py",
    "fallback_handler.py",
    "jarvis_core.py"
]

for module in required_modules:
    if os.path.exists(module):
        print(f"   ✓ {module}")
    else:
        print(f"   ✗ {module} - MISSING!")

# Check config files
print("\n3. Checking Configuration Files:")
config_files = ["apps.json", "memory.json", "gui.py"]
for config in config_files:
    if os.path.exists(config):
        print(f"   ✓ {config}")
    else:
        print(f"   ✗ {config} - MISSING!")

# Check Vosk model
print("\n4. Checking Vosk Model:")
vosk_path = "vosk-model-small-en-in-0.4"
if os.path.isdir(vosk_path):
    print(f"   ✓ Vosk model found at {vosk_path}")
else:
    print(f"   ✗ Vosk model NOT FOUND!")
    print("   → Download from: https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip")
    print("   → Extract to: " + os.path.join(os.getcwd(), vosk_path))

# Check Python dependencies
print("\n5. Checking Python Packages:")
dependencies = [
    "pyttsx3",
    "pywhatkit",
    "wikipedia",
    "pyjokes",
    "vosk",
    "pyaudio",
    "sounddevice",
    "wavio",
    "whisper",
    "speech_recognition"
]

missing = []
for dep in dependencies:
    try:
        __import__(dep)
        print(f"   ✓ {dep}")
    except ImportError:
        print(f"   ✗ {dep} - NOT INSTALLED")
        missing.append(dep)

# Summary
print("\n" + "=" * 60)
if missing:
    print("⚠️  SETUP INCOMPLETE")
    print("\nTo install missing packages:")
    print("pip install " + " ".join(missing))
else:
    print("✅ ALL DEPENDENCIES INSTALLED!")

if not os.path.isdir(vosk_path):
    print("\n❌ Vosk model required before running JARVIS")
    print("   Download: https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip")
else:
    print("\n🚀 Ready to launch JARVIS!")
    print("\nRun: python gui.py")

print("=" * 60)
