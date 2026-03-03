import pyttsx3  # type: ignore
import queue
import threading

engine = pyttsx3.init()
engine.setProperty('rate', 175)

# Pick a male voice if available
voices = engine.getProperty('voices')
for v in voices:
    if "david" in v.name.lower() or "mark" in v.name.lower():
        engine.setProperty('voice', v.id)
        print(f"[TTS] Voice: {v.name}")
        break

is_speaking = False
speech_queue = queue.Queue()


def _tts_worker():
    global is_speaking
    while True:
        text = speech_queue.get()
        if text is None:
            break
        try:
            print(f"[JARVIS] {text}")
            is_speaking = True
            engine.say(text)
            engine.runAndWait()
            is_speaking = False
        except Exception as e:
            print(f"[TTS] Error: {e}")
            is_speaking = False


threading.Thread(target=_tts_worker, daemon=True).start()


def speak(text):
    """Queue text to be spoken. Non-blocking, sequential, no overlaps."""
    speech_queue.put(text)


def init_tts():
    """No-op — engine is initialized at import time. Kept for backward compatibility."""
    pass
