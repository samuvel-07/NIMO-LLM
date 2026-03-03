from .base_skill import BaseSkill  # type: ignore
from datetime import datetime
import socket


class StatusReportSkill(BaseSkill):
    name = "status_report"
    keywords = {
        "status": 0.8,
        "report": 0.7,
        "diagnostics": 0.9,
        "diagnostic": 0.9,
        "health": 0.5,
    }
    patterns = [
        r"status\s+report",
        r"run\s+(system\s+)?diagnostics",
        r"system\s+check",
        r"give\s+me\s+a\s+report",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        parts = []

        # Time
        now = datetime.now().strftime("%I:%M %p")
        parts.append(f"Time is {now}")  # type: ignore

        # System stats
        try:
            import psutil  # type: ignore

            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            parts.append(f"CPU at {cpu} percent")  # type: ignore
            parts.append(f"Memory at {ram.percent} percent")  # type: ignore

            # Battery
            battery = psutil.sensors_battery()
            if battery:
                status = "charging" if battery.power_plugged else "on battery"
                parts.append(f"Battery {battery.percent} percent, {status}")  # type: ignore

            # Disk
            disk = psutil.disk_usage('/')
            parts.append(f"Disk at {disk.percent} percent")  # type: ignore

        except ImportError:
            parts.append("System stats unavailable, install psutil")

        # Network
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            parts.append("Network online")
        except (OSError, socket.timeout):
            parts.append("Network offline")

        return ". ".join(parts) + "."
