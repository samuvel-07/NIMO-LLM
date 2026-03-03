from brain.input.stream_handler import StreamHandler  # type: ignore
from brain.input.wake_word import WakeWordEngine  # type: ignore
from brain.input.whisper_engine import WhisperEngine  # type: ignore
import asyncio
import numpy as np  # type: ignore
import time
import sys
import os
import queue


def _resolve_path(relative_path):
    """Resolve a relative path for both normal and PyInstaller frozen mode."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller exe — data is in _MEIPASS
        base = sys._MEIPASS  # type: ignore
    else:
        # Running normally — project root
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relative_path)

# States
IDLE = "IDLE"
WAKE_DETECTED = "WAKE_DETECTED"
LISTENING_STREAMING = "LISTENING_STREAMING"
PROCESSING_FINAL = "PROCESSING_FINAL"
EXECUTING = "EXECUTING"


class VoicePipeline:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.state = IDLE

        # GPU detection
        try:
            import torch  # type: ignore
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
        except Exception:
            device = "cpu"
            compute_type = "int8"

        self.stream = StreamHandler()

        # WebRTC VAD
        try:
            import webrtcvad # type: ignore
            self.vad = webrtcvad.Vad(2)  # Level 2 = Balance of fast/accurate
            self.use_webrtc = True
            print("[OK] WebRTC VAD Loaded.")
        except ImportError:
            self.use_webrtc = False
            print("[WARN] WebRTC VAD not found, falling back to RMS.")

        self.vad_buffer = bytearray()

        # Wake Word — sensitivity raised to 0.8 for better low-voice detection
        self.wake_detector = WakeWordEngine(
            access_key="KL0iKRnxM2/KEs6Vd/ajFwp6kyHoIWi4BeT6i1dyjG8t58TvgMDVUg==",
            keyword_paths=[_resolve_path("brain/input/wake_word/JARVIS_en_windows_v4_0_0.ppn")],
            sensitivity=0.85
        )
        self.whisper = WhisperEngine()

        self.audio_buffer = []
        self.silence_start_time = 0.0
        self.last_partial_time = 0.0
        self.wake_time = 0.0
        self.WAKE_GRACE_PERIOD_SEC = 0.0  # Removed to eliminate delays
        self.SILENCE_THRESHOLD_MS = 300  # 300ms instant reaction to pause
        self.SILENCE_RMS = 0.005  # Lowered from 0.015 to properly detect silence (mic idle is 0.000015)
        self.PARTIAL_INTERVAL_MS = 300  # Fast partial updates
        self.SESSION_TIMEOUT_SEC = 15.0
        self.session_expiry_time = 0.0

        # Session window — skip wake word for follow-up commands
        self.session_active = False
        self.session_timeout = 0.0
        self.SESSION_WINDOW_SEC = 10.0  # 10 seconds after last command
        self.SESSION_REENTRY_RMS = 0.04  # Much higher than silence — requires real speech
        self.session_speech_count = 0  # Consecutive loud chunks needed to re-enter
        self.SESSION_SPEECH_REQUIRED = 3  # Need 3 consecutive loud chunks

    async def force_listen(self):
        """Force-enter listening mode — bypasses wake word (triggered by UI Key 2)."""
        if self.state == LISTENING_STREAMING:
            return  # Already listening

        print("[FORCE] Bypassing wake word — entering LISTENING mode")
        await self.orchestrator.bus.emit("WAKE_WORD_DETECTED", {"word": "force_key"})

        self.state = LISTENING_STREAMING
        self.audio_buffer = []
        self.vad_buffer.clear()
        self.silence_start_time = 0.0
        self.wake_time = time.time()
        self.last_partial_time = time.time()
        self.stream.enable_stt()

        # Start/extend session window
        self.session_active = True
        self.session_timeout = time.time() + self.SESSION_WINDOW_SEC

    async def run(self):
        print("[START] Voice Pipeline Starting (2056 Mode - Streaming)...")
        self.stream.start_stream()

        while True:
            if self.state == IDLE:
                await self._handle_idle()
            elif self.state == LISTENING_STREAMING:
                await self._handle_listening_streaming()
            elif self.state == PROCESSING_FINAL:
                await self._handle_processing_final()
            await asyncio.sleep(0.01)

    async def _handle_idle(self):
        try:
            chunk = self.stream.get_wake_word_chunk(block=False)
            if chunk is not None:
                # Check for session window — if active, detect speech without wake word
                if self.session_active and time.time() < self.session_timeout:
                    is_speech = False
                    
                    if getattr(self, 'use_webrtc', False):
                        self.vad_buffer.extend(chunk.tobytes())
                        while len(self.vad_buffer) >= 960:
                            frame = bytes(self.vad_buffer[:960])  # type: ignore
                            self.vad_buffer = self.vad_buffer[960:]  # type: ignore
                            try:
                                if self.vad.is_speech(frame, 16000):
                                    is_speech = True
                            except Exception:
                                pass
                    else:
                        chunk_float = chunk.astype(np.float32) / 32768.0
                        rms = np.sqrt(np.mean(chunk_float ** 2))
                        if rms > self.SESSION_REENTRY_RMS:
                            is_speech = True

                    if is_speech:
                        self.session_speech_count += 1
                        if self.session_speech_count >= self.SESSION_SPEECH_REQUIRED:
                            print(f"[SESSION] Re-entering listening (WebRTC Speech Detected)")
                            await self.orchestrator.bus.emit("WAKE_WORD_DETECTED", {"word": "session"})
                            self.state = LISTENING_STREAMING
                            self.audio_buffer = []
                            self.vad_buffer.clear()
                            self.silence_start_time = 0.0
                            self.wake_time = time.time()
                            self.last_partial_time = time.time()
                            self.stream.enable_stt()
                            self.session_speech_count = 0
                            return
                    else:
                        self.session_speech_count = 0  # Reset — need consecutive chunks

                # Check session timeout
                if self.session_active and time.time() >= self.session_timeout:
                    print("[SESSION] Session window expired. Wake word required.")
                    self.session_active = False

                # Standard wake word detection
                prediction = self.wake_detector.detect(chunk)
                if prediction >= 0:
                    print(f"[WAKE] State: IDLE -> WAKE_DETECTED (Wake Word: {prediction})")
                    await self.orchestrator.bus.emit("WAKE_WORD_DETECTED", {"word": prediction})

                    self.state = LISTENING_STREAMING
                    self.audio_buffer = []
                    self.vad_buffer.clear()
                    self.silence_start_time = 0.0
                    self.wake_time = time.time()
                    self.last_partial_time = time.time()
                    self.stream.enable_stt()

                    # Start/extend session window
                    self.session_active = True
                    self.session_timeout = time.time() + self.SESSION_WINDOW_SEC
        except Exception:
            pass

    async def _handle_listening_streaming(self):
        # Failsafe: Max listen timeout of 10 seconds to prevent getting stuck
        # Must be checked on every loop iteration, even if chunk is None
        if self.wake_time > 0 and (time.time() - self.wake_time) > 10.0:
            print("[TIMEOUT] Max 10s listening limit reached -> PROCESSING_FINAL")
            self.state = PROCESSING_FINAL
            self.stream.disable_stt()
            return

        try:
            chunk = self.stream.get_stt_chunk(block=False)
        except queue.Empty:
            chunk = None
        except Exception as e:
            print(f"[ERROR] Audio STT Queue Error: {e}")
            chunk = None

        if chunk is not None:
            chunk_float = chunk.astype(np.float32) / 32768.0
            self.audio_buffer.append(chunk_float)

            is_speaking = False

            # VAD Check (WebRTC or RMS Fallback)
            if getattr(self, 'use_webrtc', False):
                self.vad_buffer.extend(chunk.tobytes())
                # WebRTC strictly operates on 10, 20 or 30ms (16000Hz 30ms = 960 bytes)
                while len(self.vad_buffer) >= 960:
                    frame = bytes(self.vad_buffer[:960])  # type: ignore
                    self.vad_buffer = self.vad_buffer[960:]  # type: ignore
                    try:
                        if self.vad.is_speech(frame, 16000):
                            is_speaking = True
                    except Exception:
                        pass
                
                if len(self.audio_buffer) % 10 == 0:
                    print(f"[DEBUG VAD] WebRTC Speaking: {is_speaking}")
            else:
                rms = np.sqrt(np.mean(chunk_float ** 2))
                if len(self.audio_buffer) % 10 == 0:
                    print(f"[DEBUG VAD] Current RMS: {rms:.6f} | Target Silence < {self.SILENCE_RMS}")
                if rms >= self.SILENCE_RMS:
                    is_speaking = True

            # Fast VAD Silence check
            if not is_speaking:
                if self.silence_start_time == 0.0:
                    self.silence_start_time = time.time()

                if (time.time() - self.silence_start_time) > (self.SILENCE_THRESHOLD_MS / 1000.0):
                    print("[SILENCE] Silence Detected -> PROCESSING_FINAL")
                    self.state = PROCESSING_FINAL
                    self.stream.disable_stt()
                    self.vad_buffer.clear()
                    return
            else:
                self.silence_start_time = 0.0

                # Periodic Partial Transcription
                if (time.time() - self.last_partial_time) > (self.PARTIAL_INTERVAL_MS / 1000.0):
                    self.last_partial_time = time.time()

                    current_audio = np.concatenate(self.audio_buffer)
                    if len(current_audio) > 8000:
                        loop = asyncio.get_event_loop()
                        partial_text = await loop.run_in_executor(None, self.whisper.transcribe_partial, current_audio)

                        if partial_text:
                            par_lower = partial_text.lower()
                            if "stop" in par_lower.split()[-2:] or "enough jarvis" in par_lower or "shut up" in par_lower:
                                print(f"[INTERRUPT] INTERRUPT DETECTED: '{partial_text}'")
                                await self.orchestrator.bus.emit("INTERRUPT_SIGNAL", {})
                                self.state = IDLE
                                self.stream.disable_stt()
                                return

                            await self.orchestrator.bus.emit("PARTIAL_TRANSCRIPT", {"text": partial_text})
        
        # Always sleep a tiny bit to prevent 100% CPU loops if empty
        await asyncio.sleep(0.01)

    async def _handle_processing_final(self):
        print("[THINKING] Processing Final Audio...")

        if not self.audio_buffer:
            print("[WARN] Empty Buffer. Resetting.")
            self.state = IDLE
            return

        # Concatenate buffer
        full_audio = np.concatenate(self.audio_buffer)

        # Skip very short audio (< 0.5s at 16kHz) — likely noise
        if len(full_audio) < 4800:
            print("[WARN] Audio too short (< 0.3s). Skipping.")
            self.state = IDLE
            return

        # Run Whisper
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self.whisper.transcribe, full_audio)

        if text.strip():
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
            print(f"[USER] User said (Final): '{safe_text}'")

            # Pause mic stream so TTS can output cleanly
            self.stream.pause_stream()

            # Send to orchestrator (which may speak via TTS)
            await self.orchestrator.handle_input(text, {})

            # Resume mic stream after TTS
            self.stream.resume_stream()

            # Mandatory Deaf-Period (0.5s) to allow physical room echoes to dissipate 
            # so JARVIS's microphone does not record his own TTS voice 
            await asyncio.sleep(0.5)
            self.stream.clear_wake_word_queue()

            # Extend session window after successful command
            self.session_active = True
            self.session_timeout = time.time() + self.SESSION_WINDOW_SEC
            print(f"[SESSION] Window extended — {self.SESSION_WINDOW_SEC}s (no wake word needed)")
        else:
            print("[WARN] No speech recognized.")

        self.stream.clear_wake_word_queue()
        self.state = IDLE
        print("[STATE] State: PROCESSING_FINAL -> IDLE")

    def stop(self):
        """Clean shutdown: stop audio stream and wake word engine."""
        print("[VOICE] Stopping pipeline...")
        try:
            if self.stream:
                self.stream.stop_stream()
        except Exception as e:
            print(f"[VOICE] Stream stop error (ok): {e}")
        try:
            if self.wake_detector:
                self.wake_detector.cleanup()
        except Exception as e:
            print(f"[VOICE] Wake detector cleanup error (ok): {e}")
        print("[VOICE] Pipeline stopped.")
