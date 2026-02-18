import asyncio
from typing import Dict, List
from .base_skill import BaseSkill

class TimeoutSkill(BaseSkill):
    name = "timeout_skill"
    keywords = {"timeout": 1.0, "crash": 1.0}
    patterns = []
    dangerous = False

    async def execute(self, text: str, context: dict):
        if "crash" in text:
            raise ValueError("Intentional Crash")
        
        # Simulate hang
        await asyncio.sleep(6) 
        return "Should not see this"
