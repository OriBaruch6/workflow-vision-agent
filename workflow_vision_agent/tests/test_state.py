"""
Tests for state detector and screenshot manager.
"""

from workflow_vision_agent.browser import BrowserController
from workflow_vision_agent.state import StateDetector, ScreenshotManager


def test_state_detector():
    """Test the state detector."""
    controller = BrowserController(headless=True)
    
    try:
        controller.start_browser()
        controller.go_to_url("https://example.com")
        
        detector = StateDetector(controller.page)
        detector.reset()
        
        # Test state change detection
        changed = detector.detect_state_change()
        assert isinstance(changed, bool), "Should return boolean"
        
        # Test waiting for stable state
        stable = detector.wait_for_stable_state(timeout=3000)
        assert isinstance(stable, bool), "Should return boolean"
        
        print("✓ State detector tests passed")
    finally:
        controller.close_browser()


def test_screenshot_manager():
    """Test the screenshot manager."""
    controller = BrowserController(headless=True)
    
    try:
        controller.start_browser()
        controller.go_to_url("https://example.com")
        
        manager = ScreenshotManager(controller.page)
        
        # Start workflow
        workflow_path = manager.start_workflow("test_workflow")
        assert workflow_path != "", "Should create workflow folder"
        
        # Capture a step
        screenshot_path = manager.capture_step("initial_page")
        assert screenshot_path is not None, "Should capture screenshot"
        
        # Get workflow summary
        summary = manager.get_workflow_summary()
        assert summary["total_steps"] == 1, "Should have 1 step"
        assert len(summary["screenshots"]) == 1, "Should have 1 screenshot"
        
        # End workflow
        final_summary = manager.end_workflow()
        assert final_summary["total_steps"] == 1, "Should have 1 step in final summary"
        
        print("✓ Screenshot manager tests passed")
    finally:
        controller.close_browser()


if __name__ == "__main__":
    test_state_detector()
    test_screenshot_manager()

