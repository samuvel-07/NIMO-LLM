"""
Mouse Control Skill — Phase 6
Click, right click, double click, move mouse, mark, drag
"""
from .base_skill import BaseSkill  # type: ignore
import pyautogui  # type: ignore
import re


# Store marked position for drag operations
_mark_position = None


class MouseControlSkill(BaseSkill):
    name = "mouse_control"
    keywords = {
        "click": 0.8, "right click": 0.9, "double click": 0.9,
        "triple click": 0.9, "move mouse": 0.8, "mouse": 0.3,
        "drag": 0.7, "mark": 0.6, "scroll": 0.6,
    }
    patterns = [
        r"(right\s+)?click",
        r"double\s+click",
        r"triple\s+click",
        r"move\s+mouse\s+(left|right|up|down)",
        r"scroll\s+(up|down|left|right)",
        r"(start|stop)\s+scrolling",
        r"mark",
        r"drag",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        global _mark_position
        clean = text.lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)

        # Triple click
        if "triple click" in clean:
            pyautogui.click(clicks=3)
            return "Triple clicked."

        # Double click
        if "double click" in clean:
            pyautogui.doubleClick()
            return "Double clicked."

        # Right click
        if "right click" in clean:
            pyautogui.rightClick()
            return "Right clicked."

        # Single click
        if clean == "click" or clean.startswith("click"):
            pyautogui.click()
            return "Clicked."

        # Move mouse
        move_match = re.search(r'move\s+mouse\s+(left|right|up|down)(?:\s+(\d+))?', clean)
        if move_match:
            direction = move_match.group(1)
            distance = int(move_match.group(2)) if move_match.group(2) else 100
            dx, dy = 0, 0
            if direction == "left": dx = -distance
            elif direction == "right": dx = distance
            elif direction == "up": dy = -distance
            elif direction == "down": dy = distance
            pyautogui.moveRel(dx, dy, duration=0.2)
            return f"Mouse moved {direction} {distance}px."

        # Scroll
        scroll_match = re.search(r'scroll\s+(up|down|left|right)(?:\s+(\d+))?', clean)
        if scroll_match:
            direction = scroll_match.group(1)
            amount = int(scroll_match.group(2)) if scroll_match.group(2) else 3
            if direction == "up":
                pyautogui.scroll(amount)
            elif direction == "down":
                pyautogui.scroll(-amount)
            elif direction == "left":
                pyautogui.hscroll(-amount)
            elif direction == "right":
                pyautogui.hscroll(amount)
            return f"Scrolled {direction}."

        # Mark position for drag
        if "mark" in clean:
            _mark_position = pyautogui.position()
            return f"Position marked at ({_mark_position.x}, {_mark_position.y})."  # type: ignore

        # Drag from marked position
        if "drag" in clean:
            if _mark_position:
                current = pyautogui.position()
                pyautogui.moveTo(_mark_position.x, _mark_position.y)  # type: ignore
                pyautogui.drag(
                    current.x - _mark_position.x,  # type: ignore
                    current.y - _mark_position.y,  # type: ignore
                    duration=0.5
                )
                _mark_position = None
                return "Dragged to current position."
            else:
                return "No mark set. Say 'mark' first."

        return "I didn't catch that mouse command."
