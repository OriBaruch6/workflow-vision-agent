"""
Test script for Disney Plus login using the new AI agent system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import from src
from src.models.schemas import TaskInput
from src.agent import WorkflowExecutor


def test_disney_plus_login():
    """Test logging in to Disney Plus."""
    print("🎬 Testing: How can I log in to my Disney Plus account?")
    print("=" * 60)
    
    task = TaskInput(
        app="disneyplus",
        task_description="How can I log in to my Disney Plus account?",
        base_url="https://www.disneyplus.com",
    )
    
    executor = WorkflowExecutor(headless=False)
    result = executor.execute(task)
    
    print(f"\n{'='*60}")
    print(f"📊 Workflow Result:")
    print(f"   Success: {'✅ Yes' if result.success else '❌ No'}")
    print(f"   States captured: {result.total_states}")
    print(f"   Duration: {result.duration_seconds:.2f}s")
    if result.error_message:
        print(f"   Error: {result.error_message}")
    
    print(f"\n📸 Captured States:")
    for i, state in enumerate(result.states, 1):
        print(f"   {i}. {state.filename}")
        if state.action_taken:
            print(f"      Action: {state.action_taken}")
        if state.is_modal:
            print(f"      ⚠️  Modal state")
        if state.is_form:
            print(f"      📝 Form state")
    
    return result.success


if __name__ == "__main__":
    test_disney_plus_login()

