from .base_skill import BaseSkill


class OpenFileSkill(BaseSkill):
    name = "open_file"
    keywords = {
        "open": 0.3, 
        "file": 0.7, 
        "document": 0.9
    }
    patterns = [r"open\s+(file|document)"]
    dangerous = False

    async def execute(self, text: str, context: dict):
        return f"Pretending to open a file: {text}"
