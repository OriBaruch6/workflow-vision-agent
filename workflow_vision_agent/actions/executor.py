"""
Action executor for performing interactions on web pages.
"""

from typing import Optional, Dict, List
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from workflow_vision_agent.elements import ElementFinder


class ActionExecutor:
    """Executes actions on web pages like clicking, typing, and form filling."""

    def __init__(self, page: Page, element_finder: Optional[ElementFinder] = None):
        """
        Initialize the action executor.
        
        Args:
            page: Playwright page object
            element_finder: ElementFinder instance (creates one if not provided)
        """
        self.page = page
        self.finder = element_finder or ElementFinder(page)

    def click(self, text: str, element_type: str = "button") -> bool:
        """
        Click on an element by its text.
        
        Args:
            text: Text to search for (button text, link text, etc.)
            element_type: Type of element to find ("button", "link", or "any")
            
        Returns:
            True if clicked successfully, False otherwise
        """
        try:
            locator = None
            
            if element_type == "button":
                locator = self.finder.find_button(text)
            elif element_type == "link":
                locator = self.finder.find_link(text)
            else:
                # Try button first, then link, then any element
                locator = self.finder.find_button(text) or self.finder.find_link(text) or self.finder.find_by_text(text)
            
            if not locator:
                print(f"Could not find {element_type} with text: {text}")
                return False
            
            print(f"Clicking {element_type}: {text}")
            locator.click(timeout=5000)
            
            # Wait a bit for UI to update
            self.page.wait_for_timeout(500)
            return True
            
        except PlaywrightTimeoutError:
            print(f"Timeout waiting for {element_type} to be clickable: {text}")
            return False
        except Exception as error:
            print(f"Error clicking {element_type} '{text}': {error}")
            return False

    def type_text(self, field_label: str, text: str) -> bool:
        """
        Type text into an input field by its label.
        
        Args:
            field_label: Label text of the input field
            text: Text to type
            
        Returns:
            True if typed successfully, False otherwise
        """
        try:
            input_field = self.finder.find_input_by_label(field_label)
            
            if not input_field:
                print(f"Could not find input field with label: {field_label}")
                return False
            
            print(f"Typing into '{field_label}': {text}")
            input_field.clear()
            input_field.fill(text)
            
            # Wait a bit for input to register
            self.page.wait_for_timeout(300)
            return True
            
        except Exception as error:
            print(f"Error typing into field '{field_label}': {error}")
            return False

    def fill_form(self, fields: Dict[str, str]) -> bool:
        """
        Fill multiple form fields at once.
        
        Args:
            fields: Dictionary mapping field labels to values
                   Example: {"Name": "John", "Email": "john@example.com"}
            
        Returns:
            True if all fields filled successfully, False otherwise
        """
        try:
            all_success = True
            
            for label, value in fields.items():
                success = self.type_text(label, value)
                if not success:
                    all_success = False
            
            return all_success
            
        except Exception as error:
            print(f"Error filling form: {error}")
            return False

    def select_option(self, select_label: str, option_text: str) -> bool:
        """
        Select an option from a dropdown/select field.
        
        Args:
            select_label: Label text of the select field
            option_text: Text of the option to select
            
        Returns:
            True if selected successfully, False otherwise
        """
        try:
            # Find the select field by label
            select_field = self.finder.find_input_by_label(select_label)
            
            if not select_field:
                # Try finding select element directly
                label = self.finder.find_by_text(select_label)
                if label:
                    # Try to find associated select
                    select_field = self.page.locator("select").first
                else:
                    print(f"Could not find select field with label: {select_label}")
                    return False
            
            print(f"Selecting '{option_text}' from '{select_label}'")
            select_field.select_option(label=option_text, timeout=5000)
            
            self.page.wait_for_timeout(300)
            return True
            
        except Exception as error:
            print(f"Error selecting option '{option_text}' from '{select_label}': {error}")
            return False

    def submit_form(self, form_selector: Optional[str] = None) -> bool:
        """
        Submit a form by pressing Enter or clicking submit button.
        
        Args:
            form_selector: Optional CSS selector for the form (if None, finds first form)
            
        Returns:
            True if submitted successfully, False otherwise
        """
        try:
            if form_selector:
                form = self.page.locator(form_selector).first
            else:
                # Try to find submit button
                submit_button = self.finder.find_button("submit") or self.finder.find_button("save") or self.finder.find_button("create")
                
                if submit_button:
                    print("Submitting form by clicking submit button")
                    submit_button.click(timeout=5000)
                    self.page.wait_for_timeout(1000)
                    return True
                
                # Fallback: find first form and submit
                form = self.page.locator("form").first
                if not self.finder._is_visible(form):
                    print("Could not find form to submit")
                    return False
            
            print("Submitting form")
            form.press("Enter")
            self.page.wait_for_timeout(1000)
            return True
            
        except Exception as error:
            print(f"Error submitting form: {error}")
            return False

    def wait_for_navigation(self, timeout: int = 5000) -> bool:
        """
        Wait for page navigation to complete.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            True if navigation completed, False if timeout
        """
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            print("Timeout waiting for navigation")
            return False
        except Exception as error:
            print(f"Error waiting for navigation: {error}")
            return False

    def wait_for_element_visible(self, text: str, timeout: int = 5000) -> bool:
        """
        Wait for an element with specific text to become visible.
        
        Args:
            text: Text to wait for
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            True if element became visible, False if timeout
        """
        try:
            element = self.finder.find_by_text(text)
            if element:
                element.wait_for(state="visible", timeout=timeout)
                return True
            return False
        except Exception:
            return False

