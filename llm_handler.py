# llm_handler.py
"""
Local LLM Handler for JARVIS
Manages Ollama integration for conversational AI responses
"""

class LLMHandler:
    def __init__(self, model="llama3.2:3b", log_fn=print):
        """
        Initialize LLM handler with Ollama
        
        Args:
            model: Model name to use (default: llama3.2:3b - fast and light)
            log_fn: Logging function
        """
        self.model = model
        self.log = log_fn
        self.conversation_history = []
        self.max_history = 5  # Keep last 5 exchanges for context
        self.ollama_available = False
        
        # Try to import ollama
        try:
            import ollama
            self.ollama = ollama
            self._check_availability()
        except ImportError:
            self.log("Ollama package not installed. Run: pip install ollama")
            self.ollama = None
    
    def _check_availability(self):
        """Check if Ollama server is running and model is available"""
        if not self.ollama:
            return False
        
        try:
            # Test connection by listing models
            models = self.ollama.list()
            self.ollama_available = True
            
            # Check if our model is downloaded
            model_names = [m.get('name', '').split(':')[0] for m in models.get('models', [])]
            base_model = self.model.split(':')[0]
            
            if base_model not in model_names:
                self.log(f"Model {self.model} not found. Run: ollama pull {self.model}")
                return False
            
            self.log(f"LLM ready: {self.model}")
            return True
            
        except Exception as e:
            self.log(f"Ollama not available: {e}")
            self.log("Make sure Ollama is installed and running")
            self.ollama_available = False
            return False
    
    def is_available(self):
        """Check if LLM is ready to use"""
        if not self.ollama_available:
            self._check_availability()
        return self.ollama_available
    
    def generate_response(self, prompt, use_history=True, stream=False):
        """
        Generate LLM response for given prompt
        
        Args:
            prompt: User's question/prompt
            use_history: Include conversation history for context
            stream: Stream response (for future real-time display)
        
        Returns:
            str: LLM generated response
        """
        if not self.is_available():
            raise Exception("LLM not available. Install Ollama and download model.")
        
        # Build full prompt with history
        if use_history and self.conversation_history:
            context = self._build_context_prompt()
            full_prompt = f"{context}\n\nUser: {prompt}\nJARVIS:"
        else:
            full_prompt = f"You are JARVIS, a helpful desktop voice assistant. Be brief and conversational.\n\nUser: {prompt}\nJARVIS:"
        
        try:
            # Generate response using Ollama
            response = self.ollama.generate(
                model=self.model,
                prompt=full_prompt,
                stream=stream
            )
            
            # Extract text from response (handle both dict and object)
            if hasattr(response, 'response'):
                # Response is an object
                answer = response.response.strip()
            elif isinstance(response, dict):
                # Response is a dict
                answer = response.get('response', '').strip()
            else:
                # Fallback
                answer = str(response).strip()
            
            return answer
            
        except Exception as e:
            self.log(f"LLM generation error: {e}")
            raise
    
    def _build_context_prompt(self):
        """Build conversation context from history"""
        context_lines = ["You are JARVIS, a helpful desktop voice assistant. Previous conversation:"]
        
        for exchange in self.conversation_history[-self.max_history:]:
            context_lines.append(f"User: {exchange['user']}")
            context_lines.append(f"JARVIS: {exchange['assistant']}")
        
        return "\n".join(context_lines)
    
    def add_to_history(self, user_msg, assistant_msg):
        """
        Add exchange to conversation history
        
        Args:
            user_msg: What the user said
            assistant_msg: What JARVIS responded
        """
        self.conversation_history.append({
            "user": user_msg,
            "assistant": assistant_msg
        })
        
        # Keep only last max_history exchanges
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.log("Conversation history cleared")
    
    def download_model(self, model_name):
        """
        Download a new model
        
        Args:
            model_name: Name of model to download (e.g., "llama3.2:3b")
        
        Returns:
            bool: Success status
        """
        if not self.ollama:
            self.log("Ollama package not installed")
            return False
        
        try:
            self.log(f"Downloading model: {model_name} (this may take a while...)")
            self.ollama.pull(model_name)
            self.log(f"Model {model_name} downloaded successfully")
            return True
        except Exception as e:
            self.log(f"Failed to download model: {e}")
            return False
    
    def list_available_models(self):
        """
        List all downloaded models
        
        Returns:
            list: List of model names
        """
        if not self.ollama:
            return []
        
        try:
            response = self.ollama.list()
            models = response.get('models', [])
            return [m.get('name', 'unknown') for m in models]
        except Exception as e:
            self.log(f"Failed to list models: {e}")
            return []
    
    def switch_model(self, model_name):
        """
        Switch to a different model
        
        Args:
            model_name: Name of model to switch to
        
        Returns:
            bool: Success status
        """
        available = self.list_available_models()
        
        if model_name in available:
            self.model = model_name
            self.log(f"Switched to model: {model_name}")
            self.clear_history()  # Clear history when switching models
            return True
        else:
            self.log(f"Model {model_name} not found. Available: {available}")
            return False
    
    def get_model_info(self):
        """Get current model information"""
        return {
            "current_model": self.model,
            "available": self.ollama_available,
            "history_size": len(self.conversation_history),
            "max_history": self.max_history
        }
