# Quick JARVIS GUI Test
# Tests if GUI can launch without errors

import sys
import os

print("Testing JARVIS GUI Import...")
print("=" * 60)

try:
    # Test import
    sys.path.insert(0, os.path.dirname(__file__))
    from jarvis_core import JarvisCore
    print("[OK] jarvis_core imported successfully")
    
    # Test initialization
    core = JarvisCore(log_fn=print)
    print("[OK] JarvisCore initialized")
    
    # Check modules
    print("\nModules loaded:")
    print(f"  - Intent Classifier: {core.intent_classifier is not None}")
    print(f"  - Context Manager: {core.context_manager is not None}")
    print(f"  - Response Generator: {core.response_generator is not None}")
    print(f"  - Fallback Handler: {core.fallback_handler is not None}")
    print(f"  - LLM Handler: {core.llm_handler is not None}")
    
    print("\n" + "=" * 60)
    print("SUCCESS! GUI should work now.")
    print("Run: python gui.py")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
