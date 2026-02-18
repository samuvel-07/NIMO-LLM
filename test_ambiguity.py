import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def test():
    print("Initializing Orchestrator...")
    orchestrator = Orchestrator()
    
    test_cases = [
        "open chrome",
        "open document",
        "open file",
        "open"
    ]

    print("\nStarting Ambiguity Tests...\n")
    
    for text in test_cases:
        print(f"--- Input: '{text}' ---")
        result = await orchestrator.handle_input(text, {})
        
        # Handle different return types (Decision vs Execution Output)
        if hasattr(result, "action"):
            decision = result
            print(f"Action: {decision.action}")
            print(f"Reason: {decision.reason}")
            print(f"Best Skill: {decision.skill} ({decision.confidence:.2f})")
            
            scores = decision.scores
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            print("Top Scores:")
            for skill, score in sorted_scores[:3]:
                 print(f"  - {skill}: {score:.2f}")

            if len(sorted_scores) > 1:
                margin = sorted_scores[0][1] - sorted_scores[1][1]
                print(f"Margin: {margin:.2f}")
        else:
            print(f"Action: EXECUTION_COMPLETE")
            print(f"Output: {result}")
        
        print("")

if __name__ == "__main__":
    asyncio.run(test())
