# Audio Reactor - Real-time audio analysis and particle reactivity

import numpy as np
import sounddevice as sd
from scipy import signal
import queue
import threading

class AudioReactor:
    """Real-time audio analysis for particle reactivity"""
    
    def __init__(self, sample_rate=16000, fft_size=512):
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.num_freq_bands = 16  # Number of frequency bands for particles
        
        # Audio buffer
        self.audio_queue = queue.Queue()
        self.current_amplitude = 0.0
        self.frequency_bands = np.zeros(self.num_freq_bands)
        
        # Smoothing
        self.amplitude_smooth = 0.0
        self.freq_smooth = np.zeros(self.num_freq_bands)
        self.smooth_factor = 0.3
        
        # Stream
        self.stream = None
        self.is_active = False
        
    def start(self):
        """Start audio monitoring"""
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            
            # Put data in queue
            self.audio_queue.put(indata.copy())
        
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=audio_callback,
            blocksize=self.fft_size
        )
        self.stream.start()
        self.is_active = True
        
    def stop(self):
        """Stop audio monitoring"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.is_active = False
        
    def update(self):
        """Process audio data and update reactivity values"""
        if not self.is_active:
            return
        
        # Get latest audio data
        try:
            audio_data = None
            while not self.audio_queue.empty():
                audio_data = self.audio_queue.get_nowait()
            
            if audio_data is None:
                return
            
            # Flatten to 1D
            audio_data = audio_data.flatten()
            
            # Calculate amplitude (RMS)
            amplitude = np.sqrt(np.mean(audio_data**2))
            amplitude = min(amplitude * 10.0, 1.0)  # Normalize and scale
            
            # Smooth amplitude
            self.amplitude_smooth = (self.amplitude_smooth * (1 - self.smooth_factor) + 
                                    amplitude * self.smooth_factor)
            self.current_amplitude = self.amplitude_smooth
            
            # FFT for frequency analysis
            fft = np.fft.rfft(audio_data, n=self.fft_size)
            fft_magnitude = np.abs(fft)
            
            # Split into frequency bands
            band_size = len(fft_magnitude) // self.num_freq_bands
            
            for i in range(self.num_freq_bands):
                start = i * band_size
                end = start + band_size
                band_energy = np.mean(fft_magnitude[start:end])
                
                # Normalize
                band_energy = min(band_energy / 1000.0, 1.0)
                
                # Smooth
                self.freq_smooth[i] = (self.freq_smooth[i] * (1 - self.smooth_factor) + 
                                      band_energy * self.smooth_factor)
            
            self.frequency_bands = self.freq_smooth.copy()
            
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Audio processing error: {e}")
    
    def get_amplitude(self):
        """Get current smoothed amplitude (0.0 to 1.0)"""
        return self.current_amplitude
    
    def get_frequency_bands(self):
        """Get frequency band energies for particle displacement"""
        return self.frequency_bands
    
    def is_speaking(self, threshold=0.1):
        """Detect if voice/sound is present"""
        return self.current_amplitude > threshold
