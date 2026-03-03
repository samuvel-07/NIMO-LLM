"""
Narrator Control Skill — Phase 6
Start/stop Windows Narrator, speed, scan mode
"""
from .base_skill import BaseSkill  # type: ignore
import pyautogui  # type: ignore
import subprocess
import re


class NarratorControlSkill(BaseSkill):
    name = "narrator_control"
    keywords = {
        "narrator": 0.9, "screen reader": 0.7,
        "scan mode": 0.7, "read aloud": 0.5,
    }
    patterns = [
        r"(start|stop|toggle)\s+narrator",
        r"(be\s+quiet|shut\s+up)",
        r"speak\s+(faster|slower)",
        r"scan\s+mode\s+(on|off)",
        r"read\s+(next|previous)\s+.+",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        clean = text.lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)

        # Start narrator
        if "start narrator" in clean:
            pyautogui.hotkey('win', 'ctrl', 'enter')
            return "Narrator started."

        # Stop narrator
        if "stop narrator" in clean:
            pyautogui.hotkey('win', 'ctrl', 'enter')
            return "Narrator stopped."

        # Be quiet / shut up
        if "be quiet" in clean or "shut up" in clean:
            pyautogui.press('ctrl')  # Ctrl stops Narrator speech
            return "Narrator silenced."

        # Speak faster
        if "speak faster" in clean or "faster" in clean:
            # Narrator: Caps Lock + Plus
            pyautogui.hotkey('capslock', 'plus')
            return "Narrator speaking faster."

        # Speak slower
        if "speak slower" in clean or "slower" in clean:
            # Narrator: Caps Lock + Minus
            pyautogui.hotkey('capslock', 'minus')
            return "Narrator speaking slower."

        # Scan mode on/off
        if "scan mode" in clean:
            if "on" in clean:
                pyautogui.hotkey('capslock', 'space')
                return "Scan mode enabled."
            elif "off" in clean:
                pyautogui.hotkey('capslock', 'space')
                return "Scan mode disabled."

        return "Narrator command not recognized."
