
import torch # type: ignore
import sys

print(f"Python Version: {sys.version}")
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    print("SUCCESS: GPU Acceleration Enabled.")
else:
    print("FAILURE: GPU Not Detected.")
