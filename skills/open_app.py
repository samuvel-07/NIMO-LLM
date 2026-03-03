from .base_skill import BaseSkill  # type: ignore
import subprocess
import webbrowser
import re


APP_MAP = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "google": "chrome",
    "browser": "chrome",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "firefox": "firefox",
    "instagram": "https://www.instagram.com",
    "twitter": "https://www.twitter.com",
    "x": "https://www.twitter.com",
    "youtube": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "spotify": "spotify",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "cmd": "cmd",
    "command prompt": "cmd",
    "terminal": "wt",
    "powershell": "powershell",
    "explorer": "explorer",
    "file explorer": "explorer",
    "settings": "ms-settings:",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "vscode": "code",
    "vs code": "code",
    "code": "code",
    "teams": "msteams",
    "slack": "slack",
    "discord": "discord",
    "task manager": "taskmgr",
    "snipping tool": "snippingtool",
}

# Maps app names to their process names for taskkill
PROCESS_MAP = {
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "firefox": "firefox.exe",
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
    "spotify": "Spotify.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "paint": "mspaint.exe",
    "teams": "ms-teams.exe",
    "slack": "slack.exe",
    "discord": "Discord.exe",
    "explorer": "explorer.exe",
    "terminal": "WindowsTerminal.exe",
    "cmd": "cmd.exe",
    "vscode": "Code.exe",
    "vs code": "Code.exe",
    "code": "Code.exe",
    "task manager": "Taskmgr.exe",
}


class OpenAppSkill(BaseSkill):
    name = "open_app"
    keywords = {
        "open": 0.3, "launch": 0.5, "start": 0.4,
        "close": 0.5, "quit": 0.5, "exit": 0.4,
        "chrome": 0.8, "notepad": 0.8, "calculator": 0.8,
    }
    patterns = [
        r"open\s+\w+", r"launch\s+\w+",
        r"close\s+\w+", r"quit\s+\w+", r"exit\s+\w+",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        clean = text.lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)

        # Detect close/quit/exit
        is_close = False
        for prefix in ["close ", "quit ", "exit ", "kill "]:
            if clean.startswith(prefix):
                clean = clean[len(prefix):]
                is_close = True
                break

        if not is_close:
            for prefix in ["open ", "launch ", "start ", "run "]:
                if clean.startswith(prefix):
                    clean = clean[len(prefix):]
                    break

        target = clean.strip()

        if is_close:
            return self._close_app(target)
        else:
            return self._open_app(target)

    def _open_app(self, target: str) -> str:
        mapped = APP_MAP.get(target, target)
        print(f"[OPEN_APP] Target: '{target}' -> '{mapped}'")

        if mapped.startswith("http") or mapped.startswith("ms-"):
            webbrowser.open(mapped)
            return f"Opening {target}."
        else:
            subprocess.Popen(f'start "" "{mapped}"', shell=True)
            return f"Launching {target}."

    def _close_app(self, target: str) -> str:
        process = PROCESS_MAP.get(target)
        if not process:
            # Try adding .exe
            process = target + ".exe"

        print(f"[CLOSE_APP] Closing: '{target}' -> '{process}'")
        try:
            subprocess.run(
                f'taskkill /IM "{process}" /F',
                shell=True, capture_output=True, timeout=5
            )
            return f"Closed {target}."
        except Exception as e:
            print(f"[CLOSE_APP] Error: {e}")
            return f"Couldn't close {target}."
