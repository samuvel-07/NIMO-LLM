from .base_skill import BaseSkill  # type: ignore
import os


class StealthModeSkill(BaseSkill):
    name = "stealth_mode"
    keywords = {
        "stealth": 0.9,
        "dark": 0.5,
        "silent": 0.6,
        "quiet": 0.5,
    }
    patterns = [
        r"(activate|enable|go)\s+stealth",
        r"stealth\s+mode",
        r"go\s+dark",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        actions = []

        # Mute system audio
        try:
            os.system('powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"')
            actions.append("Audio muted")
        except Exception:
            pass

        # Reduce brightness (Windows PowerShell)
        try:
            os.system(
                'powershell -Command "(Get-WmiObject -Namespace root/WMI '
                '-Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 20)"'
            )
            actions.append("Brightness reduced")
        except Exception:
            actions.append("Brightness unchanged")

        return "Stealth mode engaged. " + ", ".join(actions) + "."
