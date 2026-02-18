import speech_recognition as sr
import asyncio
import functools
import sys
import queue

# Try to import PyAudio, if it fails, try sounddevice
HAS_PYAUDIO = True
try:
    import pyaudio
except ImportError:
    HAS_PYAUDIO = False
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError:
        print("⚠️ Voice Error: Neither PyAudio nor sounddevice found. Voice input will not work.")

class SoundDeviceStream:
    def __init__(self, stream):
        self.stream = stream

    def read(self, chunk):
        # sounddevice returns (data, overflow)
        data, overflow = self.stream.read(chunk)
        if overflow:
            print("Warning: Audio overflow")
        return bytes(data)

    def close(self):
        self.stream.stop()
        self.stream.close()

class SoundDeviceMicrophone(sr.AudioSource):
    def __init__(self, device_index=None, sample_rate=16000, chunk_size=1024):
        self.device_index = device_index
        self.SAMPLE_RATE = sample_rate
        self.CHUNK = chunk_size
        self.SAMPLE_WIDTH = 2
        self.stream = None

    def __enter__(self):
        try:
            self.raw_stream = sd.RawInputStream(
                samplerate=self.SAMPLE_RATE,
                blocksize=self.CHUNK,
                device=self.device_index,
                channels=1,
                dtype='int16',
                latency='low'
            )
            self.raw_stream.start()
            self.stream = SoundDeviceStream(self.raw_stream)
            return self
        except Exception as e:
            print(f"Error opening sounddevice stream: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.stream:
            self.stream.close()
            self.stream = None

class VoiceAdapter:
    def __init__(self, orchestrator, context):
        self.recognizer = sr.Recognizer()
        self.orchestrator = orchestrator
        self.context = context
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        
        if HAS_PYAUDIO:
            print("🎤 Using PyAudio Microphone")
            self.microphone = sr.Microphone()
        elif 'sounddevice' in sys.modules:
            print("🎤 Using sounddevice Microphone (Fallback)")
            self.microphone = SoundDeviceMicrophone()
        else:
            self.microphone = None
            print("❌ No microphone backend available.")

    async def listen_loop(self):
        if not self.microphone:
            return

        print("🎧 Voice Adapter Initialized.")
        loop = asyncio.get_event_loop()
        
        # Calibration
        try:
            with self.microphone as source:
                 await loop.run_in_executor(None, self.recognizer.adjust_for_ambient_noise, source)
        except Exception as e:
            print(f"⚠️ Calibration skipped or failed: {e}")

        print("🎤 Listening...")

        while True:
            try:
                with self.microphone as source:
                    
                    if isinstance(self.microphone, SoundDeviceMicrophone):
                         pass
                    
                    try:
                        # 1. Listen with Timeouts (Non-blocking)
                        # - timeout: 5s (wait for speech start)
                        # - phrase_time_limit: 10s (max speech duration)
                        audio = await loop.run_in_executor(
                            None, 
                            lambda: self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        )
                    except sr.WaitTimeoutError:
                        # No speech detected in 5 seconds
                        # Just loop again (non-blocking)
                        await asyncio.sleep(0.1) 
                        continue

                # Recognize
                try:
                    text = await loop.run_in_executor(None, lambda: self.recognizer.recognize_google(audio))
                    
                    if text:
                        print(f"🗣 Heard: '{text}'")
                        await self.orchestrator.handle_input(text, self.context)
                
                except sr.UnknownValueError:
                    pass # Speech unintelligible
                except sr.RequestError as e:
                    print(f"⚠️ Voice Service Error: {e}")

            except Exception as e:
                print(f"⚠️ Voice Loop Error: {e}")
                await asyncio.sleep(1)
