"""
Tests for browser controller.
"""

from workflow_vision_agent.browser import BrowserController


def test_browser_controller():
    """Test the browser controller."""
    controller = BrowserController(headless=True)
    
    try:
        controller.start_browser()
        assert controller.page is not None, "Page should be created"
        
        controller.go_to_url("https://example.com")
        assert "example.com" in controller.get_current_url(), "Should navigate to example.com"
        
        screenshot_path = controller.take_screenshot("test_page")
        assert screenshot_path.endswith(".png"), "Screenshot should be PNG"
        
        print("✓ Browser controller tests passed")
    finally:
        controller.close_browser()


if __name__ == "__main__":
    test_browser_controller()

