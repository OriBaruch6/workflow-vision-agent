"""
Dataset manager for organizing captured workflow data.
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..models.schemas import WorkflowMetadata


class DatasetManager:
    """Manages workflow dataset organization and storage."""
    
    def __init__(self, datasets_dir: Path = Path("datasets")):
        """
        Initialize dataset manager.
        
        Args:
            datasets_dir: Root directory for all datasets
        """
        self.datasets_dir = Path(datasets_dir)
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
    
    def create_workflow_dir(self, workflow_name: str) -> Path:
        """
        Create a directory for a workflow.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Path to workflow directory
        """
        # Sanitize name
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in workflow_name)
        safe_name = safe_name.replace(' ', '_').lower()
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workflow_dir = self.datasets_dir / f"{safe_name}_{timestamp}"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        return workflow_dir
    
    def save_workflow_metadata(
        self, workflow_name: str, metadata: WorkflowMetadata
    ):
        """
        Save workflow metadata to JSON file.
        
        Args:
            workflow_name: Name of the workflow
            metadata: WorkflowMetadata to save
        """
        # Find the workflow directory (most recent with this name)
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in workflow_name)
        safe_name = safe_name.replace(' ', '_').lower()
        
        # Find matching directories
        matching_dirs = list(self.datasets_dir.glob(f"{safe_name}_*"))
        if not matching_dirs:
            # Create new one
            workflow_dir = self.create_workflow_dir(workflow_name)
        else:
            # Use most recent
            workflow_dir = max(matching_dirs, key=lambda p: p.stat().st_mtime)
        
        # Save metadata
        metadata_path = workflow_dir / "metadata.json"
        
        # Convert to dict for JSON serialization
        metadata_dict = metadata.model_dump()
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata_dict, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"💾 Saved metadata to {metadata_path}")
    
    def load_workflow_metadata(self, workflow_name: str) -> Optional[WorkflowMetadata]:
        """
        Load workflow metadata.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            WorkflowMetadata or None if not found
        """
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in workflow_name)
        safe_name = safe_name.replace(' ', '_').lower()
        
        matching_dirs = list(self.datasets_dir.glob(f"{safe_name}_*"))
        if not matching_dirs:
            return None
        
        workflow_dir = max(matching_dirs, key=lambda p: p.stat().st_mtime)
        metadata_path = workflow_dir / "metadata.json"
        
        if not metadata_path.exists():
            return None
        
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return WorkflowMetadata(**data)
    
    def list_workflows(self) -> list:
        """List all captured workflows."""
        workflows = []
        for workflow_dir in self.datasets_dir.iterdir():
            if workflow_dir.is_dir():
                metadata_path = workflow_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        workflows.append({
                            "name": workflow_dir.name,
                            "app": data.get("app"),
                            "task": data.get("task_description"),
                            "success": data.get("success"),
                            "timestamp": data.get("timestamp"),
                        })
                    except Exception:
                        pass
        
        return sorted(workflows, key=lambda w: w.get("timestamp", ""), reverse=True)

