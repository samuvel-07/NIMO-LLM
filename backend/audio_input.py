import sounddevice as sd
import numpy as np
import time
import threading

class AudioInput:
    """
    Handles microphone input and Voice Activity Detection (VAD) using sounddevice.
    """
    def __init__(self, sample_rate=16000, chunk_size=1024, threshold=0.015):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.threshold = threshold  # Normalized float threshold for VAD (approx 500/32768)
        self.stream = None
        self.running = False
        self.is_listening = False
        
        # Callbacks
        self.on_speech_start = None
        self.on_speech_end = None
        self.on_audio_chunk = None

    def start(self):
        """Start microphone stream"""
        if self.running:
            return
            
        self.running = True
        
        # sounddevice callback
        def callback(indata, frames, time, status):
            if status:
                print(status)
            
            # indata is numpy array of float32 by default
            # Calculate energy (RMS)
            energy = np.sqrt(np.mean(indata**2))
            
            # Simple VAD Logic
            if energy > self.threshold:
                if not self.is_listening:
                    self.is_listening = True
                    if self.on_speech_start:
                        self.on_speech_start()
            else:
                if self.is_listening:
                    # Debounce could be added here
                    self.is_listening = False
                    if self.on_speech_end:
                        self.on_speech_end()
            
            # Pass chunk
            if self.on_audio_chunk:
                self.on_audio_chunk(indata, energy)

        try:
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                callback=callback
            )
            self.stream.start()
            print(f"[AudioInput] Mic started (sounddevice). Threshold: {self.threshold}")
        except Exception as e:
            print(f"[AudioInput] Error starting stream: {e}")
            self.running = False

    def stop(self):
        """Stop microphone stream"""
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        print("[AudioInput] Mic stopped")

# Test/Debug
if __name__ == "__main__":
    def on_start(): print("Host: [Speaking...]")
    def on_end(): print("Host: [Silence]")
    
    mic = AudioInput(threshold=0.02) # Adjusted for float32
    mic.on_speech_start = on_start
    mic.on_speech_end = on_end
    
    print("Testing AudioInput (sounddevice)... (Press Ctrl+C to stop)")
    mic.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        mic.stop()
