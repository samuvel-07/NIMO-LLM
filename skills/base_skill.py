from abc import ABC, abstractmethod
from typing import List, Dict

class BaseSkill(ABC):
    name: str = ""
    keywords: Dict[str, float] = {}
    patterns: list = []
    dangerous: bool = False
    permission_level: str = "LOW"  # LOW | MEDIUM | CRITICAL

    @abstractmethod
    async def execute(self, text: str, context: dict):
        pass
