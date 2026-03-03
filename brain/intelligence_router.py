import requests  # type: ignore
import os
import time

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OLLAMA_URL = "http://localhost:11434/api/generate"

GROQ_ACTIVE = True
LAST_FAIL_TIME = 0


def ask_groq(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 120
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=6
    )

    r.raise_for_status()

    data = r.json()
    return data["choices"][0]["message"]["content"]


def ask_ollama(prompt):
    payload = {
        "model": "llama3:8b",
        "prompt": f"You are JARVIS, confident and concise.\nUser: {prompt}\nAssistant:",
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()["response"]


def generate_response(user_text):
    global GROQ_ACTIVE, LAST_FAIL_TIME

    messages = [
        {"role": "system", "content": "You are JARVIS. Respond clearly and concise."},
        {"role": "user", "content": user_text}
    ]

    # Auto-recovery: retry Groq after 5 minutes
    if not GROQ_ACTIVE and time.time() - LAST_FAIL_TIME > 300:
        GROQ_ACTIVE = True
        print("[INFO] Groq auto-recovery: retrying after 5 min cooldown.")

    if GROQ_ACTIVE:
        try:
            return ask_groq(messages)
        except Exception as e:
            print(f"[WARN] Groq failed: {e}. Switching to Ollama.")
            GROQ_ACTIVE = False
            LAST_FAIL_TIME = time.time()
            try:
                return ask_ollama(user_text)
            except Exception as e2:
                print(f"[ERROR] Ollama also failed: {e2}")
                return None
    else:
        try:
            return ask_ollama(user_text)
        except Exception as e:
            print(f"[ERROR] Ollama failed: {e}")
            return None
