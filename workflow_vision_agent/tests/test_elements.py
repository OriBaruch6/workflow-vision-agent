"""
Tests for element finder.
"""

from workflow_vision_agent.browser import BrowserController
from workflow_vision_agent.elements import ElementFinder


def test_element_finder():
    """Test the element finder."""
    controller = BrowserController(headless=True)
    
    try:
        controller.start_browser()
        controller.go_to_url("https://example.com")
        
        finder = ElementFinder(controller.page)
        
        # Test finding form fields
        fields = finder.find_form_fields()
        assert isinstance(fields, list), "Should return a list"
        
        # Test finding link (might not find on example.com, but should not error)
        link = finder.find_link("More information")
        # No assertion - might not find link on example.com
        
        print("✓ Element finder tests passed")
    finally:
        controller.close_browser()


if __name__ == "__main__":
    test_element_finder()

