# brain/intent_router.py

class IntentRouter:
    def __init__(self):
        """
        Initialize the Intent Router.
        This will eventually load keywords, regex patterns, or a small BERT model.
        """
        self.command_keywords = [
            # App control
            "open", "close", "start", "stop", "launch", "quit", "exit",
            # Window management
            "switch", "minimize", "maximize", "restore", "snap",
            # Mouse & keyboard
            "click", "right click", "double click", "press", "move mouse",
            "scroll", "mark", "drag", "undo", "redo", "copy", "paste", "cut",
            # Dictation & text
            "type", "dictate", "spell", "correct", "select",
            # Search & system
            "search", "google", "look up",
            "turn on", "turn off", "play", "volume", "mute",
            # Narrator & voice
            "narrator", "scan mode", "voice access", "cancel", "help",
        ]

    def determine_intent(self, text):
        """
        Analyze text to determine if it's a COMMAND or CHAT.
        
        Args:
            text (str): User input text.
        
        Returns:
            dict: {
                "type": "COMMAND" | "CHAT",
                "confidence": float,
                "metadata": {} 
            }
        """
        text_lower = text.lower().strip()
        
        # 1. Simple Keyword Matching (Baseline)
        for keyword in self.command_keywords:
            if text_lower.startswith(keyword):
                return {
                    "type": "COMMAND",
                    "confidence": 0.8,
                    "metadata": {"keyword": keyword}
                }
        
        # 2. Default to CHAT
        return {
            "type": "CHAT",
            "confidence": 1.0,
            "metadata": {}
        }
