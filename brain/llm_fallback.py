import requests # type: ignore
import json
from typing import Optional, Dict, Any

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"

SYSTEM_PROMPT = """
You are an intent classification engine for a voice assistant.
You are an intent classification engine for a voice assistant.
The user speaks Indian English. Understand pronunciation and phrasing variations. 
Do not misinterpret intent based on slight grammatical or vocabulary differences intrinsic to the dialect.

Return ONLY valid JSON. No explanation. No extra text.

Format:
{
  "intent": "<skill_name>",
  "entity": "<target_or_null>",
  "action": "<sub_action_or_null>",
  "confidence": <0.0-1.0>
}

Available intents:
- open_app (open/launch/close/quit apps. action: "open" or "close")
- window_manager (switch/minimize/maximize/restore/snap. action: "switch", "minimize", "maximize", "restore", "snap_left", "snap_right", "desktop", "task_switcher")
- web_search (search on google/youtube/bing. entity: the query)
- mouse_control (click/right click/double click/move mouse/scroll/mark/drag. action: "click", "right_click", "double_click", "move_left", "move_right", "move_up", "move_down", "scroll_up", "scroll_down")
- keyboard_control (press keys/hotkeys/undo/copy/paste. entity: the key combo)
- dictation (type/dictate text. entity: the text to type)
- text_selection (select all/word/line/text. action: "select_all", "select_word", "select_line")
- voice_control (wake/sleep/cancel/help)
- narrator_control (start/stop narrator, speed, scan mode)
- time_query (what time is it)
- system_status (cpu/ram/battery status)
- status_report (full system report)
- open_file (open a file)
- shutdown_system (shutdown/restart computer)
- unknown

If unsure, return:
{
  "intent": "unknown",
  "entity": null,
  "action": null,
  "confidence": 0.0
}
"""

class LLMSkillInterpreter:

    def interpret(self, text: str) -> Dict[str, Any]:
        payload = {
            "model": MODEL,
            "prompt": SYSTEM_PROMPT + "\nUser input: " + text,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_ctx": 2048
            }
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=10)
            
            if response.status_code != 200:
                print(f"[ERROR] Ollama API returned status {response.status_code}")
                return {
                    "intent": "unknown",
                    "entity": None,
                    "confidence": 0.0
                }

            data = response.json().get("response", "")
            
            # Clean potential markdown
            clean_data = data.strip()
            if clean_data.startswith("```json"):
                clean_data = clean_data[7:]
            if clean_data.startswith("```"):
                clean_data = clean_data[3:]
            if clean_data.endswith("```"):
                clean_data = clean_data[:-3]
            clean_data = clean_data.strip()

            try:
                return json.loads(clean_data)
            except json.JSONDecodeError:
                print(f"[WARN] LLM returned invalid JSON: {clean_data}")
                return {
                    "intent": "unknown",
                    "entity": None,
                    "confidence": 0.0
                }

        except Exception as e:
            print("[ERROR] LLM Error:", e)
            return {
                "intent": "unknown",
                "entity": None,
                "confidence": 0.0
            }
