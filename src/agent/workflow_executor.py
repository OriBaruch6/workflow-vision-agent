"""
Workflow executor that orchestrates the entire workflow.
"""

import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from .navigator import BrowserNavigator
from .state_capture import StateCapture
from .llm_controller import LLMController
from ..models.schemas import TaskInput, WorkflowMetadata, StateMetadata, ActionDecision
from ..storage import DatasetManager


class WorkflowExecutor:
    """Orchestrates the complete workflow execution."""
    
    def __init__(
        self,
        headless: bool = False,
        anthropic_api_key: Optional[str] = None,
    ):
        """
        Initialize workflow executor.
        
        Args:
            headless: Run browser in headless mode
            anthropic_api_key: Anthropic API key
        """
        self.headless = headless
        self.navigator = BrowserNavigator(headless=headless)
        self.llm_controller = LLMController(api_key=anthropic_api_key)
        self.state_capture: Optional[StateCapture] = None
        self.dataset_manager = DatasetManager()
        self.max_iterations = 10  
        self.low_confidence_threshold = 0.7
    
    def execute(self, task: TaskInput) -> WorkflowMetadata:
        """
        Execute a workflow task.
        
        Args:
            task: Task input with app and description
            
        Returns:
            WorkflowMetadata with results
        """
        start_time = time.time()
        workflow_name = f"{task.app}_{task.task_description.lower().replace(' ', '_')[:50]}"
        
        # Initialize browser
        self.navigator.start()
        
        try:
            # Set authentication if provided
            if task.auth_cookies:
                self.navigator.set_cookies(task.auth_cookies)
            
            # Navigate to base URL
            base_url = task.base_url or self._get_base_url(task.app)
            if not base_url:
                raise ValueError(f"No base URL found for app: {task.app}")
            
            print(f"🌐 Navigating to {base_url}")
            if not self.navigator.goto(base_url):
                raise RuntimeError(f"Failed to navigate to {base_url}")
            
            # Initialize state capture
            output_dir = self.dataset_manager.create_workflow_dir(workflow_name)
            self.state_capture = StateCapture(self.navigator.page, output_dir)
            
            # Capture initial state
            print("📸 Capturing initial state...")
            initial_state = self.state_capture.capture_full_state()
            if initial_state:
                print(f"✅ Captured initial state: {initial_state.filename}")
            
            # Main execution loop
            action_history: List[str] = []
            captured_states: List[StateMetadata] = []
            if initial_state:
                captured_states.append(initial_state)
            
            iteration = 0
            last_action: Optional[ActionDecision] = None
            
            while iteration < self.max_iterations:
                iteration += 1
                print(f"\n Iteration {iteration}/{self.max_iterations}")
                
                # Wait for page to stabilize
                self.navigator.wait_for_load_state()
                
                # Extract available elements
                elements = self.state_capture.extract_interactive_elements()
                print(f"   Found {len(elements)} interactive elements")
                
                # Get latest screenshot
                if captured_states:
                    latest_screenshot = output_dir / captured_states[-1].filename
                else:
                    # Take a new screenshot for decision
                    temp_state = self.state_capture.capture_full_state()
                    if temp_state:
                        captured_states.append(temp_state)
                        latest_screenshot = output_dir / temp_state.filename
                    else:
                        print("❌ Could not capture screenshot")
                        break
                
                # Ask Claude for next action
                print("🤖 Consulting AI for next action...")
                decision = self.llm_controller.decide_next_action(
                    task_description=task.task_description,
                    screenshot_path=latest_screenshot,
                    available_elements=elements,
                    action_history=action_history,
                    current_url=self.navigator.get_current_url(),
                )
                
                print(f"   Decision: {decision.action_type}")
                print(f"   Reasoning: {decision.reasoning}")
                print(f"   Confidence: {decision.confidence:.2f}")
                
                # Check if task is complete (multiple ways to indicate completion)
                task_complete = (
                    decision.action_type == "done" or
                    decision.task_complete or
                    decision.user_got_what_they_wanted
                )
                
                if task_complete:
                    print("✅ Task completed!")
                    if decision.user_got_what_they_wanted:
                        print("   ✅ User got what they wanted!")
                    break
                
                # Check confidence
                if decision.confidence < self.low_confidence_threshold:
                    print(f"⚠️  Low confidence ({decision.confidence:.2f}), may need human guidance")
                    # Continue anyway but note it
                
                # Execute action
                action_success = self._execute_action(decision)
                
                if action_success:
                    action_desc = self._format_action_description(decision)
                    action_history.append(action_desc)
                    print(f"   ✅ Executed: {action_desc}")
                else:
                    print(f"   ❌ Failed to execute action")
                    # Try alternative selector
                    if decision.target_selector:
                        alt_selector = self.llm_controller.get_alternative_selector(
                            decision.target_selector, elements
                        )
                        if alt_selector:
                            print(f"   🔄 Trying alternative selector: {alt_selector}")
                            decision.target_selector = alt_selector
                            action_success = self._execute_action(decision)
                
                # Capture new state if needed
                if decision.capture_state or action_success:
                    action_desc = self._format_action_description(decision)
                    new_state = self.state_capture.capture_full_state(action_taken=action_desc)
                    if new_state:
                        captured_states.append(new_state)
                        print(f"   📸 Captured new state: {new_state.filename}")
                
                last_action = decision
                
                # Small delay between iterations
                self.navigator.page.wait_for_timeout(500)
            
            # Check if we completed or timed out
            success = last_action and last_action.action_type == "done"
            if iteration >= self.max_iterations:
                print(f"⚠️  Reached max iterations ({self.max_iterations})")
                success = False
            
            duration = time.time() - start_time
            
            # Create workflow metadata
            workflow_metadata = WorkflowMetadata(
                task_description=task.task_description,
                app=task.app,
                timestamp=datetime.now(),
                success=success,
                total_states=len(captured_states),
                states=captured_states,
                error_message=None if success else "Max iterations reached or task incomplete",
                duration_seconds=duration,
            )
            
            # Save metadata
            self.dataset_manager.save_workflow_metadata(workflow_name, workflow_metadata)
            
            print(f"\n{'='*60}")
            print(f"📊 Workflow Summary:")
            print(f"   Success: {success}")
            print(f"   States captured: {len(captured_states)}")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Output: {output_dir}")
            print(f"{'='*60}")
            
            return workflow_metadata
            
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            duration = time.time() - start_time
            return WorkflowMetadata(
                task_description=task.task_description,
                app=task.app,
                timestamp=datetime.now(),
                success=False,
                total_states=len(captured_states) if 'captured_states' in locals() else 0,
                states=captured_states if 'captured_states' in locals() else [],
                error_message=str(e),
                duration_seconds=duration,
            )
        finally:
            self.navigator.close()
    
    def _execute_action(self, decision: ActionDecision) -> bool:
        """Execute an action decision."""
        if not decision.target_selector:
            return False
        
        try:
            if decision.action_type == "click":
                return self.navigator.click(decision.target_selector)
            elif decision.action_type == "type":
                if not decision.value:
                    return False
                return self.navigator.fill(decision.target_selector, decision.value)
            elif decision.action_type == "wait":
                self.navigator.page.wait_for_timeout(2000)
                return True
            elif decision.action_type == "scroll":
                self.navigator.page.evaluate("window.scrollBy(0, 500)")
                return True
            else:
                return False
        except Exception as e:
            print(f"   ⚠️  Action execution error: {e}")
            return False
    
    def _format_action_description(self, decision: ActionDecision) -> str:
        """Format action for history."""
        if decision.action_type == "click":
            return f"Click {decision.target_description or decision.target_selector}"
        elif decision.action_type == "type":
            return f"Type '{decision.value}' into {decision.target_description or decision.target_selector}"
        elif decision.action_type == "wait":
            return "Wait for page to load"
        elif decision.action_type == "scroll":
            return "Scroll down"
        else:
            return f"{decision.action_type}"
    
    def _get_base_url(self, app: str) -> Optional[str]:
        """Get base URL for app from config."""
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path("apps.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    app_config = config.get("apps", {}).get(app.lower())
                    if app_config:
                        return app_config.get("base_url")
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
        
        return None

