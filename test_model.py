# Test with actual model
import sys
sys.path.insert(0, ".")

try:
    import ollama
    
    # Get full model info
    print("Getting model details...")
    response = ollama.list()
    models = response.get('models', [])
    
    if models:
        model = models[0]
        print(f"\nModel info:")
        for key, value in model.items():
            if key != 'details':
                print(f"  {key}: {value}")
        
        # Try to use it
        model_name = model.get('model', model.get('name', 'gemma3:4b'))
        print(f"\nTrying to generate with: {model_name}")
        
        result = ollama.generate(
            model=model_name,
            prompt="Say 'hello' in one word",
            stream=False
        )
        
        print(f"Response: {result.get('response', 'no response')[:100]}")
        print("\n[SUCCESS] Ollama working!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
