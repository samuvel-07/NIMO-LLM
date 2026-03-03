# 🧠 NIMO — Neural Intelligence Machine Orchestrator

> **Real-time voice-controlled AI assistant with GPU-accelerated speech recognition, dual-engine LLM intelligence, and a Three.js holographic desktop interface.**

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Electron](https://img.shields.io/badge/Electron-33-47848F?logo=electron)
![CUDA](https://img.shields.io/badge/CUDA-GPU%20Accelerated-76B900?logo=nvidia)
![Groq](https://img.shields.io/badge/Groq-LLM%20Engine-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ⚡ Architecture

```
Wake Word ("JARVIS")
        ↓
Whisper medium.en (GPU, beam_size=1)
        ↓
Deterministic Skill Scoring (Arbitration Engine)
        ↓
   ┌────┴────┐
   │         │
Skill ≥ threshold    Score low
   │                    │
Execute locally      Groq LLM (~200ms)
                        │
                   If Groq fails
                        │
                   Ollama fallback
                        │
                   speak() → TTS
```

**Perceived delay: ~0.8–1.2 seconds** from voice to response.

---

## 🚀 Features

### Intelligence
- **Dual LLM Engine** — Groq (cloud, fast) as primary, Ollama (local) as fallback
- **5-Minute Auto-Recovery** — Groq retries automatically after cooldown
- **Deterministic-First Arbitration** — Skills execute locally before LLM is invoked
- **Voice Correction Dictionary** — Auto-fixes Indian English misrecognitions

### Voice Pipeline
- **Faster-Whisper** `medium.en` on CUDA with `float16` — GPU-accelerated STT
- **WebRTC VAD** — 300ms silence detection for instant response
- **Porcupine Wake Word** — "JARVIS" activation with 0.85 sensitivity
- **Session Window** — 10-second follow-up without re-triggering wake word
- **Force Listen** — Press `2` in the UI to bypass wake word

### Skills (18 Built-in)

| Skill | Description |
|---|---|
| `open_app` | Launch/close apps (Chrome, Instagram, YouTube, etc.) |
| `web_search` | Search Google, YouTube, Bing |
| `window_manager` | Switch/minimize/maximize/snap windows |
| `keyboard_control` | Press keys, hotkeys, shortcuts |
| `mouse_control` | Click, right-click, double-click, scroll |
| `dictation` | Type/dictate text |
| `text_selection` | Select all/word/line |
| `voice_control` | Wake/sleep/cancel commands |
| `narrator_control` | Start/stop Windows Narrator |
| `time_query` | Current time |
| `system_status` | CPU/RAM/battery info |
| `status_report` | Full system report |
| `focus_mode` | Distraction-free mode |
| `stealth_mode` | Quiet operation mode |

### Desktop UI
- **Electron** frameless window with acrylic blur
- **Three.js** 1000-particle holographic sphere
- **Real-time state visualization** — IDLE (blue), LISTENING (cyan pulse), RESPONDING (amber)
- **WebSocket** bridge between Python brain and Electron renderer
- **Global Hotkeys** — `Ctrl+Alt+Shift+J` toggle visibility, `Ctrl+Shift+S` kill switch

---

## 📦 Project Structure

```
├── brain/                    # Core AI Engine
│   ├── orchestrator.py       # Central command processor
│   ├── intelligence_router.py # Groq + Ollama dual LLM
│   ├── arbitration_engine.py # Deterministic skill scoring
│   ├── skill_registry.py     # Auto-discovery of skills
│   ├── execution_manager.py  # Safe async skill execution
│   ├── ws_publisher.py       # WebSocket bridge to UI
│   ├── input/
│   │   ├── whisper_engine.py # GPU STT with voice corrections
│   │   ├── voice_pipeline.py # Wake word → VAD → Whisper → Brain
│   │   └── stream_handler.py # Audio stream management
│   ├── personality/
│   │   └── jarvis_voice.py   # JARVIS response templates
│   ├── memory/
│   │   └── short_term_memory.py # Context tracking
│   └── utils/
│       └── tts.py            # Queue-based pyttsx3 TTS
│
├── skills/                   # Pluggable skill modules
│   ├── base_skill.py         # Skill interface
│   ├── open_app.py
│   ├── keyboard_control.py
│   ├── mouse_control.py
│   └── ... (18 skills)
│
├── desktop/                  # Electron UI
│   ├── main.js               # Window management
│   ├── core.js               # Three.js particle engine
│   ├── shaders.js            # GLSL vertex/fragment shaders
│   ├── states.js             # Visual state machine
│   └── shutdown.js           # GPU cleanup lifecycle
│
├── run_brain.py              # Entry point
├── START_DESKTOP.bat         # One-click launcher
└── requirements.txt          # Python dependencies
```

---

## 🛠️ Setup

### Prerequisites
- **Python 3.12+** with CUDA-capable GPU
- **Node.js 18+** (for Electron)
- **NVIDIA GPU** with CUDA toolkit installed
- **Groq API Key** from [console.groq.com](https://console.groq.com)

### Installation

```bash
# Clone
git clone https://github.com/samuvel-07/NIMO-LLM.git
cd NIMO-LLM

# Python environment
python -m venv .venv_gpu
.venv_gpu\Scripts\activate
pip install -r requirements.txt

# Electron
cd desktop
npm install
cd ..

# Configure
# Add your Groq API key to .env:
echo GROQ_API_KEY=your_key_here > .env
```

### Run

```bash
# Option 1: Double-click the desktop shortcut (JARVIS brain icon)
# Option 2: Run the batch file
START_DESKTOP.bat
# Option 3: Manual
python run_brain.py
```

---

## ⌨️ Controls

| Key | Action |
|---|---|
| Say **"JARVIS"** | Wake word activation |
| `2` | Force listen (bypass wake word) |
| `Ctrl+Alt+Shift+J` | Toggle UI visibility |
| `Ctrl+Shift+S` | Kill switch |
| `S` | Shutdown (when UI focused) |

---

## 🔧 Configuration

| Setting | File | Default |
|---|---|---|
| Groq API Key | `.env` | — |
| Groq Model | `intelligence_router.py` | `llama3-70b-8192` |
| Whisper Model | `whisper_engine.py` | `medium.en` (CUDA) |
| Silence Threshold | `voice_pipeline.py` | 300ms |
| TTS Rate | `tts.py` | 175 wpm |
| Wake Sensitivity | `voice_pipeline.py` | 0.85 |

---

## 📄 License

MIT License — Samuel Jayaraj

---

> *"I am JARVIS. Responding clearly and concise."*
