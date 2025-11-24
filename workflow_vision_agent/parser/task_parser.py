"""
AI-powered task parser that understands questions using LLM.
"""

from typing import Optional, Dict
from workflow_vision_agent.ai import LLMClient


class TaskParser:
    """AI-powered parser that understands questions about web apps."""

    def __init__(self, use_ai: bool = True):
        """
        Initialize the AI-powered task parser.
        
        Args:
            use_ai: If True, use AI to understand questions. If False, use fallback parsing.
        """
        self.use_ai = use_ai
        if use_ai:
            self.ai_client = LLMClient()
        else:
            self.ai_client = None

    def parse_question(self, question: str) -> Dict[str, Optional[str]]:
        """
        Use AI to understand a question and extract all information.
        
        Args:
            question: The question from Agent A (any format)
            
        Returns:
            Dictionary with app_name, action, url, steps, context, and original_question
        """
        if self.use_ai and self.ai_client:
            # Use AI to understand the question
            result = self.ai_client.understand_question(question)
            return result
        else:
            # Fallback to basic parsing
            return self._fallback_parse(question)

    def _fallback_parse(self, question: str) -> Dict:
        """Fallback parsing if AI is not available."""
        import re
        from urllib.parse import urlparse
        
        result = {
            "app_name": None,
            "action": None,
            "url": None,
            "steps": [],
            "context": "",
            "original_question": question,
        }
        
        # Extract URL from markdown links
        url_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", question)
        if url_match:
            result["url"] = url_match.group(2)
            link_text = url_match.group(1)
            app_name = link_text.strip().lower()
            app_name = re.sub(r'\s+(website|app|site|page)', '', app_name, flags=re.IGNORECASE)
            result["app_name"] = app_name if app_name else None
        else:
            # Try to extract URL from plain text
            url_in_text = re.search(r"https?://[^\s]+", question)
            if url_in_text:
                result["url"] = url_in_text.group(0)
                try:
                    parsed_url = urlparse(result["url"])
                    domain = parsed_url.netloc.replace("www.", "").split(".")[0]
                    result["app_name"] = domain.lower()
                except:
                    pass
        
        # Basic action extraction
        cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", "", question)
        cleaned = re.sub(r"https?://[^\s]+", "", cleaned)
        cleaned = re.sub(r"\s+[a-z]{1,3}\s+[a-z]+(?:\s+[a-z]+)*\s*$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^([a-z]{1,3}\s+){0,3}", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip("? \t\n")
        words = cleaned.split()
        if len(words) >= 2:
            result["action"] = cleaned.lower()
        
        return result

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

