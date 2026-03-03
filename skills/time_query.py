from .base_skill import BaseSkill # type: ignore
from datetime import datetime


class TimeQuerySkill(BaseSkill):
    name = "time_query"
    keywords = {
        "time": 0.9,
        "clock": 0.8,
        "hour": 0.6,
    }
    patterns = [
        r"what\s+time",
        r"what's\s+the\s+time",
        r"tell\s+me\s+the\s+time",
        r"current\s+time",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d")
        return f"{time_str} on {date_str}"
