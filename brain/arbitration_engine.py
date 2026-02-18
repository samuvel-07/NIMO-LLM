from .decision_schema import Decision
from .thresholds import (
    EXECUTION_THRESHOLD,
    CLARIFICATION_THRESHOLD,
    DANGEROUS_THRESHOLD,
    DANGEROUS_SKILLS
)
from .scoring.keyword_scorer import KeywordScorer
from .scoring.pattern_scorer import PatternScorer
from .scoring.context_scorer import ContextScorer

class ArbitrationEngine:

    def __init__(self, skill_registry):
        self.skill_registry = skill_registry
        self.keyword_scorer = KeywordScorer(skill_registry)
        self.pattern_scorer = PatternScorer(skill_registry)
        self.context_scorer = ContextScorer(skill_registry)

    def evaluate(self, text: str, context: dict) -> Decision:
        # Collect real scores
        scores = self._collect_scores(text, context)

        # Find best match
        if not scores:
            best_skill = None
            best_score = 0.0
            margin = 0.0
        else:
            best_skill = max(scores, key=scores.get)
            best_score = scores[best_skill]
            
            sorted_scores = sorted(scores.values(), reverse=True)
            if len(sorted_scores) > 1:
                margin = sorted_scores[0] - sorted_scores[1]
            else:
                margin = sorted_scores[0]

        safety_override = False
        action = "LLM_FALLBACK"
        threshold_used = EXECUTION_THRESHOLD
        reason = ""

        if best_score >= EXECUTION_THRESHOLD:
            # Check for dangerous skills
            if best_skill in DANGEROUS_SKILLS:
                if best_score < DANGEROUS_THRESHOLD:
                    action = "CLARIFY"
                    safety_override = True
                    threshold_used = DANGEROUS_THRESHOLD
                    reason = "Dangerous skill requires higher confidence"
                else:
                    action = "EXECUTE_SKILL"
                    reason = "Confidence above dangerous threshold"
            else:
                action = "EXECUTE_SKILL"
                reason = "Confidence above execution threshold"
            
            # Margin Check
            if action == "EXECUTE_SKILL" and margin < 0.10:
                action = "CLARIFY"
                reason = f"Ambiguous match (margin {margin:.2f} < 0.10)"

        elif best_score >= CLARIFICATION_THRESHOLD:
            action = "CLARIFY"
            threshold_used = CLARIFICATION_THRESHOLD
            reason = "Confidence in clarification range"

        else:
            action = "LLM_FALLBACK"
            reason = "Low confidence, fallback to LLM"

        return Decision(
            action=action,
            skill=best_skill,
            confidence=best_score,
            scores=scores,
            final_score=best_score,
            threshold=threshold_used,
            safety_override=safety_override,
            reason=reason
        )

    def _collect_scores(self, text: str, context: dict):
        keyword_scores = self.keyword_scorer.score(text)
        pattern_scores = self.pattern_scorer.score(text)
        context_scores = self.context_scorer.score(text, context)

        final_scores = {}

        # Assuming skill registry ensures both scorers return same keys (skills)
        # Use keyword scores as base iterator
        for skill in keyword_scores:
            base_score = (
                0.6 * keyword_scores.get(skill, 0.0) +
                0.4 * pattern_scores.get(skill, 0.0)
            )
            # Add context boost (Multiplicative)
            # context_scores returns e.g. 0.15. We do base * 1.15
            context_boost = context_scores.get(skill, 0.0)
            final_score = base_score * (1 + context_boost)
            
            final_scores[skill] = final_score

        # Normalize Scores (Relative Scoring via Max)
        # This ensures the top skill is always 1.0 (relative dominance),
        # allowing the Margin Check to handle ambiguity logic.
        max_score = max(final_scores.values()) if final_scores else 0.0
        
        # Safety: score must still be significant to be boosted?
        # User requested purely relative, but let's be careful.
        # If max_score is tiny, we might amplify noise.
        # But per instructions: "Add lightweight normalization... / max_score"
        
        if max_score > 0:
            for skill in final_scores:
                final_scores[skill] = final_scores[skill] / max_score

        return final_scores
