"""
Parse questions to understand what task needs to be performed.
"""

import re
from typing import Optional, Dict
from urllib.parse import urlparse


class TaskParser:
    """Extracts information from questions about what to do in web apps."""

    def __init__(self):
        """Initialize the task parser."""
        pass

    def parse_question(self, question: str) -> Dict[str, Optional[str]]:
        """
        Parse a question to extract the app, action, and URL.
        
        Args:
            question: The question like "How do I create a project in [Linear](url)?"
            
        Returns:
            Dictionary with app_name, action, url, and original_question
        """
        result = {
            "app_name": None,
            "action": None,
            "url": None,
            "original_question": question,
        }

        # Extract URL from markdown links
        url_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", question)
        if url_match:
            result["url"] = url_match.group(2)
            link_text = url_match.group(1)
            # Get app name from the markdown link text
            app_name = self._find_app_name(question, link_text, result["url"])
            result["app_name"] = app_name
        else:
            # Try to extract URL from plain text
            url_in_text = re.search(r"https?://[^\s]+", question)
            if url_in_text:
                result["url"] = url_in_text.group(0)
            result["app_name"] = self._find_app_name(question, None, result["url"])
        
        # Extract the action (what the user wants to do)
        action = self._extract_action(question)
        if action:
            result["action"] = action

        return result

    def _find_app_name(self, question: str, link_text: Optional[str] = None, url: Optional[str] = None) -> Optional[str]:
        """
        Find which app is mentioned in the question.
        Tries multiple strategies to extract app name generically.
        
        Args:
            question: The question text
            link_text: Text from markdown link if available
            url: URL if available
            
        Returns:
            App name in lowercase, or None if not found
        """
        # Strategy 1: Extract from markdown link text (most reliable)
        if link_text:
            # Clean up the link text and use it as app name
            app_name = link_text.strip()
            # Remove common words that might be in link text
            app_name = re.sub(r'\s+(website|app|site|page)', '', app_name, flags=re.IGNORECASE)
            if app_name:
                return app_name.lower()
        
        # Strategy 2: Extract from URL domain
        if url:
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                # Remove www. and common TLDs
                domain = re.sub(r'^www\.', '', domain)
                domain_parts = domain.split('.')
                if len(domain_parts) >= 2:
                    # Get the main domain (e.g., "linear" from "linear.app")
                    main_domain = domain_parts[-2] if domain_parts[-2] not in ['com', 'org', 'net'] else domain_parts[-3] if len(domain_parts) >= 3 else domain_parts[-2]
                    return main_domain.lower()
            except Exception:
                pass
        
        # Strategy 3: Look for capitalized words in the question (common app names)
        # Find words that are capitalized and might be app names
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', question)
        # Filter out common question words
        common_words = {'How', 'Do', 'I', 'Create', 'The', 'In', 'To', 'A', 'An'}
        app_candidates = [word for word in capitalized_words if word not in common_words]
        if app_candidates:
            # Return the first capitalized word that's not a common word
            return app_candidates[0].lower()
        
        return None

    def _extract_action(self, question: str) -> Optional[str]:
        """
        Extract what action the user wants to perform.
        Simple approach: remove URLs, location phrases, and question words.
        
        Args:
            question: The question text
            
        Returns:
            The action description, or None if not found
        """
        # Step 1: Remove markdown links and URLs
        cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", "", question)
        cleaned = re.sub(r"https?://[^\s]+", "", cleaned)
        
        # Step 2: Remove location/app references at the end
        cleaned = re.sub(r"\s+[a-z]{1,3}\s+[a-z]+(?:\s+[a-z]+)*\s*$", "", cleaned, flags=re.IGNORECASE)
        
        # Step 3: Remove question words at start (very short words at beginning)
        cleaned = re.sub(r"^([a-z]{1,3}\s+){0,3}", "", cleaned, flags=re.IGNORECASE)
        
        # Step 4: Clean up and validate
        cleaned = cleaned.strip("? \t\n")
        cleaned = re.sub(r"\s+", " ", cleaned)
        
        # Step 5: Check if we have a meaningful action (at least 2 words)
        words = cleaned.split()
        if len(words) >= 2:
            return cleaned.lower()
        
        return None

    def is_valid_task(self, parsed_task: Dict) -> bool:
        """
        Check if the parsed task has enough information to proceed.
        
        Args:
            parsed_task: The result from parse_question()
            
        Returns:
            True if task is valid, False otherwise
        """
        has_url = parsed_task.get("url") is not None
        has_app = parsed_task.get("app_name") is not None
        has_action = parsed_task.get("action") is not None

        return has_url and (has_app or has_action)

