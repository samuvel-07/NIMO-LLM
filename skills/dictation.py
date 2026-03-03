"""
Dictation Skill — Phase 6
Voice-to-text input, spelling, correction, capitalization
"""
from .base_skill import BaseSkill  # type: ignore
import pyautogui  # type: ignore
import pyperclip  # type: ignore
import re
import time


# Track last dictated text for corrections
_last_dictated = ""


class DictationSkill(BaseSkill):
    name = "dictation"
    keywords = {
        "dictate": 0.8, "type": 0.7, "spell": 0.6,
        "correct": 0.5, "cap": 0.4, "no space": 0.5,
    }
    patterns = [
        r"dictate\s+.+",
        r"type\s+.+",
        r"spell\s+that",
        r"correct\s+(that|.+)",
        r"cap\s+\w+",
        r"no\s+space\s+.+",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        global _last_dictated
        clean = text.lower().strip()

        # "spell that" — type last word letter by letter
        if clean in ("spell that", "spell it"):
            if _last_dictated:
                last_word = _last_dictated.split()[-1]
                for char in last_word:
                    pyautogui.press(char)
                    time.sleep(0.05)
                return f"Spelled: {last_word}"
            return "Nothing to spell."

        # "correct that" or "correct <text>" — select and prepare for retyping
        if clean.startswith("correct"):
            target = clean.replace("correct that", "").replace("correct ", "").strip()
            if not target and _last_dictated:
                # Select last dictated text
                for _ in range(len(_last_dictated)):
                    pyautogui.press('backspace')
                return f"Cleared '{_last_dictated}'. Speak the correction."
            return "Nothing to correct."

        # "cap <text>" — capitalize first letter
        cap_match = re.search(r'cap\s+(.+)', clean)
        if cap_match:
            content = cap_match.group(1).strip()
            capitalized = content[0].upper() + content[1:]  # type: ignore
            pyperclip.copy(capitalized)
            pyautogui.hotkey('ctrl', 'v')
            _last_dictated = capitalized
            return f"Typed: {capitalized}"

        # "no space <text>" — type without leading space
        nospace_match = re.search(r'no\s+space\s+(.+)', clean)
        if nospace_match:
            content = nospace_match.group(1).strip()
            pyperclip.copy(content)
            pyautogui.hotkey('ctrl', 'v')
            _last_dictated = content
            return f"Typed (no space): {content}"

        # "dictate <text>" or "type <text>"
        content = text  # Use original case
        for prefix in ["dictate ", "type ", "Dictate ", "Type "]:
            if content.startswith(prefix):
                content = content[len(prefix):]
                break

        content = content.strip()
        if content:
            # Use clipboard for Unicode support
            pyperclip.copy(content)
            pyautogui.hotkey('ctrl', 'v')
            _last_dictated = content
            return f"Typed: '{content}'"

        return "What would you like me to type?"
