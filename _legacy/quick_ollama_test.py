# Quick Ollama Connection Test
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("Testing Ollama Connection...")
print("=" * 50)

try:
    from llm_handler import LLMHandler
    
    # Initialize with gemma3:4b (user's model)
    llm = LLMHandler(model="gemma3:4b")
    
    print(f"\n1. LLM Handler initialized")
    print(f"   Model: {llm.model}")
    
    # Check availability
    if llm.is_available():
        print(f"\n2. [SUCCESS] Ollama is running!")
        
        # List models
        models = llm.list_available_models()
        print(f"\n3. Available models:")
        for m in models:
            print(f"   - {m}")
        
        # Test response
        print(f"\n4. Testing LLM response...")
        question = "What is Python in one sentence?"
        print(f"   Q: {question}")
        
        response = llm.generate_response(question, use_history=False)
        print(f"   A: {response}")
        
        print(f"\n[SUCCESS] LLM integration working perfectly!")
        
    else:
        print(f"\n[FAIL] Ollama not available")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
