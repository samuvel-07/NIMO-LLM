from faster_whisper import WhisperModel # type: ignore
import numpy as np # type: ignore
import torch # type: ignore
import traceback

# Voice correction dictionary — fixes common Indian English misrecognitions
CORRECTIONS = {
    "insta gram": "instagram",
    "crome": "chrome",
    "chrom": "chrome",
    "you tube": "youtube",
    "shut down": "shutdown",
    "re start": "restart",
    "what's app": "whatsapp",
    "whats app": "whatsapp",
    "note pad": "notepad",
    "vis code": "vs code",
    "v s code": "vs code",
}

def apply_corrections(text):
    lower = text.lower()
    for wrong, correct in CORRECTIONS.items():
        lower = lower.replace(wrong, correct)
    return lower

class WhisperEngine:
    def __init__(self):
        print("Loading 'medium.en' Whisper Model on cuda (float16)...")
        self.model = WhisperModel("medium.en", device="cuda", compute_type="float16")
        # CUDA Warm-Up: Force PyTorch to allocate VRAM on boot
        print("   [~] Warming up GPU tensors...")
        self.model.transcribe(np.zeros(16000).astype(np.float32), language="en")
        print("[OK] Whisper Ready")

    def transcribe_partial(self, audio_data: np.ndarray):
        """
        Fast transcription for partials (Visuals only).
        Uses aggressive VAD and beam_size=1 for speed.
        Returns text.
        """
        if not self.model: return ""
        try:
            segments, _ = self.model.transcribe(
                audio_data,
                beam_size=1,             # Fast decode
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=400),
                language="en",
                task="transcribe",
                initial_prompt="This conversation is in Indian English accent. Common commands include: open chrome, open instagram, open youtube, shutdown system, restart system, search google, play music. Use English words only.",
                condition_on_previous_text=False,
                no_speech_threshold=0.65
            )
            return apply_corrections(" ".join([s.text for s in segments]).strip())
        except:
            return ""

    def transcribe(self, audio_data: np.ndarray):
        """
        Transcribe a complete audio buffer (float32).
        Returns the full text string.
        """
        if not self.model: 
            return ""

        try:
            # Word timestamps enabled for better VAD/segmentation if needed
            segments, info = self.model.transcribe(
                audio_data, 
                beam_size=1,
                best_of=1,
                temperature=0.0,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=300),
                language="en",
                task="transcribe",
                initial_prompt="This conversation is in Indian English accent. Common commands include: open chrome, open instagram, open youtube, shutdown system, restart system, search google, play music. Use English words only.",
                condition_on_previous_text=False,
                no_speech_threshold=0.65
            )
            
            # segments is a generator, must consume it
            text = " ".join([segment.text for segment in segments]).strip()
            return apply_corrections(text)
        except Exception as e:
            print(f"Transcription Error: {e}")
            traceback.print_exc()
            return ""
