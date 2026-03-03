from .base_skill import BaseSkill # type: ignore
import platform


class SystemStatusSkill(BaseSkill):
    name = "system_status"
    keywords = {
        "system": 0.7,
        "status": 0.8,
        "battery": 0.9,
        "cpu": 0.9,
        "ram": 0.8,
        "memory": 0.6,
    }
    patterns = [
        r"system\s+status",
        r"how\s+much\s+(ram|memory|cpu|battery)",
        r"check\s+(system|battery|cpu)",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        try:
            import psutil  # type: ignore

            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            ram_used = ram.used / (1024 ** 3)
            ram_total = ram.total / (1024 ** 3)
            ram_pct = ram.percent

            report = f"CPU at {cpu}%. RAM {ram_used:.1f} of {ram_total:.1f} GB ({ram_pct}%)"

            # Battery (laptop)
            battery = psutil.sensors_battery()
            if battery:
                report += f". Battery {battery.percent}%"
                if battery.power_plugged:
                    report += " (charging)"

            return report

        except ImportError:
            return f"System: {platform.system()} {platform.release()}. Install psutil for detailed stats."
        except Exception as e:
            return f"Could not read system status: {e}"
