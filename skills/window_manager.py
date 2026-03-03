"""
Window Manager Skill — Phase 6
Switch, minimize, maximize, restore, snap, desktop, task switcher
"""
from .base_skill import BaseSkill  # type: ignore
import pyautogui  # type: ignore
import pygetwindow as gw  # type: ignore
import re
import time


class WindowManagerSkill(BaseSkill):
    name = "window_manager"
    keywords = {
        "switch": 0.6, "minimize": 0.8, "maximize": 0.8,
        "restore": 0.7, "snap": 0.7, "desktop": 0.6,
        "task switcher": 0.8, "alt tab": 0.8,
    }
    patterns = [
        r"switch\s+to\s+\w+",
        r"(minimize|maximize|restore)\s*(window|it|\w+)?",
        r"snap\s+(window\s+)?(to\s+)?(left|right|top|bottom)",
        r"go\s+to\s+desktop",
        r"show\s+task\s+switcher",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        clean = text.lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)

        # Go to desktop
        if "go to desktop" in clean or "show desktop" in clean:
            pyautogui.hotkey('win', 'd')
            return "Going to desktop."

        # Task switcher
        if "task switcher" in clean or "alt tab" in clean:
            pyautogui.hotkey('alt', 'tab')
            return "Task switcher opened."

        # Snap window
        snap_match = re.search(r'snap\s+(?:window\s+)?(?:to\s+)?(left|right|top|bottom|up|down)', clean)
        if snap_match:
            direction = snap_match.group(1)
            key_map = {"left": "left", "right": "right", "top": "up", "up": "up", "bottom": "down", "down": "down"}
            key = key_map.get(direction, "left")
            pyautogui.hotkey('win', key)
            return f"Window snapped to the {direction}."

        # Switch to app
        switch_match = re.search(r'switch\s+to\s+(.+)', clean)
        if switch_match:
            app_name = switch_match.group(1).strip()
            return self._focus_window(app_name)

        # Minimize/Maximize/Restore
        for action in ["minimize", "maximize", "restore"]:
            if action in clean:
                # Extract optional app name
                target = re.sub(rf'{action}\s*(window|it)?\s*', '', clean).strip()
                return self._window_action(action, target if target else None)

        return "I'm not sure what window action you want."

    def _focus_window(self, app_name: str) -> str:
        """Find and focus a window by name."""
        windows = gw.getWindowsWithTitle('')  # type: ignore
        for win in windows:
            if app_name in win.title.lower() and win.title.strip():  # type: ignore
                try:
                    if win.isMinimized:  # type: ignore
                        win.restore()  # type: ignore
                    win.activate()  # type: ignore
                    return f"Switched to {win.title}."  # type: ignore
                except Exception:
                    # Fallback: use Alt+Tab approach
                    pass
        return f"No window found for '{app_name}'."

    def _window_action(self, action: str, target: str = None) -> str:  # type: ignore
        """Perform minimize/maximize/restore on a window."""
        if target:
            windows = gw.getWindowsWithTitle('')  # type: ignore
            for win in windows:
                if target in win.title.lower() and win.title.strip():  # type: ignore
                    try:
                        if action == "minimize":
                            win.minimize()  # type: ignore
                        elif action == "maximize":
                            win.maximize()  # type: ignore
                        elif action == "restore":
                            win.restore()  # type: ignore
                        return f"{win.title} {action}d."  # type: ignore
                    except Exception:
                        pass
            return f"No window found for '{target}'."
        else:
            # Act on current window
            if action == "minimize":
                pyautogui.hotkey('win', 'down')
            elif action == "maximize":
                pyautogui.hotkey('win', 'up')
            elif action == "restore":
                pyautogui.hotkey('win', 'down')
            return f"Window {action}d."
