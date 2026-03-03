"""
Text Selection Skill — Phase 6
Select text via voice commands using keyboard shortcuts
"""
from .base_skill import BaseSkill  # type: ignore
import pyautogui  # type: ignore
import re


class TextSelectionSkill(BaseSkill):
    name = "text_selection"
    keywords = {
        "select": 0.8, "select all": 0.9, "select that": 0.8,
        "select word": 0.8, "select line": 0.8,
        "select paragraph": 0.8,
    }
    patterns = [
        r"select\s+all",
        r"select\s+that",
        r"select\s+(word|line|paragraph)",
        r"select\s+(previous|next)\s+(character|word)",
        r"select\s+from\s+.+\s+to\s+.+",
        r"select\s+.+",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        clean = text.lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)

        # Select all
        if clean == "select all":
            pyautogui.hotkey('ctrl', 'a')
            return "Selected all."

        # Select that (last dictated text)
        if clean == "select that":
            pyautogui.hotkey('ctrl', 'a')  # Fallback: select all
            return "Selected."

        # Select word (double-click selects a word)
        if "select word" in clean:
            pyautogui.doubleClick()
            return "Word selected."

        # Select line
        if "select line" in clean:
            pyautogui.press('home')
            pyautogui.hotkey('shift', 'end')
            return "Line selected."

        # Select paragraph
        if "select paragraph" in clean:
            pyautogui.hotkey('ctrl', 'shift', 'up')
            return "Paragraph selected."

        # Select previous/next character
        prev_char = re.search(r'select\s+previous\s+character', clean)
        if prev_char:
            pyautogui.hotkey('shift', 'left')
            return "Previous character selected."

        next_char = re.search(r'select\s+next\s+character', clean)
        if next_char:
            pyautogui.hotkey('shift', 'right')
            return "Next character selected."

        # Select previous/next word
        prev_word = re.search(r'select\s+previous\s+word', clean)
        if prev_word:
            pyautogui.hotkey('ctrl', 'shift', 'left')
            return "Previous word selected."

        next_word = re.search(r'select\s+next\s+word', clean)
        if next_word:
            pyautogui.hotkey('ctrl', 'shift', 'right')
            return "Next word selected."

        # "select <specific text>" — use Find & Select
        select_match = re.search(r'select\s+(.+)', clean)
        if select_match:
            target = select_match.group(1).strip()
            # Use Ctrl+H (Find) to locate text
            pyautogui.hotkey('ctrl', 'f')
            pyautogui.sleep(0.3)
            pyautogui.typewrite(target, interval=0.02)
            pyautogui.press('enter')
            pyautogui.press('escape')
            return f"Selected '{target}'."

        return "What would you like me to select?"
