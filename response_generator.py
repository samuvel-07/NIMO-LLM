# response_generator.py
"""
Natural Response Generator for JARVIS
Makes responses feel human and conversational
"""
import random

class ResponseGenerator:
    def __init__(self):
        self.responses = {
            "open_app": [
                "Opening {app_name}",
                "Launching {app_name} now",
                "Got it, starting {app_name}",
                "{app_name} coming right up",
                "Sure, opening {app_name}"
            ],
            "close_app": [
                "Closing {app_name}",
                "Shutting down {app_name}",
                "Done, {app_name} is closed",
                "{app_name} terminated",
                "Alright, {app_name} is gone"
            ],
            "close_all_apps": [
                "Closing all apps now",
                "Terminating all applications",
                "Shutting everything down",
                "Okay, closing all non-essential apps"
            ],
            "play_media": [
                "Playing {media_name}",
                "Sure, playing {media_name} on YouTube",
                "Got it, {media_name} coming up",
                "Alright, searching for {media_name}"
            ],
            "time_query": [
                "The time is {time}",
                "It's {time}",
                "Right now it's {time}",
                "Currently {time}"
            ],
            "search_query": [
                "Looking up {search_term}",
                "Searching for {search_term}",
                "Let me find info on {search_term}",
                "Here's what I found about {search_term}"
            ],
            "joke": [
                "Alright, here's one",
                "Let me tell you a joke",
                "Sure, this is funny",
                "Okay, listen to this"
            ],
            "system_shutdown": [
                "Shutting down in {delay} seconds",
                "Okay, powering off in {delay} seconds",
                "Initiating shutdown. {delay} seconds to save your work",
                "System shutdown in {delay} seconds"
            ],
            "greeting": [
                "Hello! How can I help?",
                "Hey there!",
                "Hi! What do you need?",
                "Good to hear from you!"
            ],
            "status_query": [
                "All systems operational",
                "I'm doing great, ready to help",
                "Running smoothly",
                "Everything's good here"
            ],
            "success": [
                "Done",
                "All set",
                "Got it",
                "No problem",
                "Easy"
            ],
            "error": [
                "Hmm, couldn't do that",
                "Sorry, ran into an issue",
                "That didn't work",
                "Something went wrong there",
                "Failed to complete that"
            ],
            "not_understood": [
                "Didn't catch that, say it again?",
                "Not sure what you mean",
                "Could you rephrase that?",
                "Didn't understand, try again?",
                "What was that?"
            ],
            "app_not_found": [
                "App not found. You can add it via the GUI",
                "Don't know that app. Add it in settings",
                "Can't find {app_name}. Try adding it first",
                "That app isn't in my list"
            ],
            "clarification_needed": [
                "Which app did you mean?",
                "What should I {action}?",
                "Can you be more specific?",
                "Need more details on that"
            ],
            "wake_acknowledged": [
                "Yes?",
                "I'm listening",
                "What's up?",
                "Ready",
                "Go ahead"
            ]
        }
    
    def generate(self, intent, success=True, **kwargs):
        """
        Generate a natural response based on intent and context
        
        Args:
            intent: The classified intent
            success: Whether the action succeeded
            **kwargs: Variables to fill in the response (app_name, time, etc.)
        
        Returns:
            Natural language response string
        """
        if not success:
            response = random.choice(self.responses["error"])
            if "app_name" in kwargs:
                return f"{response} with {kwargs['app_name']}"
            return response
        
        # Get response template
        if intent not in self.responses:
            return random.choice(self.responses["success"])
        
        template = random.choice(self.responses[intent])
        
        # Fill in placeholders
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # If missing a required field, return generic success
            return random.choice(self.responses["success"])
    
    def get_clarification(self, intent, context=None):
        """
        Ask for clarification when command is unclear
        
        Args:
            intent: The unclear intent
            context: Additional context about what's missing
        
        Returns:
            Clarification question
        """
        if intent == "open_app" or intent == "close_app":
            return random.choice([
                "Which app?",
                "What application?",
                "Open what?",
                "Which one?"
            ])
        
        if intent == "play_media":
            return random.choice([
                "What should I play?",
                "Which song?",
                "What do you want to listen to?"
            ])
        
        if intent == "search_query":
            return random.choice([
                "Search for what?",
                "Who should I look up?",
                "What topic?"
            ])
        
        # Generic clarification
        return random.choice(self.responses["clarification_needed"])
    
    def get_confirmation(self, intent, **kwargs):
        """
        Get confirmation for sensitive actions
        
        Args:
            intent: The intent to confirm
            **kwargs: Context variables
        
        Returns:
            Confirmation question
        """
        if intent == "system_shutdown":
            return "Are you sure you want to shut down?"
        
        if intent == "close_all_apps":
            return "Close all apps? This will terminate everything"
        
        action = intent.replace("_", " ")
        if "app_name" in kwargs:
            return f"Just confirming - {action} {kwargs['app_name']}?"
        
        return f"Confirm: {action}?"
