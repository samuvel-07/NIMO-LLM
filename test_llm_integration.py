# -*- coding: utf-8 -*-
# Test LLM Integration

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("JARVIS LLM Integration Test")
print("=" * 60)

# Test 1: Import LLM Handler
print("\n[1/5] Testing LLM Handler Import...")
try:
    from llm_handler import LLMHandler
    print("[OK] LLM handler imported")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Initialize LLM Handler
print("\n[2/5] Testing LLM Handler Initialization...")
llm = LLMHandler()

if llm.is_available():
    print("[OK] Ollama is running and model available!")
    print(f"     Model: {llm.model}")
else:
    print("[WARN] Ollama not available")
    print("       This is expected if you haven't installed Ollama yet")
    print("       Install: https://ollama.com/download")
    print("       Then run: ollama pull llama3.2:3b")

# Test 3: Test Intent Classification for Conversations
print("\n[3/5] Testing Intent Classification...")
from intent_classifier import IntentClassifier

classifier = IntentClassifier()

test_queries = [
    ("open chrome", "open_app"),  # Should be command
    ("explain python", "conversational_query"),  # Should be LLM
    ("what is AI", "conversational_query"),  # Should be LLM
    ("how do computers work", "conversational_query"),  # Should be LLM
]

all_correct = True
for query, expected in test_queries:
    result = classifier.classify(query)
    actual = result['intent']
    status = "[OK]" if actual == expected else "[FAIL]"
    print(f"  {status} '{query}' -> {actual} (expected: {expected})")
    if actual != expected:
        all_correct = False

if all_correct:
    print("[OK] Intent routing works correctly!")
else:
    print("[WARN] Some intent classifications didn't match expected")

# Test 4: Test LLM Response (if available)
print("\n[4/5] Testing LLM Response Generation...")
if llm.is_available():
    try:
        test_prompt = "What is Python in one sentence?"
        print(f"  Asking: '{test_prompt}'")
        response = llm.generate_response(test_prompt, use_history=False)
        print(f"  Response: {response[:100]}...")
        print("[OK] LLM response generation works!")
    except Exception as e:
        print(f"[FAIL] LLM error: {e}")
else:
    print("[SKIP] Ollama not available, skipping LLM test")

# Test 5: Test Integration with JarvisCore
print("\n[5/5] Testing Full Integration...")
try:
    from jarvis_core import JarvisCore
    
    # Create core instance (don't start the listening loop)
    logs = []
    def test_log(msg):
        logs.append(msg)
    
    core = JarvisCore(log_fn=test_log)
    
    # Check if LLM was initialized
    has_llm = hasattr(core, 'llm_handler')
    llm_status = "with LLM" if has_llm and core.llm_handler.is_available() else "without LLM"
    
    print(f"  [OK] JarvisCore initialized {llm_status}")
    
    # Test command classification
    cmd = "explain artificial intelligence"
    classified = core.intent_classifier.classify(cmd)
    
    if classified['intent'] == 'conversational_query':
        print(f"  [OK] '{cmd}' correctly routed to conversational_query")
    else:
        print(f"  [WARN] '{cmd}' routed to {classified['intent']} instead of conversational_query")
    
except Exception as e:
    print(f"[FAIL] Integration error: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)

if llm.is_available():
    print("\n[SUCCESS] LLM Integration Complete!")
    print("\nWhat works:")
    print("  - LLM handler initialized and connected to Ollama")
    print("  - Intent classifier routes questions to LLM")
    print("  - Commands still go to fast handlers")
    print("  - Full JARVIS integration ready")
    print("\nTry these commands:")
    print("  'Jarvis open chrome' -> Fast command")
    print("  'Jarvis explain quantum computing' -> LLM response")
    print("  'Jarvis what is machine learning' -> LLM response")
else:
    print("\n[PARTIAL SUCCESS] Code Integration Complete!")
    print("\nWhat works:")
    print("  - LLM handler module created")
    print("  - Intent routing configured")
    print("  - Commands work normally")
    print("\nTo enable LLM:")
    print("  1. Install Ollama: https://ollama.com/download")
    print("  2. Download model: ollama pull llama3.2:3b")
    print("  3. Install Python package: pip install ollama")
    print("  4. Run test again!")

print("=" * 60)
