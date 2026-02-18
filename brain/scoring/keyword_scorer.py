class KeywordScorer:

    def __init__(self, skill_registry):
        self.skill_registry = skill_registry

    def score(self, text: str) -> dict:
        text = text.lower()
        scores = {}

        for skill in self.skill_registry.get_all_skills():
            try:
                keywords = skill.keywords
                # Using weighted sum instead of count
                score = sum(weight for word, weight in keywords.items() if word in text)
                
                # Cap score at 1.0
                scores[skill.name] = min(1.0, score)
            except AttributeError:
                # Fallback if skill uses old list format (for backward compatibility during migration)
                scores[skill.name] = 0.0

        return scores
