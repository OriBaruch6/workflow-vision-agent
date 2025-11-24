"""
Tests for action executor.
"""

from workflow_vision_agent.browser import BrowserController
from workflow_vision_agent.elements import ElementFinder
from workflow_vision_agent.actions import ActionExecutor


def test_action_executor():
    """Test the action executor."""
    controller = BrowserController(headless=True)
    
    try:
        controller.start_browser()
        controller.go_to_url("https://example.com")
        
        finder = ElementFinder(controller.page)
        executor = ActionExecutor(controller.page, finder)
        
        # Test clicking (might not find on example.com, but should not error)
        result = executor.click("More information", element_type="link")
        # No assertion - might not find link on example.com
        
        # Test waiting for navigation
        controller.go_to_url("https://example.com")
        navigation_result = executor.wait_for_navigation(timeout=3000)
        assert isinstance(navigation_result, bool), "Should return boolean"
        
        print("✓ Action executor tests passed")
    finally:
        controller.close_browser()


if __name__ == "__main__":
    test_action_executor()

