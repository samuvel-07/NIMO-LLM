
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing Brain Imports...")
try:
    from brain.orchestrator import Orchestrator  # type: ignore
    print("[OK] Successfully imported Orchestrator")
    
    orc = Orchestrator()
    print("[OK] Successfully initialized Orchestrator")
    
    if orc.llm:
        print("[OK] LLM Handler attached")
    else:
        print("[FAIL] LLM Handler missing")

except ImportError as e:
    print(f"[FAIL] Import Failed: {e}")
except Exception as e:
    print(f"[FAIL] Initialization Failed: {e}")
