import time
import math

class ContextScorer:

    def __init__(self, skill_registry, decay_lambda=0.5, max_boost=0.20):
        self.skill_registry = skill_registry
        self.decay_lambda = decay_lambda
        self.max_boost = max_boost

    def update_memory(self, context: dict, executed_skill: str):
        """
        Updates the skill memory with the executed skill.
        Applies decay to all existing memories before boosting the current one.
        """
        now = time.time()
        if "skill_memory" not in context:
            context["skill_memory"] = {}
            
        memory = context["skill_memory"]

        # Decay existing memories
        for skill_name in list(memory.keys()):
            entry = memory[skill_name]
            last_updated = entry.get("last_updated", now)
            weight = entry.get("weight", 0.0)
            
            elapsed_minutes = (now - last_updated) / 60.0
            
            # Exponential decay
            decayed = weight * math.exp(-self.decay_lambda * elapsed_minutes)

            if decayed < 0.01:
                del memory[skill_name]
            else:
                memory[skill_name]["weight"] = decayed
                memory[skill_name]["last_updated"] = now

        # Boost current skill
        current_entry = memory.get(executed_skill, {"weight": 0.0, "last_updated": now})
        new_weight = current_entry["weight"] + 0.15
        
        # Cap weight
        new_weight = min(self.max_boost, new_weight)
        
        memory[executed_skill] = {
            "weight": new_weight,
            "last_updated": now
        }

    def score(self, text: str, context: dict) -> dict:
        """
        Calculates boost scores based on time-decayed memory.
        Does not mutate the stored memory, only calculates current strength.
        """
        now = time.time()
        memory = context.get("skill_memory", {})
        scores = {}

        for skill_name, entry in memory.items():
            last_updated = entry.get("last_updated", now)
            weight = entry.get("weight", 0.0)
            
            elapsed_minutes = (now - last_updated) / 60.0
            
            # Calculate current decayed weight
            decayed = weight * math.exp(-self.decay_lambda * elapsed_minutes)
            
            if decayed > 0.001:
                scores[skill_name] = min(decayed, self.max_boost)
        
        return scores
