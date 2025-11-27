"""
State capture module for detecting UI changes and capturing screenshots/DOM.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from PIL import Image
import io

from ..models.schemas import ElementInfo, StateMetadata


class StateCapture:
    """Captures UI states and detects when new states occur."""
    
    def __init__(self, page: Page, output_dir: Path):
        """
        Initialize state capture.
        
        Args:
            page: Playwright page object
            output_dir: Directory to save captures
        """
        self.page = page
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.previous_dom_hash: Optional[str] = None
        self.previous_url: Optional[str] = None
        self.previous_modal_count: int = 0
        self.state_counter: int = 0
    
    def capture_full_state(
        self, action_taken: Optional[str] = None
    ) -> Optional[StateMetadata]:
        """
        Capture the current UI state if it's new.
        
        Args:
            action_taken: Description of action that led to this state
            
        Returns:
            StateMetadata if new state detected, None otherwise
        """
        # Wait for page to stabilize
        self._wait_for_stable_state()
        
        # Check if this is a new state
        if not self._is_new_state():
            return None
        
        # Capture screenshot and DOM
        self.state_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.state_counter:03d}_state_{timestamp}.jpg"  # Save as JPEG
        dom_filename = f"{self.state_counter:03d}_dom_{timestamp}.json"
        
        screenshot_path = self.output_dir / filename
        dom_path = self.output_dir / dom_filename
        
        # Take screenshot and save as JPEG immediately (much smaller than PNG)
        try:
            # Take screenshot to bytes first
            screenshot_bytes = self.page.screenshot(full_page=True, type="png")
            
            # Convert PNG to JPEG immediately (3.9 MB PNG -> ~1.3 MB JPEG at quality=85)
            img = Image.open(io.BytesIO(screenshot_bytes))
            
            # Convert to RGB (JPEG requires RGB)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            original_size = (img.width, img.height)
            
            # Claude API has max dimension limit of 8000px - ALWAYS enforce this
            max_dimension = 8000
            if img.width > max_dimension or img.height > max_dimension:
                if img.width > img.height:
                    ratio = max_dimension / img.width
                    new_size = (max_dimension, int(img.height * ratio))
                else:
                    ratio = max_dimension / img.height
                    new_size = (int(img.width * ratio), max_dimension)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"   📐 Resized from {original_size[0]}x{original_size[1]} to {new_size[0]}x{new_size[1]} (Claude 8K limit)")
            
            # Verify dimensions are within limit (safety check)
            if img.width > max_dimension or img.height > max_dimension:
                # Force resize to ensure compliance
                if img.width > img.height:
                    ratio = max_dimension / img.width
                    new_size = (max_dimension, int(img.height * ratio))
                else:
                    ratio = max_dimension / img.height
                    new_size = (int(img.width * ratio), max_dimension)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"   ⚠️  Force resized to {new_size[0]}x{new_size[1]} to meet 8K limit")
            
            # Also resize if too wide for efficiency (but keep under 8K limit)
            max_width = min(1920, max_dimension)
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                # Ensure height doesn't exceed 8K
                if new_size[1] > max_dimension:
                    ratio = max_dimension / new_size[1]
                    new_size = (int(new_size[0] * ratio), max_dimension)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"   📐 Resized to {new_size[0]}x{new_size[1]} for efficiency")
            
            # Save as JPEG with good quality (85 is a good balance)
            # Update filename to .jpg
            screenshot_path = screenshot_path.with_suffix('.jpg')
            filename = screenshot_path.name
            
            img.save(screenshot_path, 'JPEG', quality=85, optimize=True)
            
            file_size = screenshot_path.stat().st_size
            print(f"   📸 Saved as JPEG: {file_size / 1024 / 1024:.2f} MB")
            
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return None
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return None
        
        # Capture DOM snapshot
        dom_snapshot = self._capture_dom_snapshot()
        try:
            with open(dom_path, "w", encoding="utf-8") as f:
                json.dump(dom_snapshot, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ DOM capture error: {e}")
            dom_filename = None
        
        # Update previous state
        self.previous_dom_hash = self._compute_dom_hash(dom_snapshot)
        self.previous_url = self.page.url
        self.previous_modal_count = self._count_modals()
        
        # Create metadata (filename was updated to .jpg above)
        metadata = StateMetadata(
            filename=filename,
            dom_filename=dom_filename,
            action_taken=action_taken,
            has_url=self._has_unique_url(),
            url=self.page.url if self._has_unique_url() else None,
            timestamp=datetime.now(),
            element_count=len(dom_snapshot.get("interactive_elements", [])),
            is_modal=self._is_modal_state(),
            is_form=self._is_form_state(dom_snapshot),
        )
        
        return metadata
    
    def extract_interactive_elements(self) -> List[ElementInfo]:
        """
        Extract all interactive elements from the current page.
        
        Returns:
            List of ElementInfo objects
        """
        try:
            elements = self.page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = [
                        'button', 'a', 'input', 'select', 'textarea',
                        '[role="button"]', '[role="link"]', '[role="menuitem"]',
                        '[onclick]', '[tabindex="0"]'
                    ];
                    
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0 && 
                                window.getComputedStyle(el).visibility !== 'hidden' &&
                                window.getComputedStyle(el).display !== 'none') {
                                elements.push({
                                    selector: selector,
                                    text: el.textContent?.trim() || el.value || el.placeholder || '',
                                    tag: el.tagName.toLowerCase(),
                                    role: el.getAttribute('role') || null,
                                    type: el.type || null,
                                    placeholder: el.placeholder || null,
                                    ariaLabel: el.getAttribute('aria-label') || null,
                                    isVisible: true,
                                    isEnabled: !el.disabled
                                });
                            }
                        });
                    });
                    return elements;
                }
            """)
            
            # Convert to ElementInfo objects
            element_infos = []
            for i, elem in enumerate(elements):
                # Generate unique selector
                selector = self._generate_selector(elem, i)
                
                element_infos.append(ElementInfo(
                    selector=selector,
                    text=elem.get("text") or None,
                    tag=elem.get("tag", "unknown"),
                    role=elem.get("role"),
                    type=elem.get("type"),
                    placeholder=elem.get("placeholder"),
                    aria_label=elem.get("ariaLabel"),
                    is_visible=elem.get("isVisible", True),
                    is_enabled=elem.get("isEnabled", True),
                ))
            
            return element_infos
        except Exception as e:
            print(f"❌ Error extracting elements: {e}")
            return []
    
    def _wait_for_stable_state(self):
        """Wait for the page to stabilize after an action."""
        try:
            # Wait for network to be idle
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except PlaywrightTimeoutError:
            pass  # Acceptable if network never idles
        
        # Additional wait for dynamic content
        self.page.wait_for_timeout(500)
        
        # Check if DOM has changed
        for _ in range(5):  # Check 5 times over 1 second
            self.page.wait_for_timeout(200)
            # If DOM hasn't changed, we're stable
            current_hash = self._compute_dom_hash(self._capture_dom_snapshot())
            if current_hash == self.previous_dom_hash:
                break
    
    def _is_new_state(self) -> bool:
        """Determine if the current state is new and worth capturing."""
        current_url = self.page.url
        current_modal_count = self._count_modals()
        current_dom_hash = self._compute_dom_hash(self._capture_dom_snapshot())
        
        # URL changed
        if current_url != self.previous_url:
            return True
        
        # Modal appeared
        if current_modal_count > self.previous_modal_count:
            return True
        
        # DOM structure changed significantly
        if current_dom_hash != self.previous_dom_hash:
            return True
        
        # Check for success/error messages
        if self._has_new_messages():
            return True
        
        return False
    
    def _count_modals(self) -> int:
        """Count visible modal/dialog elements."""
        try:
            count = self.page.evaluate("""
                () => {
                    const modals = document.querySelectorAll(
                        '[role="dialog"], [role="alertdialog"], .modal, .dialog, [class*="modal"], [class*="dialog"]'
                    );
                    return Array.from(modals).filter(m => {
                        const style = window.getComputedStyle(m);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    }).length;
                }
            """)
            return count
        except Exception:
            return 0
    
    def _is_modal_state(self) -> bool:
        """Check if current state is a modal."""
        return self._count_modals() > 0
    
    def _is_form_state(self, dom_snapshot: Dict) -> bool:
        """Check if current state contains a form."""
        forms = dom_snapshot.get("forms", [])
        return len(forms) > 0
    
    def _has_unique_url(self) -> bool:
        """Check if current state has a unique URL (not just hash change)."""
        url = self.page.url
        # Remove hash and query params for comparison
        base_url = url.split("#")[0].split("?")[0]
        if not self.previous_url:
            return True  # First state always has URL
        prev_base = self.previous_url.split("#")[0].split("?")[0]
        return base_url != prev_base
    
    def _has_new_messages(self) -> bool:
        """Check for new success/error messages."""
        try:
            messages = self.page.evaluate("""
                () => {
                    const selectors = [
                        '[role="alert"]', '[role="status"]',
                        '.success', '.error', '.message',
                        '[class*="success"]', '[class*="error"]'
                    ];
                    const found = [];
                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => {
                            if (el.textContent && el.textContent.trim()) {
                                found.push(el.textContent.trim());
                            }
                        });
                    });
                    return found;
                }
            """)
            return len(messages) > 0
        except Exception:
            return False
    
    def _capture_dom_snapshot(self) -> Dict[str, Any]:
        """Capture a snapshot of the DOM structure."""
        try:
            snapshot = self.page.evaluate("""
                () => {
                    return {
                        url: window.location.href,
                        title: document.title,
                        forms: Array.from(document.querySelectorAll('form')).map(f => ({
                            id: f.id || null,
                            action: f.action || null,
                            method: f.method || null,
                            fields: Array.from(f.querySelectorAll('input, select, textarea')).map(inp => ({
                                type: inp.type || inp.tagName.toLowerCase(),
                                name: inp.name || null,
                                id: inp.id || null,
                                placeholder: inp.placeholder || null
                            }))
                        })),
                        interactive_elements: Array.from(document.querySelectorAll(
                            'button, a, input, select, textarea, [role="button"], [role="link"]'
                        )).map(el => ({
                            tag: el.tagName.toLowerCase(),
                            text: el.textContent?.trim() || el.value || el.placeholder || '',
                            id: el.id || null,
                            class: el.className || null,
                            role: el.getAttribute('role') || null
                        }))
                    };
                }
            """)
            return snapshot
        except Exception as e:
            print(f"❌ DOM snapshot error: {e}")
            return {}
    
    def _compute_dom_hash(self, dom_snapshot: Dict) -> str:
        """Compute a hash of the DOM structure for comparison."""
        import hashlib
        
        # Create a simplified representation
        structure = {
            "url": dom_snapshot.get("url", ""),
            "title": dom_snapshot.get("title", ""),
            "form_count": len(dom_snapshot.get("forms", [])),
            "element_count": len(dom_snapshot.get("interactive_elements", [])),
            "modal_count": self._count_modals(),
        }
        
        structure_str = json.dumps(structure, sort_keys=True)
        return hashlib.md5(structure_str.encode()).hexdigest()
    
    def _generate_selector(self, element: Dict, index: int) -> str:
        """Generate a unique CSS selector for an element."""
        # Try ID first
        if element.get("id"):
            return f"#{element['id']}"
        
        # Try data-testid
        # (We'd need to capture this in the evaluate, but for now use tag + index)
        tag = element.get("tag", "div")
        text = element.get("text", "")
        
        # Try to create a meaningful selector
        if text and len(text) < 50:
            # Use text content as fallback
            return f"{tag}:has-text('{text[:30]}')"
        
        return f"{tag}:nth-of-type({index + 1})"
    
    def _compress_image(self, image_bytes: bytes, max_size: int, quality: int = 80) -> bytes:
        """
        Compress PNG image to fit within size limit by converting to JPEG.
        Always converts to JPEG for better compression.
        
        Args:
            image_bytes: Original image bytes
            max_size: Maximum size in bytes
            quality: JPEG quality (start with 80, reduce if needed)
            
        Returns:
            Compressed image bytes (JPEG format)
        """
        try:
            # Open image
            img = Image.open(io.BytesIO(image_bytes))
            original_size = len(image_bytes)
            
            # Convert to RGB if needed (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Try different quality levels (start high, go lower)
            compressed = None
            for q in range(quality, 50, -5):
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=q, optimize=True)
                compressed = output.getvalue()
                
                if len(compressed) <= max_size:
                    return compressed
            
            # If still too large, resize and try again
            scale = 0.9
            original_img = img
            while len(compressed) > max_size and scale > 0.5:
                new_size = (int(original_img.width * scale), int(original_img.height * scale))
                resized = original_img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Try different quality levels with resized image
                for q in range(75, 50, -5):
                    output = io.BytesIO()
                    resized.save(output, format='JPEG', quality=q, optimize=True)
                    compressed = output.getvalue()
                    if len(compressed) <= max_size:
                        return compressed
                
                scale -= 0.1
            
            # Return best compression we got (should be under limit now)
            return compressed if compressed else image_bytes
            
        except Exception as e:
            print(f"⚠️  Image compression error: {e}, using original")
            import traceback
            traceback.print_exc()
            return image_bytes
    
    def reset(self):
        """Reset state tracking (for new workflow)."""
        self.previous_dom_hash = None
        self.previous_url = None
        self.previous_modal_count = 0
        self.state_counter = 0

