class PermissionManager:

    def __init__(self):
        self.tier_thresholds = {
            "LOW": 0.80,
            "MEDIUM": 0.85,
            "CRITICAL": 0.92
        }
        self.require_confirmation = {
            "LOW": False,
            "MEDIUM": False,
            "CRITICAL": True
        }

    def is_allowed(self, skill, confidence):
        # Default to LOW threshold if level is unknown
        required = self.tier_thresholds.get(skill.permission_level, 0.80)
        confirm_needed = self.require_confirmation.get(skill.permission_level, False)

        if confidence < required:
             return False, False, f"{skill.permission_level} permission requires {required:.2f} confidence."

        if confirm_needed:
             return True, True, "Confirmation required for critical skill."

        return True, False, None
