"""
Workflow Vision Agent
"""

__version__ = "0.1.0"

# Import main components for easy access
from workflow_vision_agent.browser import BrowserController
from workflow_vision_agent.parser import TaskParser
from workflow_vision_agent.elements import ElementFinder
from workflow_vision_agent.actions import ActionExecutor
from workflow_vision_agent.state import StateDetector, ScreenshotManager
from workflow_vision_agent.orchestrator import WorkflowOrchestrator
from workflow_vision_agent.ai import LLMClient

__all__ = ["BrowserController", "TaskParser", "ElementFinder", "ActionExecutor", "StateDetector", "ScreenshotManager", "WorkflowOrchestrator", "LLMClient"]

