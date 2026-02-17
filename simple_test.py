# Simple test - download and use llama3.2:3b
import sys
sys.path.insert(0, ".")

try:
    import ollama
    
    model_name = "llama3.2:3b"
    
    print(f"Checking if {model_name} is available...")
    
    try:
        # Try to generate - this will auto-pull if not available
        print(f"\nTesting generation with {model_name}...")
        print("(This may download the model if not present - ~2GB)")
        
        result = ollama.generate(
            model=model_name,
            prompt="Say hello in one word",
            stream=False
        )
        
        response_text = result.get('response', '').strip()
        print(f"\nOllama response: {response_text}")
        print("\n[SUCCESS] Ollama + JARVIS integration ready!")
        print(f"Using model: {model_name}")
        
    except Exception as e:
        if "404" in str(e):
            print(f"\nModel not found. Downloading {model_name}...")
            print("This will take a few minutes (~2GB download)")
            ollama.pull(model_name)
            print("\nDownload complete! Run test again.")
        else:
            raise
        
except Exception as e:
    print(f"Error: {e}")
