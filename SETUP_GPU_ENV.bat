@echo off
echo ============================================================
echo   JARVIS GPU Environment Setup
echo ============================================================

echo [1/5] Creating Python 3.12 Virtual Environment (.venv_gpu)...
py -3.12 -m venv .venv_gpu

echo [2/5] Activating Virtual Environment...
call .venv_gpu\Scripts\activate

echo [3/5] Upgrading PIP...
python -m pip install --upgrade pip

echo [4/5] Installing PyTorch with CUDA 12.1...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo [5/5] Installing Dependencies...
pip install -r requirements.txt

echo ============================================================
echo   Setup Complete!
echo ============================================================
pause
