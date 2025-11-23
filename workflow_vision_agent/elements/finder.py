"""
Find UI elements on web pages for performing actions.
"""

from typing import Optional, List
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError


class ElementFinder:
    """Finds UI elements on the page using various strategies."""

    def __init__(self, page: Page):
        """
        Initialize the element finder.
        
        Args:
            page: Playwright page object to search on
        """
        self.page = page

    def find_button(self, text: str) -> Optional[Locator]:
        """
        Find a button by text.
        
        Args:
            text: Text to search for (case-insensitive, partial match)
            
        Returns:
            Button locator if found, None otherwise
        """
        try:
            text_lower = text.lower()
            
            # Strategy 1: Button role with text
            button = self.page.get_by_role("button", name=text, exact=False).first
            if self._is_visible(button):
                return button
            
            # Strategy 2: Button tag with text
            button = self.page.locator(f"button:has-text('{text_lower}')").first
            if self._is_visible(button):
                return button
            
            # Strategy 3: Element with button role
            button = self.page.locator(f"[role='button']:has-text('{text_lower}')").first
            if self._is_visible(button):
                return button
            
            # Strategy 4: Link styled as button
            button = self.page.locator(f"a[class*='button']:has-text('{text_lower}')").first
            if self._is_visible(button):
                return button
            
            return None
        except Exception as error:
            print(f"Error finding button '{text}': {error}")
            return None

    def find_link(self, text: str) -> Optional[Locator]:
        """
        Find a link by text.
        
        Args:
            text: Text to search for (case-insensitive, partial match)
            
        Returns:
            Link locator if found, None otherwise
        """
        try:
            text_lower = text.lower()
            
            # Strategy 1: Link role with text
            link = self.page.get_by_role("link", name=text, exact=False).first
            if self._is_visible(link):
                return link
            
            # Strategy 2: Anchor tag with text
            link = self.page.locator(f"a:has-text('{text_lower}')").first
            if self._is_visible(link):
                return link
            
            return None
        except Exception as error:
            print(f"Error finding link '{text}': {error}")
            return None

    def find_form_fields(self) -> List[Locator]:
        """
        Find all form input fields on the page.
        
        Returns:
            List of input field locators
        """
        try:
            fields = []
            
            # Find all input types
            inputs = self.page.locator("input[type='text'], input[type='email'], input[type='password'], input[type='number'], textarea")
            count = inputs.count()
            for i in range(count):
                fields.append(inputs.nth(i))
            
            return fields
        except Exception as error:
            print(f"Error finding form fields: {error}")
            return []

    def find_by_text(self, text: str) -> Optional[Locator]:
        """
        Find any element containing the text.
        
        Args:
            text: Text to search for (case-insensitive, partial match)
            
        Returns:
            Element locator if found, None otherwise
        """
        try:
            text_lower = text.lower()
            element = self.page.locator(f"text='{text_lower}'").first
            if self._is_visible(element):
                return element
            return None
        except Exception as error:
            print(f"Error finding element with text '{text}': {error}")
            return None

    def find_input_by_label(self, label_text: str) -> Optional[Locator]:
        """
        Find an input field by its label text.
        
        Args:
            label_text: Label text to search for
            
        Returns:
            Input locator if found, None otherwise
        """
        try:
            label_text_lower = label_text.lower()
            
            # Strategy 1: Find label, then associated input
            label = self.page.locator(f"label:has-text('{label_text_lower}')").first
            if self._is_visible(label):
                label_id = label.get_attribute("for")
                if label_id:
                    input_field = self.page.locator(f"#{label_id}").first
                    if self._is_visible(input_field):
                        return input_field
            
            # Strategy 2: Input with aria-label
            input_field = self.page.locator(f"input[aria-label*='{label_text_lower}']").first
            if self._is_visible(input_field):
                return input_field
            
            # Strategy 3: Input with placeholder
            input_field = self.page.locator(f"input[placeholder*='{label_text_lower}']").first
            if self._is_visible(input_field):
                return input_field
            
            return None
        except Exception as error:
            print(f"Error finding input by label '{label_text}': {error}")
            return None

    def _is_visible(self, locator: Locator) -> bool:
        """
        Check if an element is visible.
        
        Args:
            locator: Element locator to check
            
        Returns:
            True if visible, False otherwise
        """
        try:
            locator.wait_for(state="visible", timeout=1000)
            return True
        except Exception:
            return False

    def wait_for_element(self, locator: Locator, timeout: int = 5000):
        """
        Wait for an element to be visible.
        
        Args:
            locator: Element locator to wait for
            timeout: Maximum time to wait in milliseconds
        """
        try:
            locator.wait_for(state="visible", timeout=timeout)
        except Exception as error:
            print(f"Element not visible within timeout: {error}")

