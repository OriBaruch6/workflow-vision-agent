"""
Browser navigation module using Playwright.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError


class BrowserNavigator:
    """Handles browser navigation and interaction using Playwright."""
    
    def __init__(self, headless: bool = False, browser_type: str = "chromium"):
        """
        Initialize the browser navigator.
        
        Args:
            headless: Run browser in headless mode
            browser_type: Browser type ('chromium', 'firefox', 'webkit')
        """
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.navigation_history: List[str] = []
        self.cookies_file = Path(".browser_cookies.json")
        self.storage_file = Path(".browser_storage.json")
    
    def start(self):
        """Start the browser and create a new context."""
        self.playwright = sync_playwright().start()
        
        browser_launcher = getattr(self.playwright, self.browser_type)
        self.browser = browser_launcher.launch(headless=self.headless)
        
        # Create context with persistent storage
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        
        # Load saved cookies and storage
        self._load_persistence()
        
        self.page = self.context.new_page()
    
    def close(self):
        """Close the browser and save persistence data."""
        if self.context:
            self._save_persistence()
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def goto(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 60000) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle')
            timeout: Timeout in milliseconds (default: 60s for slow sites)
            
        Returns:
            True if navigation successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started. Call start() first.")
            
            self.page.goto(url, wait_until=wait_until, timeout=timeout)
            # Give page a moment to stabilize
            self.page.wait_for_timeout(2000)
            self.navigation_history.append(url)
            return True
        except PlaywrightTimeoutError:
            # Even if timeout, page might be usable
            print(f"⚠️  Navigation timeout for {url}, but page may be usable")
            self.page.wait_for_timeout(2000)
            return True
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
    def click(self, selector: str, timeout: int = 5000) -> bool:
        """
        Click an element by CSS selector.
        
        Args:
            selector: CSS selector for the element
            timeout: Timeout in milliseconds
            
        Returns:
            True if click successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")
            
            element = self.page.locator(selector).first
            element.wait_for(state="visible", timeout=timeout)
            
            # Try normal click first
            try:
                element.click(timeout=timeout)
                return True
            except Exception:
                # If normal click fails (overlay blocking), try JavaScript click
                try:
                    self.page.evaluate(f"""
                        () => {{
                            const el = document.querySelector('{selector}');
                            if (el) {{
                                el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                                el.click();
                                return true;
                            }}
                            return false;
                        }}
                    """)
                    self.page.wait_for_timeout(1000)  # Wait for navigation/action
                    return True
                except Exception as e2:
                    print(f"   ⚠️  JavaScript click also failed: {e2}")
                    return False
        except Exception as e:
            print(f"❌ Click error on {selector}: {e}")
            return False
    
    def fill(self, selector: str, value: str, timeout: int = 5000) -> bool:
        """
        Fill a form field by CSS selector.
        
        Args:
            selector: CSS selector for the input field
            value: Value to fill
            timeout: Timeout in milliseconds
            
        Returns:
            True if fill successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")
            
            element = self.page.locator(selector).first
            element.wait_for(state="visible", timeout=timeout)
            element.fill(value)
            return True
        except Exception as e:
            print(f"❌ Fill error on {selector}: {e}")
            return False
    
    def wait_for_element(
        self, selector: str, state: str = "visible", timeout: int = 10000
    ) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector
            state: Element state ('visible', 'attached', 'hidden')
            timeout: Timeout in milliseconds
            
        Returns:
            True if element appeared
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")
            
            self.page.wait_for_selector(selector, state=state, timeout=timeout)
            return True
        except Exception:
            return False
    
    def wait_for_load_state(self, state: str = "networkidle", timeout: int = 30000):
        """Wait for page load state."""
        try:
            if self.page:
                self.page.wait_for_load_state(state, timeout=timeout)
        except Exception:
            pass  # Timeout is acceptable
    
    def get_current_url(self) -> str:
        """Get the current page URL."""
        return self.page.url if self.page else ""
    
    def _load_persistence(self):
        """Load cookies and localStorage from saved files."""
        if not self.context:
            return
        
        # Load cookies
        if self.cookies_file.exists():
            try:
                with open(self.cookies_file, "r") as f:
                    cookies = json.load(f)
                    self.context.add_cookies(cookies)
            except Exception as e:
                print(f"⚠️  Error loading cookies: {e}")
        
        # localStorage is loaded per-page, so we'll handle it in goto()
    
    def _save_persistence(self):
        """Save cookies and localStorage to files."""
        if not self.context:
            return
        
        # Save cookies
        try:
            cookies = self.context.cookies()
            with open(self.cookies_file, "w") as f:
                json.dump(cookies, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving cookies: {e}")
        
        # localStorage is saved per-page
    
    def set_cookies(self, cookies: List[Dict[str, Any]]):
        """Set cookies for authentication."""
        if self.context:
            self.context.add_cookies(cookies)
    
    def get_local_storage(self) -> Dict[str, str]:
        """Get localStorage items from current page."""
        if not self.page:
            return {}
        
        return self.page.evaluate("() => ({ ...localStorage })")
    
    def set_local_storage(self, items: Dict[str, str]):
        """Set localStorage items on current page."""
        if not self.page:
            return
        
        for key, value in items.items():
            self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")

