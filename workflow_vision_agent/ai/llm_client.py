"""
LLM client for AI-powered understanding.
"""

import os
import json
from typing import Dict, Optional
from .prompts import get_question_understanding_prompt, get_system_message


class LLMClient:
    """Client for interacting with LLM APIs."""

    def __init__(self, provider: str = "anthropic", model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the LLM client.
        
        Args:
            provider: AI provider (default: "anthropic")
            model: Model name to use (default: "claude-3-5-sonnet-20241022")
        """
        self.provider = provider
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            print("Warning: No API key found. Set ANTHROPIC_API_KEY environment variable.")
            print("Falling back to rule-based parsing.")

    def understand_question(self, question: str) -> Dict[str, Optional[str]]:
        """
        Use AI to understand a question and extract all information.
        
        Args:
            question: The question from Agent A
            
        Returns:
            Dictionary with app_name, action, url, and parsed information
        """
        if not self.api_key:
            # Fallback to basic extraction if no API key
            return self._fallback_parse(question)
        
        try:
            prompt = self._create_understanding_prompt(question)
            response = self._call_llm(prompt)
            return self._parse_llm_response(response, question)
        except Exception as error:
            print(f"AI parsing failed: {error}. Falling back to rule-based parsing.")
            return self._fallback_parse(question)

    def _create_understanding_prompt(self, question: str) -> str:
        """Create prompt for LLM to understand the question."""
        return get_question_understanding_prompt(question)

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API."""
        if self.provider == "anthropic":
            return self._call_anthropic(prompt)
        else:
            raise ValueError(f"Only Anthropic is supported. Provider '{self.provider}' not supported.")

    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Get system message from prompts module
            system_message = get_system_message()
            
            response = client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_message,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as error:
            raise Exception(f"Anthropic API error: {error}")

    def _parse_llm_response(self, response: str, original_question: str) -> Dict:
        """Parse LLM response into structured format."""
        try:
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            
            return {
                "app_name": data.get("app_name", "").lower() if data.get("app_name") else None,
                "action": data.get("action", "").lower() if data.get("action") else None,
                "url": data.get("url") or None,
                "steps": data.get("steps", []),
                "context": data.get("context", ""),
                "original_question": original_question,
            }
        except Exception as error:
            print(f"Failed to parse LLM response: {error}")
            return self._fallback_parse(original_question)

    def _fallback_parse(self, question: str) -> Dict:
        """Fallback to basic rule-based parsing if AI fails."""
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
        
        # Basic URL extraction
        url_match = re.search(r"https?://[^\s]+", question)
        if url_match:
            result["url"] = url_match.group(0)
            try:
                parsed_url = urlparse(result["url"])
                domain = parsed_url.netloc.replace("www.", "").split(".")[0]
                result["app_name"] = domain.lower()
            except:
                pass
        
        # Basic action extraction
        cleaned = re.sub(r"https?://[^\s]+", "", question)
        cleaned = re.sub(r"\s+[a-z]{1,3}\s+[a-z]+(?:\s+[a-z]+)*\s*$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^([a-z]{1,3}\s+){0,3}", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip("? \t\n")
        words = cleaned.split()
        if len(words) >= 2:
            result["action"] = cleaned.lower()
        
        return result

