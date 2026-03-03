"""
Voice Control Skill — Phase 6
Wake/sleep/cancel/what can I say
"""
from .base_skill import BaseSkill  # type: ignore


AVAILABLE_COMMANDS = """
Available commands:
• Open/Close apps: 'Open Chrome', 'Close Notepad'
• Window control: 'Minimize', 'Maximize', 'Snap window left', 'Go to desktop'
• Mouse: 'Click', 'Right click', 'Double click', 'Move mouse right'
• Keyboard: 'Press Ctrl S', 'Press Enter', 'Undo', 'Copy', 'Paste'
• Dictation: 'Type hello world', 'Dictate meeting notes'
• Selection: 'Select all', 'Select word', 'Select line'
• Search: 'Search on Google for weather'
• System: 'System status', 'Status report', 'What time is it'
• Narrator: 'Start narrator', 'Stop narrator'
• Voice: 'Voice access sleep', 'Cancel'
""".strip()


class VoiceControlSkill(BaseSkill):
    name = "voice_control"
    keywords = {
        "voice access": 0.9, "wake up": 0.7, "sleep": 0.6,
        "what can i say": 0.9, "cancel": 0.7,
        "help": 0.5, "commands": 0.5,
    }
    patterns = [
        r"voice\s+access\s+(wake\s+up|sleep)",
        r"what\s+can\s+i\s+say",
        r"cancel",
        r"show\s+commands",
        r"help",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        clean = text.lower().strip()

        # Wake up
        if "wake up" in clean:
            # Voice pipeline handles this via wake word, but confirm
            return "I'm already listening."

        # Sleep
        if "sleep" in clean or "go to sleep" in clean:
            # Signal the pipeline to pause
            pipeline = context.get('voice_pipeline')
            if pipeline:
                pipeline.session_active = False
                pipeline.session_timeout = 0.0
            return "Going to sleep. Say 'Jarvis' to wake me."

        # Cancel
        if clean == "cancel":
            return "Cancelled."

        # What can I say / help / show commands
        if "what can i say" in clean or "help" in clean or "commands" in clean:
            print(AVAILABLE_COMMANDS)
            return "Here are the available commands."

        return "Voice control command not recognized."
