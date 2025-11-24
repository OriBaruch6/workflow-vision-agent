"""
Detects UI state changes to know when to capture screenshots.
"""

from typing import Optional
from playwright.sync_api import Page


class StateDetector:
    """Detects when the UI state has changed significantly."""

    def __init__(self, page: Page):
        """
        Initialize the state detector.
        
        Args:
            page: Playwright page object
        """
        self.page = page
        self.last_url = None
        self.last_dom_hash = None

    def detect_state_change(self, wait_time: int = 1000) -> bool:
        """
        Detect if the UI state has changed significantly.
        
        Args:
            wait_time: Time to wait in milliseconds for UI to settle after action
            
        Returns:
            True if state changed, False otherwise
        """
        try:
            # Wait for UI to settle
            self.page.wait_for_timeout(wait_time)
            
            # Check URL change
            current_url = self.page.url
            url_changed = current_url != self.last_url
            if url_changed:
                self.last_url = current_url
                return True
            
            # Check DOM changes (simple hash of page content)
            current_dom_hash = self._get_dom_hash()
            dom_changed = current_dom_hash != self.last_dom_hash
            if dom_changed:
                self.last_dom_hash = current_dom_hash
                return True
            
            return False
            
        except Exception as error:
            print(f"Error detecting state change: {error}")
            return False

    def _get_dom_hash(self) -> str:
        """
        Get a simple hash of the page DOM to detect changes.
        
        Returns:
            Hash string of page content
        """
        try:
            # Get page content length and key element counts
            content = self.page.content()
            body_text = self.page.locator("body").inner_text()
            
            # Simple hash: content length + visible element counts
            visible_buttons = self.page.locator("button:visible").count()
            visible_inputs = self.page.locator("input:visible, textarea:visible").count()
            visible_links = self.page.locator("a:visible").count()
            
            # Create a simple hash
            hash_value = f"{len(content)}_{len(body_text)}_{visible_buttons}_{visible_inputs}_{visible_links}"
            return hash_value
            
        except Exception:
            return "unknown"

    def reset(self):
        """Reset state tracking (call when navigating to new page)."""
        try:
            self.last_url = self.page.url
            self.last_dom_hash = self._get_dom_hash()
        except Exception:
            self.last_url = None
            self.last_dom_hash = None

    def wait_for_stable_state(self, timeout: int = 5000) -> bool:
        """
        Wait for the page state to become stable (no changes for a period).
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            True if state became stable, False if timeout
        """
        try:
            # Wait for network to be idle
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            
            # Wait a bit more for any animations/transitions
            self.page.wait_for_timeout(500)
            
            return True
        except Exception:
            return False

