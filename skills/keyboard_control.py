"""
Keyboard Control Skill — Phase 6
Press keys, hotkeys, hold/release, repeat
"""
from .base_skill import BaseSkill  # type: ignore
import pyautogui  # type: ignore
import re


# Key name aliases — maps spoken names to pyautogui key names
KEY_ALIASES = {
    "control": "ctrl", "ctrl": "ctrl",
    "alt": "alt", "alternate": "alt",
    "shift": "shift",
    "enter": "enter", "return": "enter",
    "tab": "tab",
    "escape": "esc", "esc": "esc",
    "space": "space", "spacebar": "space",
    "backspace": "backspace", "back space": "backspace",
    "delete": "delete", "del": "delete",
    "home": "home", "end": "end",
    "page up": "pageup", "page down": "pagedown",
    "up": "up", "down": "down", "left": "left", "right": "right",
    "windows": "win", "win": "win",
    "print screen": "printscreen",
    "caps lock": "capslock",
    "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
    "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
    "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
    # Letters & numbers handled dynamically
}

# Dangerous key combos that need confirmation
DANGEROUS_COMBOS = [
    ("ctrl", "alt", "delete"),
    ("alt", "f4"),
]


class KeyboardControlSkill(BaseSkill):
    name = "keyboard_control"
    keywords = {
        "press": 0.8, "type": 0.3, "key": 0.4,
        "hold": 0.6, "release": 0.6, "undo": 0.7,
        "redo": 0.7, "copy": 0.7, "paste": 0.7, "cut": 0.7,
    }
    patterns = [
        r"press\s+.+",
        r"press\s+and\s+hold\s+\w+",
        r"release\s+\w+",
        r"undo(\s+that)?",
        r"redo(\s+that)?",
        r"copy(\s+that)?",
        r"paste(\s+that)?",
        r"cut(\s+that)?",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        clean = text.lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)

        # Quick shortcuts
        if clean in ("undo", "undo that"):
            pyautogui.hotkey('ctrl', 'z')
            return "Undone."
        if clean in ("redo", "redo that"):
            pyautogui.hotkey('ctrl', 'y')
            return "Redone."
        if clean in ("copy", "copy that"):
            pyautogui.hotkey('ctrl', 'c')
            return "Copied."
        if clean in ("paste", "paste that"):
            pyautogui.hotkey('ctrl', 'v')
            return "Pasted."
        if clean in ("cut", "cut that"):
            pyautogui.hotkey('ctrl', 'x')
            return "Cut."

        # "press and hold <key>"
        hold_match = re.search(r'press\s+and\s+hold\s+(\w+)', clean)
        if hold_match:
            key = self._resolve_key(hold_match.group(1))
            if key:
                pyautogui.keyDown(key)
                return f"{key.upper()} held down."

        # "release <key>"
        release_match = re.search(r'release\s+(\w+)', clean)
        if release_match:
            key = self._resolve_key(release_match.group(1))
            if key:
                pyautogui.keyUp(key)
                return f"{key.upper()} released."

        # "press <key> <N> times"
        repeat_match = re.search(r'press\s+(.+?)\s+(\d+)\s+times?', clean)
        if repeat_match:
            key_str = repeat_match.group(1).strip()
            count = int(repeat_match.group(2))
            count = min(count, 50)  # Safety cap
            keys = self._parse_keys(key_str)
            if keys:
                for _ in range(count):
                    if len(keys) > 1:
                        pyautogui.hotkey(*keys)
                    else:
                        pyautogui.press(keys[0])
                key_display = "+".join(k.upper() for k in keys)
                return f"{key_display} pressed {count} times."

        # "press <key1> <key2>..." (hotkey or single key)
        press_match = re.search(r'press\s+(.+)', clean)
        if press_match:
            key_str = press_match.group(1).strip()
            keys = self._parse_keys(key_str)
            if keys:
                # Safety check for dangerous combos
                key_tuple = tuple(keys)
                for dangerous in DANGEROUS_COMBOS:
                    if all(k in key_tuple for k in dangerous):
                        return f"Blocked: {'+'.join(k.upper() for k in keys)} is a dangerous combination."

                if len(keys) > 1:
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(keys[0])
                key_display = "+".join(k.upper() for k in keys)
                return f"{key_display} pressed."

        return "I didn't understand the key command."

    def _resolve_key(self, spoken: str) -> str:
        """Resolve a spoken key name to pyautogui key name."""
        spoken = spoken.lower().strip()
        if spoken in KEY_ALIASES:
            return KEY_ALIASES[spoken]
        # Single letter or number
        if len(spoken) == 1:
            return spoken
        return spoken

    def _parse_keys(self, key_str: str) -> list:
        """Parse a string like 'ctrl s' or 'control shift t' into key list."""
        parts = key_str.split()
        keys = []
        for part in parts:
            resolved = self._resolve_key(part)
            if resolved:
                keys.append(resolved)
        return keys
