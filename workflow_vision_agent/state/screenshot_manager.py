"""
Manages screenshots for workflow documentation.
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from playwright.sync_api import Page


class ScreenshotManager:
    """Manages screenshots and workflow documentation."""

    def __init__(self, page: Page, base_folder: str = "screenshots"):
        """
        Initialize the screenshot manager.
        
        Args:
            page: Playwright page object
            base_folder: Base folder for storing screenshots
        """
        self.page = page
        self.base_folder = Path(base_folder)
        self.base_folder.mkdir(exist_ok=True)
        
        self.workflow_folder: Optional[Path] = None
        self.screenshots: List[Dict[str, str]] = []
        self.step_counter = 0

    def start_workflow(self, workflow_name: str) -> str:
        """
        Start a new workflow session.
        
        Args:
            workflow_name: Name for this workflow (used in folder name)
            
        Returns:
            Path to the workflow folder
        """
        try:
            # Create timestamped folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in workflow_name)
            safe_name = safe_name.replace(' ', '_').lower()
            
            self.workflow_folder = self.base_folder / f"{safe_name}_{timestamp}"
            self.workflow_folder.mkdir(exist_ok=True)
            
            self.screenshots = []
            self.step_counter = 0
            
            print(f"Started workflow: {self.workflow_folder}")
            return str(self.workflow_folder)
            
        except Exception as error:
            print(f"Error starting workflow: {error}")
            return ""

    def capture_step(self, step_description: str, step_number: Optional[int] = None) -> Optional[str]:
        """
        Capture a screenshot for a workflow step.
        
        Args:
            step_description: Description of what this step does
            step_number: Optional step number (auto-increments if not provided)
            
        Returns:
            Path to the saved screenshot, or None if failed
        """
        try:
            if not self.workflow_folder:
                # Fallback to base folder if no workflow started
                self.workflow_folder = self.base_folder
                self.workflow_folder.mkdir(exist_ok=True)
            
            # Use provided step number or auto-increment
            if step_number is None:
                self.step_counter += 1
                step_number = self.step_counter
            else:
                self.step_counter = max(self.step_counter, step_number)
            
            # Create safe filename
            safe_desc = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in step_description)
            safe_desc = safe_desc.replace(' ', '_').lower()[:50]  # Limit length
            
            filename = f"step_{step_number:03d}_{safe_desc}.png"
            screenshot_path = self.workflow_folder / filename
            
            # Take screenshot
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            
            # Record screenshot info
            screenshot_info = {
                "step_number": step_number,
                "description": step_description,
                "screenshot_path": str(screenshot_path),
                "filename": filename
            }
            self.screenshots.append(screenshot_info)
            
            print(f"Captured step {step_number}: {step_description}")
            print(f"  Screenshot: {screenshot_path}")
            
            return str(screenshot_path)
            
        except Exception as error:
            print(f"Error capturing screenshot: {error}")
            return None

    def get_workflow_summary(self) -> Dict:
        """
        Get a summary of the captured workflow.
        
        Returns:
            Dictionary with workflow information and screenshot list
        """
        return {
            "workflow_folder": str(self.workflow_folder) if self.workflow_folder else None,
            "total_steps": len(self.screenshots),
            "screenshots": self.screenshots.copy()
        }

    def get_workflow_steps(self) -> List[Dict[str, str]]:
        """
        Get list of workflow steps with screenshots.
        
        Returns:
            List of step dictionaries with description and screenshot path
        """
        return self.screenshots.copy()

    def end_workflow(self) -> Dict:
        """
        End the workflow and return final summary.
        
        Returns:
            Complete workflow summary
        """
        summary = self.get_workflow_summary()
        print(f"\nWorkflow completed: {summary['total_steps']} steps captured")
        print(f"Workflow folder: {summary['workflow_folder']}")
        return summary

