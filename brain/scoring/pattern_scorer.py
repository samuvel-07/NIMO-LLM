import re

class PatternScorer:

    def __init__(self, skill_registry):
        self.skill_registry = skill_registry

    def score(self, text: str) -> dict:
        scores = {}

        for skill in self.skill_registry.get_all_skills():
            # Safely get patterns, defaulting to empty list
            patterns = getattr(skill, "patterns", [])
            
            # Check if any pattern matches the input text
            match_found = any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

            scores[skill.name] = 1.0 if match_found else 0.0

        return scores
