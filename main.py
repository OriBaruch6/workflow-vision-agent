"""
Main entry point for the AI agent system.
Can be used as CLI or to start the FastAPI server.
"""

import sys
import argparse
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.schemas import TaskInput
from src.agent import WorkflowExecutor
import uvicorn


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Web Agent System")
    parser.add_argument(
        "mode",
        choices=["cli", "server"],
        help="Run mode: 'cli' for command line, 'server' for API server",
    )
    parser.add_argument("--app", help="App name (for CLI mode)")
    parser.add_argument("--task", help="Task description (for CLI mode)")
    parser.add_argument("--url", help="Base URL (optional, for CLI mode)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host for API server")
    
    args = parser.parse_args()
    
    if args.mode == "cli":
        if not args.app or not args.task:
            print("❌ Error: --app and --task required for CLI mode")
            sys.exit(1)
        
        task = TaskInput(
            app=args.app,
            task_description=args.task,
            base_url=args.url,
        )
        
        executor = WorkflowExecutor(headless=args.headless)
        result = executor.execute(task)
        
        if result.success:
            print("\n✅ Workflow completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Workflow failed: {result.error_message}")
            sys.exit(1)
    
    elif args.mode == "server":
        print(f"🚀 Starting API server on {args.host}:{args.port}")
        uvicorn.run("src.api.app:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    main()

