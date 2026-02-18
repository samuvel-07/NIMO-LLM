from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Decision:
    action: str                    # EXECUTE_SKILL | CLARIFY | LLM_FALLBACK
    skill: Optional[str]
    confidence: float
    scores: Dict[str, float]
    final_score: float
    threshold: float
    safety_override: bool
    reason: str

    def to_dict(self):
        return {
            "action": self.action,
            "skill": self.skill,
            "confidence": self.confidence,
            "scores": self.scores,
            "final_score": self.final_score,
            "threshold": self.threshold,
            "safety_override": self.safety_override,
            "reason": self.reason
        }
