from typing import Dict, List
from .base_skill import BaseSkill

class CriticalSkill(BaseSkill):
    name = "critical_skill"
    keywords = {"destroy": 1.0, "system": 1.0}
    patterns = []
    dangerous = True
    permission_level = "CRITICAL"

    async def execute(self, text: str, context: dict):
        return "Critical Action Executed"
