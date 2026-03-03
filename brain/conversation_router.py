import requests  # type: ignore
import json
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """You are JARVIS AI, a real-time voice assistant.

Rules:
1. Never execute actions directly.
2. If the user requests a system action, respond ONLY in JSON.
3. Never hallucinate skills that don't exist.
4. For normal conversation, respond naturally in plain text.
5. Be concise. Max 2 sentences unless asked for more.
6. Never say you are an AI model.

Available action intents:
- open_app (open/launch/close apps)
- window_manager (switch/minimize/maximize/snap windows)
- web_search (search google/youtube/bing)
- mouse_control (click/right click/double click/scroll)
- keyboard_control (press keys/hotkeys)
- dictation (type/dictate text)
- text_selection (select all/word/line)
- voice_control (wake/sleep/cancel)
- narrator_control (start/stop narrator)
- time_query (what time is it)
- system_status (cpu/ram/battery)
- status_report (full system report)
- shutdown_system (shutdown/restart computer)

Response formats:

Single action:
{"mode": "action", "intent": "open_app", "entity": "chrome"}

Multiple actions:
{"mode": "multi_action", "actions": [{"intent": "open_app", "entity": "chrome"}, {"intent": "time_query", "entity": null}]}

Normal conversation:
Just reply naturally in plain text. Do NOT wrap chat in JSON.
"""


def groq_stream(messages):
    """Stream tokens from Groq API."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 150
    }

    with requests.post(GROQ_URL, headers=headers, json=payload, stream=True, timeout=8) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data:"):
                    data = decoded.replace("data: ", "")
                    if data.strip() == "[DONE]":
                        break
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta


def groq_complete(messages):
    """Non-streaming Groq call — used for structured JSON responses."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "stream": False,
        "temperature": 0.3,
        "max_tokens": 150
    }

    r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=8)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def ollama_generate(prompt):
    """Fallback: local Ollama generation."""
    payload = {
        "model": "llama3:8b",
        "prompt": prompt,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()["response"]


def build_messages(user_text):
    """Build the message list with system prompt."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text}
    ]


def generate_response(user_text):
    """Stream tokens from Groq, fallback to Ollama. Used for pure chat."""
    messages = build_messages(user_text)

    try:
        for token in groq_stream(messages):
            yield token
    except Exception as e:
        print(f"[WARN] Groq streaming failed: {e}. Switching to Ollama.")
        try:
            fallback = ollama_generate(user_text)
            yield fallback
        except Exception as e2:
            print(f"[ERROR] Ollama also failed: {e2}")
            yield "I'm having trouble responding right now."


def get_structured_response(user_text):
    """Get a complete response from Groq for structured parsing.
    Returns (is_json, parsed_or_text)."""
    messages = build_messages(user_text)

    try:
        full_response = groq_complete(messages)
    except Exception as e:
        print(f"[WARN] Groq complete failed: {e}. Switching to Ollama.")
        try:
            full_response = ollama_generate(user_text)
        except Exception as e2:
            print(f"[ERROR] Ollama also failed: {e2}")
            return False, "I'm having trouble responding right now."

    # Try to parse as JSON (structured action response)
    stripped = full_response.strip()

    # Clean markdown code fences if present
    if stripped.startswith("```json"):
        stripped = stripped[7:]
    if stripped.startswith("```"):
        stripped = stripped[3:]
    if stripped.endswith("```"):
        stripped = stripped[:-3]
    stripped = stripped.strip()

    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict) and "mode" in parsed:
            return True, parsed
    except (json.JSONDecodeError, KeyError):
        pass

    # Not JSON — it's a chat response
    return False, full_response
