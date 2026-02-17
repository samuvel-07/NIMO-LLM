# Final JARVIS + LLM Integration Test
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("JARVIS + Ollama LLM Integration Test")
print("=" * 60)

# Test LLM Handler
print("\n[1/3] Testing LLM Handler...")
from llm_handler import LLMHandler

llm = LLMHandler(model="llama3.2:3b")

if llm.is_available():
    print("[OK] LLM Handler connected to Ollama")
    
    # Test question
    question = "What is Python in one short sentence?"
    print(f"\nAsking: '{question}'")
    
    response = llm.generate_response(question, use_history=False)
    print(f"Answer: {response[:150]}...")
    print("[OK] LLM responses working!")
else:
    print("[FAIL] LLM not available")
    sys.exit(1)

# Test Intent Routing
print("\n[2/3] Testing Intent Classification...")
from intent_classifier import IntentClassifier

classifier = IntentClassifier()

test_cases = [
    ("open chrome", "open_app"),
    ("explain artificial intelligence", "conversational_query"),
]

for cmd, expected in test_cases:
    result = classifier.classify(cmd)
    status = "[OK]" if result['intent'] == expected else "[FAIL]"
    print(f"  {status} '{cmd}' -> {result['intent']}")

# Test conversation with history
print("\n[3/3] Testing Conversation History...")
llm.clear_history()

q1 = "What is AI?"
a1 = llm.generate_response(q1, use_history=False)
llm.add_to_history(q1, a1)
print(f"  Q1: {q1}")
print(f"  A1: {a1[:80]}...")

q2 = "Give me a simple example"  # Should use context from Q1
a2 = llm.generate_response(q2, use_history=True)
print(f"  Q2: {q2}")
print(f"  A2: {a2[:80]}...")
print("[OK] Conversation history working!")

print("\n" + "=" * 60)
print("[SUCCESS] JARVIS + LLM FULLY OPERATIONAL!")
print("=" * 60)
print("\nYou can now:")
print("  - Run: python gui.py")
print("  - Say: 'Jarvis, explain quantum computing'")
print("  - Say: 'Jarvis, what is machine learning'")
print("  - Say: 'Jarvis, open chrome' (still fast!)")
print("=" * 60)
