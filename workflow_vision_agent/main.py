"""
Main entry point for the workflow vision agent.
"""

from workflow_vision_agent import WorkflowOrchestrator
import sys


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python -m workflow_vision_agent.main \"<question>\"")
        print("\nExample:")
        print('  python -m workflow_vision_agent.main "How do I create a project in Linear?"')
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    
    # Create orchestrator and execute
    orchestrator = WorkflowOrchestrator(headless=False, use_ai=True)
    result = orchestrator.execute(question)
    
    if result.get("success"):
        print(f"\n✅ Workflow completed!")
        print(f"   Screenshots saved in: {result.get('workflow_folder', 'N/A')}")
    else:
        print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

