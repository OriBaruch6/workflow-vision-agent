"""
FastAPI application with endpoints for workflow execution.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import os

from ..models.schemas import TaskInput, WorkflowMetadata
from ..agent import WorkflowExecutor

app = FastAPI(
    title="AI Web Agent System",
    description="Automatically navigate web applications and capture UI workflow screenshots",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Web Agent System",
        "version": "1.0.0",
        "endpoints": {
            "execute": "/api/execute",
            "health": "/health",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
    return {
        "status": "healthy",
        "anthropic_api_key_set": api_key_set,
    }


@app.post("/api/execute", response_model=WorkflowMetadata)
async def execute_workflow(
    task: TaskInput,
    headless: bool = False,
    anthropic_api_key: Optional[str] = None,
) -> WorkflowMetadata:
    """
    Execute a workflow task.
    
    Args:
        task: Task input with app and description
        headless: Run browser in headless mode
        anthropic_api_key: Override API key (optional)
    
    Returns:
        WorkflowMetadata with results
    """
    try:
        executor = WorkflowExecutor(
            headless=headless,
            anthropic_api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"),
        )
        
        result = executor.execute(task)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows")
async def list_workflows():
    """List all captured workflows."""
    from ..storage import DatasetManager
    
    manager = DatasetManager()
    workflows = manager.list_workflows()
    
    return {"workflows": workflows, "total": len(workflows)}


@app.get("/api/workflows/{workflow_name}")
async def get_workflow(workflow_name: str):
    """Get details of a specific workflow."""
    from ..storage import DatasetManager
    
    manager = DatasetManager()
    metadata = manager.load_workflow_metadata(workflow_name)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return metadata.model_dump()

