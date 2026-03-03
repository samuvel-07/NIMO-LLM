from .base_skill import BaseSkill  # type: ignore
import subprocess
import os


class FocusModeSkill(BaseSkill):
    name = "focus_mode"
    keywords = {
        "focus": 0.9,
        "concentrate": 0.7,
        "work": 0.4,
        "distraction": 0.6,
    }
    patterns = [
        r"(activate|enable|start)\s+focus\s+mode",
        r"focus\s+mode",
        r"i\s+need\s+to\s+(focus|concentrate)",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        actions = []

        # Lower volume (Windows — nircmd optional, fallback to PowerShell)
        try:
            # PowerShell volume control (no external tools needed)
            subprocess.Popen(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"',
                shell=True
            )
            actions.append("Volume lowered")
        except Exception:
            pass

        # Close known distracting apps
        for app in ["spotify", "discord"]:
            try:
                os.system(f'taskkill /IM {app}.exe /F 2>nul')
            except Exception:
                pass
        actions.append("Distracting apps closed")

        # Open coding tools
        try:
            subprocess.Popen('start "" "code"', shell=True)
            actions.append("VS Code launched")
        except Exception:
            pass

        return "Focus mode activated. " + ", ".join(actions) + "."
