"""
Pydantic models for data validation and type safety.
"""

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class ElementInfo(BaseModel):
    """Information about an interactive element on the page."""
    
    selector: str = Field(..., description="CSS selector for the element")
    text: Optional[str] = Field(None, description="Visible text content")
    tag: str = Field(..., description="HTML tag name")
    role: Optional[str] = Field(None, description="ARIA role if present")
    type: Optional[str] = Field(None, description="Input type if applicable")
    placeholder: Optional[str] = Field(None, description="Placeholder text if applicable")
    aria_label: Optional[str] = Field(None, description="ARIA label if present")
    is_visible: bool = Field(..., description="Whether element is visible")
    is_enabled: bool = Field(..., description="Whether element is enabled")


class StateMetadata(BaseModel):
    """Metadata for a captured UI state."""
    
    filename: str = Field(..., description="Screenshot filename")
    dom_filename: Optional[str] = Field(None, description="DOM snapshot filename")
    action_taken: Optional[str] = Field(None, description="Action that led to this state")
    has_url: bool = Field(..., description="Whether this state has a unique URL")
    url: Optional[str] = Field(None, description="URL if applicable")
    timestamp: datetime = Field(default_factory=datetime.now)
    element_count: int = Field(..., description="Number of interactive elements")
    is_modal: bool = Field(default=False, description="Whether this is a modal state")
    is_form: bool = Field(default=False, description="Whether this is a form state")


class ActionDecision(BaseModel):
    """Claude's decision about the next action to take."""
    
    action_type: Literal["click", "type", "wait", "scroll", "done"] = Field(
        ..., description="Type of action to perform"
    )
    target_selector: Optional[str] = Field(
        None, description="CSS selector for target element"
    )
    target_description: Optional[str] = Field(
        None, description="Human-readable description of target"
    )
    value: Optional[str] = Field(None, description="Value to type if action is 'type'")
    reasoning: str = Field(..., description="Claude's reasoning for this decision")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)"
    )
    capture_state: bool = Field(
        default=True, description="Whether this represents a new UI state worth capturing"
    )
    task_complete: bool = Field(
        default=False, description="Whether the task has been completed"
    )
    user_got_what_they_wanted: bool = Field(
        default=False, description="Whether the user got what they wanted"
    )


class TaskInput(BaseModel):
    """Input for a workflow task."""
    
    app: str = Field(..., description="Application name (e.g., 'linear', 'notion')")
    task_description: str = Field(
        ..., description="Description of the task to perform"
    )
    base_url: Optional[str] = Field(
        None, description="Base URL (overrides config if provided)"
    )
    auth_cookies: Optional[Dict[str, Any]] = Field(
        None, description="Authentication cookies if needed"
    )


class WorkflowMetadata(BaseModel):
    """Complete metadata for a workflow capture."""
    
    task_description: str = Field(..., description="Task that was performed")
    app: str = Field(..., description="Application name")
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = Field(..., description="Whether task completed successfully")
    total_states: int = Field(..., description="Total number of states captured")
    states: List[StateMetadata] = Field(..., description="List of captured states")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    duration_seconds: Optional[float] = Field(None, description="Total execution time")

