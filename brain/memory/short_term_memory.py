from collections import deque
import time
import re
from typing import Optional


class ShortTermMemory:
    """Tracks last N commands for contextual understanding."""

    def __init__(self, size: int = 5):
        self.history: deque = deque(maxlen=size)
        self.last_skill: Optional[str] = None
        self.last_entity: Optional[str] = None
        self.last_timestamp: Optional[float] = None

    def update(self, skill: str, entity: str):
        """Record a successful execution."""
        self.history.append({
            "skill": skill,
            "entity": entity,
            "time": time.time()
        })
        self.last_skill = skill
        self.last_entity = entity
        self.last_timestamp = time.time()

    def get_last(self):
        """Return (last_skill, last_entity) or (None, None)."""
        return self.last_skill, self.last_entity

    def get_context_summary(self) -> str:
        """Return a one-line summary for LLM context injection."""
        if not self.history:
            return ""
        recent = list(self.history)[-3:]  # type: ignore
        parts = [f"{h['skill']}({h['entity']})" for h in recent if h.get("entity")]
        return "Recent: " + ", ".join(parts) if parts else ""

    @staticmethod
    def extract_entity(text: str, skill_name: str) -> str:
        """Pull the entity/target from raw user text."""
        clean: str = text.lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)

        # Remove command words
        for prefix in ["open ", "launch ", "start ", "run ",
                        "what ", "whats ", "tell me ", "check "]:
            if clean.startswith(prefix):  # type: ignore
                clean = clean[len(prefix):]  # type: ignore
                break

        return clean.strip()  # type: ignore
