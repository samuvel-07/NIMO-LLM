import sounddevice as sd # type: ignore
import numpy as np # type: ignore
import queue
import threading
import logging

class StreamHandler:
    """
    Manages a single audio stream from the microphone.
    Feeds two consumers:
    1. Wake Word Engine (Always active or as needed)
    2. STT Engine (Active only when listening)
    """
    def __init__(self, 
                 sample_rate=16000, 
                 chunk_size=480): # 30ms chunk for WebRTC VAD (16000 * 0.03)
        
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Queues
        # Wake Word Queue: Dropping old frames if full isn't great, but we must prevent lag.
        # With a dedicated consumer, it should stay empty.
        self.wake_word_queue = queue.Queue()
        
        # STT Queue: Unbounded or large maxsize to prevent packet loss during processing spikes
        self.stt_queue = queue.Queue()
        
        self.stream = None
        self.running = False
        self.is_listening_for_stt = False  # Gate for STT queue

    def start_stream(self):
        if self.running: return

        def callback(indata, frames, time, status):
            from brain.utils import tts # type: ignore
            if getattr(tts, 'is_speaking', False):
                return

            if status:
                print(f"Stream Status: {status}")
            
            # indata is numpy array (frames, channels)
            # Make sure it's int16 flattened to 1D array
            data_int16 = indata.flatten().astype(np.int16)
            
            # 1. Feed Wake Word (Always, or controllable? Always for now)
            self.wake_word_queue.put(data_int16)
            
            # 2. Feed STT (If enabled)
            if self.is_listening_for_stt:
                # Whisper works with float32 usually, but faster-whisper can take int16 or float32.
                # Converting to float32 here saves compute in the engine loop?
                # Actually, sending int16 bytes or array is fine.
                # Let's send the numpy array, let engine decide.
                # To be safe for VAD/Whisper, let's normalize to float32 -1.0 to 1.0 here?
                # Or just send raw int16.
                # Standard practice: Send int16 to queue, let consumer normalize if needed.
                self.stt_queue.put(data_int16)

        try:
            # Create input stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                device=None,
                channels=1,
                dtype='int16',
                callback=callback
            )
            # Type check for linter
            if self.stream is None:
                raise RuntimeError("Failed to initialize audio stream")
                
            self.stream.start() # type: ignore
            self.running = True
            print(f"[INFO] Audio Stream Started: {self.sample_rate}Hz, Chunk: {self.chunk_size}")
        except Exception as e:
            print(f"[ERROR] Error starting audio stream: {e}")
            self.running = False
            self.stream = None

    def stop_stream(self):
        if self.stream:
            try:
                self.stream.stop() # type: ignore
                self.stream.close() # type: ignore
            except Exception as e:
                print(f"[WARN] Error stopping stream: {e}")
            finally:
                self.stream = None
        self.running = False

    def pause_stream(self):
        """Pause mic input so TTS can use audio device."""
        if self.stream and self.running:
            try:
                self.stream.stop()  # type: ignore
                print("[AUDIO] Mic paused for TTS")
            except Exception as e:
                print(f"[AUDIO] Pause error: {e}")

    def resume_stream(self):
        """Resume mic input after TTS finishes."""
        if self.stream and self.running:
            try:
                self.stream.start()  # type: ignore
                print("[AUDIO] Mic resumed")
            except Exception as e:
                print(f"[AUDIO] Resume error: {e}")

    def enable_stt(self):
        """Start buffering audio for STT"""
        with self.stt_queue.mutex:
            self.stt_queue.queue.clear()
        self.is_listening_for_stt = True

    def disable_stt(self):
        """Stop buffering audio for STT"""
        self.is_listening_for_stt = False

    def clear_wake_word_queue(self):
        """Flush the wake word buffer completely so we only process fresh audio"""
        with self.wake_word_queue.mutex:
            self.wake_word_queue.queue.clear()

    def get_wake_word_chunk(self, block=True):
        return self.wake_word_queue.get(block=block)
    
    def get_stt_chunk(self, block=True):
        return self.stt_queue.get(block=block)
