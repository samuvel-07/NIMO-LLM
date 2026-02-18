import time

class ConfirmationManager:

    def __init__(self, timeout_seconds=30):
        self.timeout = timeout_seconds

    def create_pending(self, context, skill_name, payload):
        context["confirmation_state"] = {
            "pending": True,
            "skill": skill_name,
            "payload": payload,
            "expires_at": time.time() + self.timeout
        }

    def is_pending(self, context):
        state = context.get("confirmation_state", {})
        return state.get("pending", False)

    def is_expired(self, context):
        state = context.get("confirmation_state", {})
        if not state.get("pending", False):
            return False
        return time.time() > state.get("expires_at", 0)

    def clear(self, context):
        context["confirmation_state"] = {
            "pending": False,
            "skill": None,
            "payload": None,
            "expires_at": None
        }

    def get_pending(self, context):
        return context.get("confirmation_state", {})
