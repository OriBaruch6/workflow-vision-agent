"""
Main workflow orchestrator that coordinates all components.
"""

from typing import Dict, List, Optional
from workflow_vision_agent.browser import BrowserController
from workflow_vision_agent.parser import TaskParser
from workflow_vision_agent.elements import ElementFinder
from workflow_vision_agent.actions import ActionExecutor
from workflow_vision_agent.state import StateDetector, ScreenshotManager
import re


class WorkflowOrchestrator:
    """Orchestrates the complete workflow execution."""

    def __init__(self, headless: bool = False, use_ai: bool = True):
        """
        Initialize the workflow orchestrator.
        
        Args:
            headless: Run browser in headless mode
            use_ai: Use AI for task parsing
        """
        self.headless = headless
        self.use_ai = use_ai
        
        # Components (initialized when needed)
        self.browser = None
        self.parser = None
        self.finder = None
        self.executor = None
        self.detector = None
        self.screenshot_manager = None

    def execute(self, question: str) -> Dict:
        """
        Execute a complete workflow from a question.
        
        Args:
            question: The question from Agent A (e.g., "How do I create a project in Linear?")
            
        Returns:
            Dictionary with complete workflow including screenshots and step descriptions
        """
        try:
            print(f"\n{'='*60}")
            print(f"🤖 Starting Workflow Execution")
            print(f"{'='*60}")
            print(f"Question: {question}\n")
            
            # Step 1: Understand the question
            parsed_task = self._understand_question(question)
            if not self._is_valid_task(parsed_task):
                return self._create_error_response("Invalid task: missing URL or action")
            
            print(f"✅ Understood task:")
            print(f"   App: {parsed_task.get('app_name', 'N/A')}")
            print(f"   URL: {parsed_task.get('url', 'N/A')}")
            print(f"   Action: {parsed_task.get('action', 'N/A')}")
            print(f"   Steps: {len(parsed_task.get('steps', []))} steps identified\n")
            
            # Step 2: Initialize browser and navigate
            self._initialize_components()
            self.browser.start_browser()
            self.browser.go_to_url(parsed_task['url'])
            
            # Step 3: Initialize workflow tracking
            workflow_name = f"{parsed_task.get('app_name', 'workflow')}_{parsed_task.get('action', 'task')}"
            self.screenshot_manager.start_workflow(workflow_name)
            self.detector.reset()
            
            # Step 4: Capture initial state
            self.screenshot_manager.capture_step("initial_page")
            
            # Step 5: Execute each step
            steps = parsed_task.get('steps', [])
            executed_steps = []
            
            for i, step_description in enumerate(steps, 1):
                print(f"\n📋 Step {i}/{len(steps)}: {step_description}")
                
                # Capture state before action
                before_screenshot = self.screenshot_manager.capture_step(f"before_{step_description}", step_number=i*2-1)
                
                # Execute the step
                success = self._execute_step(step_description)
                
                if not success:
                    print(f"   ⚠️  Step execution had issues, continuing...")
                
                # Wait for state to stabilize
                self.detector.wait_for_stable_state(timeout=3000)
                
                # Detect state change and capture
                if self.detector.detect_state_change(wait_time=1000):
                    after_screenshot = self.screenshot_manager.capture_step(f"after_{step_description}", step_number=i*2)
                    executed_steps.append({
                        "step_number": i,
                        "description": step_description,
                        "before_screenshot": before_screenshot,
                        "after_screenshot": after_screenshot,
                        "success": success
                    })
                    print(f"   ✅ State changed, screenshot captured")
                else:
                    # Still capture even if no change detected
                    after_screenshot = self.screenshot_manager.capture_step(f"after_{step_description}", step_number=i*2)
                    executed_steps.append({
                        "step_number": i,
                        "description": step_description,
                        "before_screenshot": before_screenshot,
                        "after_screenshot": after_screenshot,
                        "success": success
                    })
                    print(f"   ✅ Screenshot captured")
            
            # Step 6: Finalize workflow
            workflow_summary = self.screenshot_manager.end_workflow()
            
            # Step 7: Cleanup
            self.browser.close_browser()
            
            # Step 8: Return complete workflow
            result = {
                "success": True,
                "question": question,
                "parsed_task": parsed_task,
                "workflow_folder": workflow_summary.get("workflow_folder"),
                "total_steps": len(executed_steps),
                "executed_steps": executed_steps,
                "all_screenshots": workflow_summary.get("screenshots", [])
            }
            
            print(f"\n{'='*60}")
            print(f"✨ Workflow completed successfully!")
            print(f"   Total steps: {len(executed_steps)}")
            print(f"   Screenshots: {workflow_summary.get('total_steps', 0)}")
            print(f"   Folder: {workflow_summary.get('workflow_folder', 'N/A')}")
            print(f"{'='*60}\n")
            
            return result
            
        except Exception as error:
            print(f"\n❌ Error executing workflow: {error}")
            if self.browser:
                try:
                    self.browser.close_browser()
                except:
                    pass
            return self._create_error_response(str(error))

    def _understand_question(self, question: str) -> Dict:
        """Understand the question using TaskParser."""
        if not self.parser:
            self.parser = TaskParser(use_ai=self.use_ai)
        return self.parser.parse_question(question)

    def _is_valid_task(self, parsed_task: Dict) -> bool:
        """Check if task is valid."""
        if not self.parser:
            self.parser = TaskParser(use_ai=self.use_ai)
        return self.parser.is_valid_task(parsed_task)

    def _initialize_components(self):
        """Initialize all components."""
        if not self.browser:
            self.browser = BrowserController(headless=self.headless)
        
        if not self.finder:
            self.finder = ElementFinder(self.browser.page)
        
        if not self.executor:
            self.executor = ActionExecutor(self.browser.page, self.finder)
        
        if not self.detector:
            self.detector = StateDetector(self.browser.page)
        
        if not self.screenshot_manager:
            self.screenshot_manager = ScreenshotManager(self.browser.page)

    def _execute_step(self, step_description: str) -> bool:
        """
        Execute a single step based on its description.
        
        Args:
            step_description: Description of the step (e.g., "click create button")
            
        Returns:
            True if executed successfully, False otherwise
        """
        try:
            step_lower = step_description.lower()
            
            # Extract action keywords
            if "click" in step_lower or "press" in step_lower:
                # Extract what to click
                text_to_click = self._extract_target_text(step_description, ["click", "press"])
                if text_to_click:
                    # Determine element type
                    element_type = "link" if "link" in step_lower else "button"
                    return self.executor.click(text_to_click, element_type=element_type)
            
            elif "fill" in step_lower or "type" in step_lower or "enter" in step_lower:
                # Extract field and value
                field_text = self._extract_field_name(step_description)
                if field_text:
                    # For now, use placeholder text (could be enhanced with AI)
                    return self.executor.type_text(field_text, "sample_value")
            
            elif "submit" in step_lower or "save" in step_lower:
                return self.executor.submit_form()
            
            elif "select" in step_lower or "choose" in step_lower:
                # Extract dropdown and option
                field_text = self._extract_target_text(step_description, ["select", "choose"])
                option_text = self._extract_option_text(step_description)
                if field_text and option_text:
                    return self.executor.select_option(field_text, option_text)
            
            elif "navigate" in step_lower or "go to" in step_lower:
                # Navigation is usually handled before steps
                return True
            
            else:
                # Try to find and click any mentioned element
                text_to_click = self._extract_target_text(step_description, [])
                if text_to_click:
                    return self.executor.click(text_to_click, element_type="any")
            
            return False
            
        except Exception as error:
            print(f"   Error executing step: {error}")
            return False

    def _extract_target_text(self, step_description: str, action_words: List[str]) -> Optional[str]:
        """Extract the target text from step description."""
        # Remove action words
        text = step_description.lower()
        for word in action_words:
            text = text.replace(word, "")
        
        # Remove common words
        text = re.sub(r'\b(the|a|an|to|and|or|button|link|element)\b', '', text)
        text = text.strip()
        
        # Return first meaningful phrase (2+ words or single capitalized word)
        words = text.split()
        if len(words) >= 2:
            return " ".join(words[:3])  # Take first 2-3 words
        elif len(words) == 1 and words[0]:
            return words[0]
        
        return None

    def _extract_field_name(self, step_description: str) -> Optional[str]:
        """Extract field name from step description."""
        # Look for patterns like "fill name field" or "enter email"
        text = step_description.lower()
        
        # Remove action words
        text = re.sub(r'\b(fill|type|enter|input|provide)\b', '', text)
        text = re.sub(r'\b(field|input|box|form)\b', '', text)
        text = text.strip()
        
        # Return first word or phrase
        words = text.split()
        if words:
            return " ".join(words[:2])
        
        return None

    def _extract_option_text(self, step_description: str) -> Optional[str]:
        """Extract option text from step description."""
        # Look for patterns like "select option X" or "choose Y"
        text = step_description.lower()
        
        # Remove action words
        text = re.sub(r'\b(select|choose|pick|option|value)\b', '', text)
        text = text.strip()
        
        words = text.split()
        if words:
            return " ".join(words[:2])
        
        return None

    def _create_error_response(self, error_message: str) -> Dict:
        """Create an error response."""
        return {
            "success": False,
            "error": error_message,
            "executed_steps": [],
            "all_screenshots": []
        }

