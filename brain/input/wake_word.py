import pvporcupine # type: ignore
import struct
import numpy as np # type: ignore
import time
import os

class WakeWordEngine:
    def __init__(self, 
                 access_key,
                 keyword_paths,
                 sensitivity=0.5):
        
        self.access_key = access_key
        self.keyword_paths = keyword_paths
        self.sensitivity = sensitivity
        self.porcupine = None
        
        # Porcupine expects 512 samples/frame
        self.frame_length = 512 
        self.buffer = []

        print(f"Loading Porcupine with models: {[os.path.basename(p) for p in keyword_paths]}...")
        
        try:
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keyword_paths=self.keyword_paths,
                sensitivities=[sensitivity] * len(keyword_paths)
            )
            print(f"[OK] Porcupine Loaded. Frame Length: {self.porcupine.frame_length}") # type: ignore
            self.frame_length = self.porcupine.frame_length # type: ignore # Update to actual
            
        except Exception as e:
            print(f"[ERROR] Porcupine Load Failed: {e}")
            self.porcupine = None
            self.frame_length = 512 # Default fallback

    def detect(self, audio_chunk):
        """
        Process a chunk of audio (int16 numpy array).
        Returns the index of the detected keyword, or -1.
        """
        if not self.porcupine: 
            return -1
            
        # 1. Handle Buffering
        # Porcupine is STRICT: process(pcm) must be exactly 512 samples.
        # Incoming chunk from StreamHandler might be different (e.g., 4096 or 1024).
        
        # Convert numpy int16 to list of ints (what porcupine expects? verify docs: expects list or struct)
        # Actually, pvporcupine.process(pcm) expects a list/tuple of integers.
        # But we can pass it list(audio_chunk).
        
        self.buffer.extend(audio_chunk.tolist())
        
        detected_index = -1
        
        # Process in chunks of self.frame_length
        while len(self.buffer) >= self.frame_length:
            frame = self.buffer[:self.frame_length]
            self.buffer = self.buffer[self.frame_length:]
            
            result = self.porcupine.process(frame)
            if result >= 0:
                print(f"[!] Wake Word Detected (Index: {result})")
                return result # Return immediately on detection
                
        return -1

    def close(self):
        if self.porcupine:
            self.porcupine.delete() # type: ignore
