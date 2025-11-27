"""
Test script for CNN subscribe workflow using the new AI agent system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.schemas import TaskInput
from src.agent import WorkflowExecutor


def test_cnn_subscribe():
    """Test subscribing to CNN."""
    print("📰 Testing: How to subscribe to CNN and what are the plans?")
    print("=" * 60)
    
    task = TaskInput(
        app="cnn",
        task_description="How can I subscribe to CNN and what subscription plans are available?",
        base_url="https://www.cnn.com",
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
        if state.has_url:
            print(f"      🔗 URL: {state.url}")
    
    return result.success


if __name__ == "__main__":
    test_cnn_subscribe()

