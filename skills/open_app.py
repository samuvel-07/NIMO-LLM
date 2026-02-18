from .base_skill import BaseSkill


class OpenAppSkill(BaseSkill):
    name = "open_app"
    keywords = {
        "open": 0.3,
        "launch": 0.5,
        "chrome": 0.8
    }
    patterns = [r"open\s+\w+"]
    dangerous = False

    async def execute(self, text: str, context: dict):
        return f"Pretending to open app based on: {text}"
