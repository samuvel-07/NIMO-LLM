import pyttsx3
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import os
import time

class TTSPlayer:
    """
    Handles Text-to-Speech generation and playback with Real-Time Amplitude analysis.
    Uses sounddevice for playback.
    """
    def __init__(self, visual_callback=None):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 165)
        self.visual_callback = visual_callback # Function(amplitude)
        self.is_speaking = False
        self.stop_event = threading.Event()
        self.stream = None

    def speak(self, text):
        """Generate audio and play it with visuals"""
        if not text: return
        
        # 1. Generate Audio to File
        temp_file = "temp_tts.wav"
        if os.path.exists(temp_file):
            try: os.remove(temp_file)
            except: pass
            
        self.engine.save_to_file(text, temp_file)
        self.engine.runAndWait() 
        
        # 2. Play Audio in Thread
        play_thread = threading.Thread(target=self._play_file, args=(temp_file,))
        play_thread.start()

    def _play_file(self, start_file):
        """Internal playback loop"""
        if not os.path.exists(start_file): return
        
        self.is_speaking = True
        self.stop_event.clear()
        
        try:
            # Read file with soundfile (returns float32 numpy array)
            data, fs = sf.read(start_file, always_2d=True)
            
            current_frame = 0
            block_size = 1024
            
            def callback(outdata, frames, time, status):
                nonlocal current_frame
                if status:
                    print(status)
                
                chunk = data[current_frame:current_frame + frames]
                if len(chunk) < frames:
                    # End of file, fill with zeros
                    outdata[:len(chunk)] = chunk
                    outdata[len(chunk):] = 0
                    raise sd.CallbackStop
                else:
                    outdata[:] = chunk
                
                # Analyze Amplitude
                # data is already float32 [-1.0, 1.0]
                rms = np.sqrt(np.mean(chunk**2))
                amplitude = min(rms * 5.0, 1.5) # Scale up for visual impact
                
                if self.visual_callback:
                    self.visual_callback(amplitude)
                
                current_frame += frames

            self.stream = sd.OutputStream(
                samplerate=fs,
                channels=data.shape[1],
                callback=callback,
                blocksize=block_size
            )
            
            with self.stream:
                self.stop_event.wait() # Wait until stopped or finished
                
        except Exception as e:
            print(f"Playback error: {e}")
        finally:
            self.is_speaking = False
            try: os.remove(start_file)
            except: pass

    def stop(self):
        self.stop_event.set()
        if self.stream:
            self.stream.stop()

# Test
if __name__ == "__main__":
    def visual_sim(amp):
        bars = "#" * int(amp * 20)
        print(f"Visual: {bars}", end='\r')

    player = TTSPlayer(visual_callback=visual_sim)
    print("Generating TTS...")
    player.speak("Hello sir, this is a test of the sound device playback system.")
    time.sleep(5) # Keep main thread alive
    player.stop()
