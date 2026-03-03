import torch
import os
import sys

print("----------------------------------------------------------------")
print("   VOICE PIPELINE DEPENDENCY CHECK")
print("----------------------------------------------------------------")

# 1. Check PyTorch & CUDA
print("\n[1] Checking PyTorch & CUDA...")
try:
    print(f"   PyTorch Version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"   CUDA Available:  {cuda_available}")
    if cuda_available:
        print(f"   GPU Name:        {torch.cuda.get_device_name(0)}")
        device = "cuda"
    else:
        print("   [!] CUDA not found. Whisper will run on CPU (Slow).")
        device = "cpu"
except ImportError:
    print("   [x] PyTorch not found.")
    device = "cpu"

# 2. Check Faster-Whisper
print("\n[2] Checking Faster-Whisper...")
try:
    from faster_whisper import WhisperModel
    # Try loading a tiny model to verify backend
    print("   Loading 'tiny' model (this triggers download)...")
    # For test, we might use "tiny" or "tiny.en"
    model = WhisperModel("tiny.en", device=device, compute_type="float16" if device=="cuda" else "int8")
    print("   [+] Faster-Whisper loaded successfully.")
except Exception as e:
    print(f"   [x] Faster-Whisper Failed: {e}")

# 3. Check OpenWakeWord
print("\n[3] Checking OpenWakeWord...")
try:
    # openwakeword might not be installed yet or might fail if onnxruntime is missing
    from openwakeword.model import Model
    # OpenWakeWord auto-downloads models on first use
    print("   Loading OpenWakeWord models...")
    oww_model = Model()
    print(f"   [+] OpenWakeWord loaded. Models: {oww_model.models.keys()}")
except Exception as e:
    print(f"   [x] OpenWakeWord Failed: {e}")

print("\n----------------------------------------------------------------")
print("   CHECK COMPLETE")
print("----------------------------------------------------------------")
