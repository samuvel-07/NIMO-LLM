
import logging

class LLMHandler:
    def __init__(self, model="llama3:8b"):
        """
        Initialize LLM handler with Ollama.
        """
        self.model = model
        self.ollama_available = False
        self.ollama = None
        
        # Try to import ollama
        try:
            import ollama # type: ignore
            self.ollama = ollama  # type: ignore
            self._check_availability()
        except ImportError:
            print("[ERROR] Ollama package not installed. Run: pip install ollama")
            self.ollama = None

    def _check_availability(self):
        """Check if Ollama server is running and model is available"""
        if not self.ollama:
            return False
        
        try:
            # Test connection by listing models
            models = self.ollama.list()  # type: ignore
            self.ollama_available = True
            
            # Check if our model is downloaded
            # API returns list of objects or dicts depending on version
            # Safely extract names
            model_names = []
            if hasattr(models, 'models'): # Object style
                 model_names = [m.model.split(':')[0] for m in models.models]
            elif isinstance(models, dict): # Dict style
                 model_names = [m.get('name', '').split(':')[0] for m in models.get('models', [])]

            base_model = self.model.split(':')[0]
            
            if base_model not in model_names:
                print(f"[WARN] Model {self.model} not found. Run: ollama pull {self.model}")
                return False
            
            print(f"[INFO] LLM Ready: {self.model}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Ollama not available: {e} (Is the server running?)")
            self.ollama_available = False
            return False

    def chat_completion(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate a response using Ollama.
        """
        if not self.ollama_available:
            return "System: LLM specific modules are unavailable."

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})

            response = self.ollama.chat(  # type: ignore
                model=self.model,
                messages=messages
            )
            
            # Extract content safely
            if hasattr(response, 'message'):
                return response.message.content
            elif isinstance(response, dict):
                return response.get('message', {}).get('content', '')
            else:
                return str(response)

        except Exception as e:
            print(f"Detailed LLM Error: {e}")
            return ""

    def chat_stream(self, prompt: str, system_prompt: str = ""):
        """
        Generate a response using Ollama and yield chunks as they stream.
        """
        if not self.ollama_available:
            yield ""
            return

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})

            response = self.ollama.chat(  # type: ignore
                model=self.model,
                messages=messages,
                stream=True
            )
            
            for chunk in response:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']

        except Exception as e:
            print(f"Detailed LLM Stream Error: {e}")
            yield ""
