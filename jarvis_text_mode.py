# JARVIS Text Interface - Test Smart Features Without Voice
# Use keyboard instead of microphone to test all features

import sys
sys.path.insert(0, ".")

print("=" * 70)
print("JARVIS TEXT INTERFACE - Smart Features + LLM")
print("=" * 70)
print("\nType commands instead of speaking them.")
print("All smart features work: context, intent, LLM, natural responses\n")
print("Commands: 'quit' to exit\n")
print("=" * 70)

# Create a text-mode JARVIS (skip voice initialization)
class TextJarvis:
    def __init__(self):
        # Import just the smart modules
        from intent_classifier import IntentClassifier
        from context_manager import ContextManager
        from response_generator import ResponseGenerator
        from fallback_handler import FallbackHandler
        from llm_handler import LLMHandler
        import json, os
        
        self.intent_classifier = IntentClassifier()
        self.context_manager = ContextManager()
        self.response_generator = ResponseGenerator()
        self.fallback_handler = FallbackHandler(
            self.context_manager,
            self.response_generator
        )
        self.llm_handler = LLMHandler()
        
        # Load apps
        self.apps_path = "apps.json"
        if os.path.exists(self.apps_path):
            self.apps = json.load(open(self.apps_path, "r"))
        else:
            self.apps = {}
        
        print(f"\n[OK] JARVIS initialized")
        print(f"[OK] LLM: {'Connected' if self.llm_handler.is_available() else 'Offline'}")
        print(f"[OK] Apps loaded: {len(self.apps)}")
        print()
    
    def process_command(self, raw_command):
        """Process command with smart features"""
        # Remove "jarvis" if present
        command = raw_command.lower().replace("jarvis", "").strip()
        
        # Step 1: Resolve context
        resolved = self.context_manager.resolve_reference(command)
        if resolved != command:
            print(f"[Context] '{command}' -> '{resolved}'")
        
        # Step 2: Classify intent
        classified = self.intent_classifier.classify(resolved)
        print(f"[Intent] {classified['intent']}")
        
        # Step 3: Check fallback
        fallback_response = self.fallback_handler.handle_unclear_command(
            resolved, classified
        )
        
        if fallback_response:
            print(f"[JARVIS] {fallback_response}\n")
            self.context_manager.add_interaction(
                command, classified, fallback_response, success=False
            )
            return
        
        # Step 4: Execute
        intent = classified['intent']
        entities = classified.get('entities', {})
        
        # Route to LLM or execute command
        if intent == 'conversational_query':
            if self.llm_handler.is_available():
                print("[LLM] Thinking...")
                response = self.llm_handler.generate_response(resolved)
            else:
                response = "LLM is offline. Start Ollama to enable conversations."
        elif intent == 'unknown' and len(resolved.split()) > 3:
            # Try LLM for unknown longer queries
            if self.llm_handler.is_available():
                print("[LLM] Routing to LLM...")
                response = self.llm_handler.generate_response(resolved)
            else:
                response = "I didn't understand that. Try a command like 'open chrome' or ask a question."
        else:
            # Generate natural response
            response = self.response_generator.generate(
                intent,
                success=True,
                **entities
            )
        
        # Step 5: Store in memory
        self.context_manager.add_interaction(
            command, classified, response, success=True
        )
        
        # Step 6: Display response
        print(f"[JARVIS] {response}\n")

# Initialize
jarvis = TextJarvis()

# Main loop
while True:
    try:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\n[JARVIS] Goodbye!")
            break
        
        jarvis.process_command(user_input)
        
    except KeyboardInterrupt:
        print("\n\n[JARVIS] Goodbye!")
        break
    except Exception as e:
        print(f"[ERROR] {e}\n")
