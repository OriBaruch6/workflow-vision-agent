"""
Test script for Notion workflows.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.schemas import TaskInput
from src.agent import WorkflowExecutor


def test_create_database():
    """Test creating a database in Notion."""
    print("🧪 Testing: Create a database in Notion")
    
    task = TaskInput(
        app="notion",
        task_description="How do I create a database in Notion?",
    )
    
    executor = WorkflowExecutor(headless=False)
    result = executor.execute(task)
    
    print(f"\n📊 Result: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   States captured: {result.total_states}")
    print(f"   Duration: {result.duration_seconds:.2f}s")
    
    return result.success


def test_filter_database():
    """Test filtering a database view in Notion."""
    print("🧪 Testing: Filter a database view in Notion")
    
    task = TaskInput(
        app="notion",
        task_description="How do I filter a database view in Notion?",
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
    parser.add_argument("test", choices=["create_database", "filter_database", "all"])
    args = parser.parse_args()
    
    if args.test == "create_database":
        test_create_database()
    elif args.test == "filter_database":
        test_filter_database()
    elif args.test == "all":
        test_create_database()
        print("\n" + "="*60 + "\n")
        test_filter_database()

