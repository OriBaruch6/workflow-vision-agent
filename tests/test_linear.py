"""
Test script for Linear workflows.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.schemas import TaskInput
from src.agent import WorkflowExecutor


def test_create_project():
    """Test creating a project in Linear."""
    print("🧪 Testing: Create a project in Linear")
    
    task = TaskInput(
        app="linear",
        task_description="How do I create a project in Linear?",
    )
    
    executor = WorkflowExecutor(headless=False)
    result = executor.execute(task)
    
    print(f"\n📊 Result: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   States captured: {result.total_states}")
    print(f"   Duration: {result.duration_seconds:.2f}s")
    
    return result.success


def test_filter_issues():
    """Test filtering issues in Linear."""
    print("🧪 Testing: Filter issues in Linear")
    
    task = TaskInput(
        app="linear",
        task_description="How do I filter issues in Linear?",
    )
    
    executor = WorkflowExecutor(headless=False)
    result = executor.execute(task)
    
    print(f"\n📊 Result: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   States captured: {result.total_states}")
    print(f"   Duration: {result.duration_seconds:.2f}s")
    
    return result.success


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("test", choices=["create_project", "filter_issues", "all"])
    args = parser.parse_args()
    
    if args.test == "create_project":
        test_create_project()
    elif args.test == "filter_issues":
        test_filter_issues()
    elif args.test == "all":
        test_create_project()
        print("\n" + "="*60 + "\n")
        test_filter_issues()

