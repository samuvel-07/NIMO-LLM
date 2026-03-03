# Check available Ollama models
import sys
sys.path.insert(0, ".")

try:
    import ollama
    
    print("Checking Ollama models...")
    response = ollama.list()
    
    models = response.get('models', [])
    
    if models:
        print(f"\nFound {len(models)} model(s):")
        for m in models:
            name = m.get('name', 'unknown')
            size = m.get('size', 0) / (1024**3)  # Convert to GB
            print(f"  - {name} ({size:.1f} GB)")
    else:
        print("\nNo models found")
        print("Download one with: ollama pull llama3.2:3b")
        
except Exception as e:
    print(f"Error: {e}")
