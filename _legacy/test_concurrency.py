import asyncio
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def stress_test():
    print("Initializing Orchestrator for Stress Test...")
    orchestrator = Orchestrator()
    context = {}

    print("\n--- Starting Concurrent Requests ---")
    start_time = time.time()
    
    # Simulate 3 inputs arriving simultaneously
    # 1. 'open chrome' -> Execution (starts memory)
    # 2. 'open document' -> Execution (updates memory)
    # 3. 'open' -> Clarify (reads memory)
    
    # Without locking, 'open' might run before 'open chrome' finishes updating memory.
    # With locking, they should finish sequentially.
    
    tasks = [
        orchestrator.handle_input("open chrome", context),
        orchestrator.handle_input("open document", context),
        orchestrator.handle_input("open", context)
    ]
    
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    print(f"\n--- Finished in {duration:.4f}s ---")
    
    for i, res in enumerate(results):
        print(f"Result {i+1}: {str(res)[:100]}...") # Truncate long output

    # Verify context integrity
    print("\n--- Context Integrity Check ---")
    if "skill_memory" in context:
        print(f"Memory keys: {list(context['skill_memory'].keys())}")
        # Both open_app and open_file should be in memory if both executed successfully
    else:
        print("Memory missing!")

if __name__ == "__main__":
    asyncio.run(stress_test())
