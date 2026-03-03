import random


class JarvisVoice:
    """Centralized personality-driven response generator.
    Tony Stark JARVIS tone — formal, confident, concise.
    Minimal speech: silent on routine, vocal on important."""

    # Skills that ALWAYS get spoken responses
    VOCAL_SKILLS = {
        "system_status", "status_report", "system_diagnostics",
        "time_query", "focus_mode", "stealth_mode",
        "strategic_mode", "voice_control", "narrator_control",
    }

    # Skills that execute silently (no speech)
    SILENT_SKILLS = {
        "open_file",
    }

    RESPONSES = {
        "open_app": [
            "{entity}",
        ],
        "time_query": [
            "The current time is {entity}.",
            "It is {entity}, sir.",
        ],
        "system_status": [
            "{entity}",
        ],
        "system_diagnostics": [
            "{entity}",
        ],
        "status_report": [
            "{entity}",
        ],
        "focus_mode": [
            "Focus mode activated. Distractions eliminated.",
        ],
        "stealth_mode": [
            "Stealth mode engaged.",
        ],
        "strategic_mode": [
            "Strategic session prepared. Tools are ready.",
        ],
        "open_file": [
            "Opening the file.",
        ],
        # Phase 6 — New skills
        "window_manager": [
            "{entity}",
        ],
        "web_search": [
            "{entity}",
        ],
        "mouse_control": [
            "{entity}",
        ],
        "keyboard_control": [
            "{entity}",
        ],
        "dictation": [
            "{entity}",
        ],
        "text_selection": [
            "{entity}",
        ],
        "voice_control": [
            "{entity}",
        ],
        "narrator_control": [
            "{entity}",
        ],
        "success_generic": [
            "Done.",
            "Executed.",
        ],
        "error": [
            "I'm afraid I cannot complete that request.",
            "That operation has failed, sir.",
            "Something went wrong. I'll look into it.",
        ],
        "clarify": [
            "I'm not entirely sure what you mean. Could you clarify?",
        ],
        "fallback": [
            "Let me think about that.",
        ],
    }

    def should_speak(self, skill: str, success: bool = True) -> bool:
        """Minimal speech governance: only speak when it matters."""
        # Always speak errors
        if not success:
            return True
        # Always speak vocal skills
        if skill in self.VOCAL_SKILLS:
            return True
        # Silent for routine skills
        if skill in self.SILENT_SKILLS:
            return False
        # Default: speak for unknown skills
        return True

    def generate(self, skill: str, entity: str = "", success: bool = True) -> str:
        """Generate a personality-driven response."""
        if not success:
            templates = self.RESPONSES.get("error", ["Something went wrong."])
        else:
            templates = self.RESPONSES.get(skill, self.RESPONSES["success_generic"])

        template = random.choice(templates)

        if entity and "{entity}" in template:
            return template.format(entity=entity.capitalize() if entity else "")
        elif "{entity}" in template:
            return template.replace("{entity}", "that")

        return template
