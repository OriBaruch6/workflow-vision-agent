"""
Browser controller for navigating web applications and capturing screenshots.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError


class BrowserController:
    """Controls the browser to navigate apps and take screenshots."""

    def __init__(self, headless: bool = False):
        """
        Initialize the browser controller.
        
        Args:
            headless: If True, run browser in background (no visible window)
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self.screenshots_folder = Path("screenshots")
        self.screenshots_folder.mkdir(exist_ok=True)

    def start_browser(self):
        """Start the browser and create a new page."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()
            print("Browser started successfully")
        except Exception as error:
            print(f"Failed to start browser: {error}")
            raise

    def close_browser(self):
        """Close the browser and cleanup."""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print("Browser closed")
        except Exception as error:
            print(f"Error closing browser: {error}")

    def go_to_url(self, url: str):
        """
        Navigate to a specific URL.
        
        Args:
            url: The website URL to visit
        """
        try:
            if not self.page:
                raise Exception("Browser not started. Call start_browser() first.")
            
            print(f"Navigating to: {url}")
            self.page.goto(url, wait_until="networkidle", timeout=30000)
            print("Page loaded successfully")
        except PlaywrightTimeoutError:
            print(f"Timeout while loading {url}")
            raise
        except Exception as error:
            print(f"Failed to navigate to {url}: {error}")
            raise

    def take_screenshot(self, step_name: str) -> str:
        """
        Take a screenshot of the current page.
        
        Args:
            step_name: Name for this screenshot (used in filename)
            
        Returns:
            Path to the saved screenshot file
        """
        try:
            if not self.page:
                raise Exception("Browser not started. Call start_browser() first.")
            
            # Create a safe filename from step name
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in step_name)
            safe_name = safe_name.replace(' ', '_').lower()
            
            screenshot_path = self.screenshots_folder / f"{safe_name}.png"
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            
            print(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        except Exception as error:
            print(f"Failed to take screenshot: {error}")
            raise

    def wait_for_page_load(self, timeout: int = 5000):
        """
        Wait for the page to finish loading.
        
        Args:
            timeout: Maximum time to wait in milliseconds
        """
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as error:
            print(f"Page load wait timeout: {error}")

    def get_current_url(self) -> str:
        """Get the current page URL."""
        try:
            return self.page.url
        except Exception as error:
            print(f"Failed to get current URL: {error}")
            return ""

