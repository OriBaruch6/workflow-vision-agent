"""
Workflow Vision Agent
"""

__version__ = "0.1.0"

# Import main components for easy access
from workflow_vision_agent.browser import BrowserController
from workflow_vision_agent.parser import TaskParser
from workflow_vision_agent.elements import ElementFinder

__all__ = ["BrowserController", "TaskParser", "ElementFinder"]

