"""
LLM controller for Claude API interactions with vision capabilities.
"""

import os
import base64
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import anthropic

from ..models.schemas import ActionDecision, ElementInfo


class LLMController:
    """Handles communication with Claude API for decision-making."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM controller.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"  
        self.conversation_history: List[Dict[str, str]] = []
    
    def decide_next_action(
        self,
        task_description: str,
        screenshot_path: Path,
        available_elements: List[ElementInfo],
        action_history: List[str],
        current_url: str,
    ) -> ActionDecision:
        """
        Ask Claude to decide the next action based on current state.
        
        Args:
            task_description: The task the user wants to accomplish
            screenshot_path: Path to current screenshot
            available_elements: List of interactive elements on page
            action_history: History of actions taken so far
            current_url: Current page URL
            
        Returns:
            ActionDecision with Claude's recommendation
        """
        # Read and encode screenshot (should already be JPEG from capture)
        with open(screenshot_path, "rb") as f:
            image_bytes = f.read()
            
            # Verify size (Claude limit is 5 MB, but base64 adds ~33%)
        
            max_size_mb = 4.0  # 4 MB to account for base64 encoding
            max_size = max_size_mb * 1024 * 1024
            
            if len(image_bytes) > max_size:
                print(f"⚠️  Screenshot too large ({len(image_bytes) / 1024 / 1024:.1f} MB), compressing...")
                from PIL import Image
                import io
                
                # Compress on-the-fly with aggressive compression
                img = Image.open(io.BytesIO(image_bytes))
                img = img.convert('RGB')  # Ensure RGB
                
                # Try different quality levels
                compressed = None
                for quality in [85, 75, 65, 50]:
                    buffer = io.BytesIO()
                    img.save(buffer, 'JPEG', quality=quality, optimize=True)
                    size_mb = buffer.tell() / (1024 * 1024)
                    
                    if size_mb <= max_size_mb:
                        compressed = buffer.getvalue()
                        print(f"   ✅ Compressed to {size_mb:.2f} MB at quality={quality}")
                        break
                
                # If still too large, resize
                if not compressed or len(compressed) > max_size:
                    print(f"   📐 Resizing image...")
                    img.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    img.save(buffer, 'JPEG', quality=75, optimize=True)
                    compressed = buffer.getvalue()
                    print(f"   ✅ Resized and compressed to {len(compressed) / 1024 / 1024:.2f} MB")
                
                image_bytes = compressed if compressed else image_bytes
            
            image_data = base64.b64encode(image_bytes).decode("utf-8")
        
        # Format available elements
        elements_text = self._format_elements(available_elements)
        
        # Format action history
        history_text = "\n".join([f"- {action}" for action in action_history[-5:]]) if action_history else "None"
        
        # Create prompt
        prompt = f"""You are an AI agent helping a user accomplish a task on a web application.

TASK: {task_description}

CURRENT URL: {current_url}

AVAILABLE INTERACTIVE ELEMENTS:
{elements_text}

PREVIOUS ACTIONS TAKEN:
{history_text}

Analyze the screenshot and available elements to determine the next action needed to progress toward completing the task.

CRITICAL: Before deciding the next action, ask yourself:
1. Has the user's task been completed? 
2. Did the user get what they wanted?
3. Is there a success message, confirmation, or completion indicator visible?

Return your decision as JSON with the following structure:
{{
    "action_type": "click" | "type" | "wait" | "scroll" | "done",
    "target_selector": "CSS selector for the element (if action is click or type)",
    "target_description": "Human-readable description of what you're targeting",
    "value": "Text to type (if action is 'type')",
    "reasoning": "Your reasoning for this decision. ALWAYS include: 'Task complete: YES/NO - [explanation]'",
    "confidence": 0.0-1.0,
    "capture_state": true/false,
    "task_complete": true/false,
    "user_got_what_they_wanted": true/false
}}

IMPORTANT:
- ALWAYS check if the task is complete before deciding next action
- Look for success messages, confirmations, completion indicators, or the desired end state
- If the task is complete, set action_type to "done", task_complete to true, and user_got_what_they_wanted to true
- Use the most specific CSS selector possible from the available elements
- If you can't find the right element, set confidence < 0.7 and explain why
- Set capture_state=true if this action will result in a new UI state (modal, form, new page)
- Be precise with selectors - prefer IDs, data-testid, or unique class combinations

Return ONLY valid JSON, no other text."""

        try:
            # Determine media type from file extension
            media_type = "image/jpeg" if str(screenshot_path).lower().endswith(('.jpg', '.jpeg')) else "image/png"
            
            # Call Claude with vision
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
            )
            
            # Parse response
            response_text = message.content[0].text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            decision_data = json.loads(response_text)
            
            # Validate and create ActionDecision (handle missing new fields gracefully)
            # Set defaults for new fields if not present
            if "task_complete" not in decision_data:
                decision_data["task_complete"] = decision_data.get("action_type") == "done"
            if "user_got_what_they_wanted" not in decision_data:
                decision_data["user_got_what_they_wanted"] = decision_data.get("task_complete", False)
            
            return ActionDecision(**decision_data)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Response was: {response_text[:200]}")
            # Return safe fallback
            return ActionDecision(
                action_type="wait",
                reasoning=f"Failed to parse Claude response: {e}",
                confidence=0.0,
                task_complete=False,
                user_got_what_they_wanted=False,
            )
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            return ActionDecision(
                action_type="wait",
                reasoning=f"API error: {e}",
                confidence=0.0,
                task_complete=False,
                user_got_what_they_wanted=False,
            )
    
    def _format_elements(self, elements: List[ElementInfo]) -> str:
        """Format element list for prompt."""
        if not elements:
            return "No interactive elements found."
        
        formatted = []
        for i, elem in enumerate(elements[:50]):  # Limit to 50 elements
            parts = [f"Element {i+1}:"]
            parts.append(f"  Selector: {elem.selector}")
            if elem.text:
                parts.append(f"  Text: {elem.text[:50]}")
            if elem.aria_label:
                parts.append(f"  Aria Label: {elem.aria_label}")
            if elem.role:
                parts.append(f"  Role: {elem.role}")
            if elem.type:
                parts.append(f"  Type: {elem.type}")
            if elem.placeholder:
                parts.append(f"  Placeholder: {elem.placeholder}")
            parts.append(f"  Enabled: {elem.is_enabled}")
            formatted.append("\n".join(parts))
        
        return "\n\n".join(formatted)
    
    def get_alternative_selector(
        self, failed_selector: str, available_elements: List[ElementInfo]
    ) -> Optional[str]:
        """
        Get an alternative selector when one fails.
        
        Args:
            failed_selector: The selector that failed
            available_elements: Available elements to choose from
            
        Returns:
            Alternative selector or None
        """
        # Simple fallback: try to find similar elements
        for elem in available_elements:
            if elem.text and len(elem.text) > 0:
                # Try text-based selector
                return f"text='{elem.text[:30]}'"
        
        return None

