import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from brain.llm_fallback import LLMSkillInterpreter # type: ignore

def test_llm_fallback():
    print("Testing LLM Fallback (Requests/Ollama)...")
    
    # Instantiate interpreter
    llm = LLMSkillInterpreter()

    test_cases = [
        "Open Google Chrome",
        "Turn off the lights",
        "Play some jazz music",
        "Delete system32", # Should be safe/unknown or shutdown but filtered by permissions
        "asdfasdfasdf" # Should be unknown
    ]

    for text in test_cases:
        print(f"\nScanning: '{text}'")
        try:
            result = llm.interpret(text)
            
            if result:
                print(f"[OK] Result: {json.dumps(result, indent=2)}")
                if "intent" not in result or "confidence" not in result:
                    print("[FAIL] Missing keys in JSON")
            else:
                print("[FAIL] No result returned")
        except Exception as e:
            print(f"[FAIL] Exception during test: {e}")

if __name__ == "__main__":
    test_llm_fallback()
