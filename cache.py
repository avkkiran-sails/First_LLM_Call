import hashlib
from typing import Optional
import os
import time
from dotenv_demo import load_dotenv
from google import genai

load_dotenv()

# Configure client without internal timeout (we'll handle retries manually)
# Using None or very large value to prevent genai library from setting a short deadline
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options={"timeout": None}  # Disable timeout from genai, use retries instead
)

class LLMCache:
    """Simple in-memory cache for LLM responses."""

    def __init__(self):
        self._cache: dict[str, str] = {}

    def _hash_prompt(self, prompt: str, model: str) -> str:
        """Create a unique key for prompt and model combination."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response if available."""
        key = self._hash_prompt(prompt, model)
        return self._cache.get(key)

    def set(self, prompt: str, model: str, response: str):
        """Cache a response."""
        key = self._hash_prompt(prompt, model)
        self._cache[key] = response

# Usage with client
cache = LLMCache()

def cached_generate(prompt: str, max_retries: int = 5) -> str:
    """Generate with caching and automatic retry on failure."""
    model = "gemini-2.5-flash"

    # Check cache first
    cached = cache.get(prompt, model)
    if cached:
        return cached

    # Generate and cache with retry logic
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            cache.set(prompt, model, response.text)
            return response.text
        
        except Exception as e:
            last_exception = e
            error_str = str(e).lower()
            
            # Handle rate limiting (429 errors)
            if "429" in error_str or "resource_exhausted" in error_str:
                if attempt < max_retries:
                    # Extract retry delay if available, otherwise use exponential backoff
                    delay = 35  # Default wait for rate limit
                    if "retry in" in error_str:
                        try:
                            import re
                            match = re.search(r'retry in (\d+(?:\.\d+)?)', error_str)
                            if match:
                                delay = float(match.group(1)) + 2  # Add buffer
                        except:
                            pass
                    print(f"Rate limited (quota exceeded), retrying in {delay}s...")
                    time.sleep(delay)
                    continue
            
            # Retry on transient errors (deadline, timeout, connect)
            elif any(keyword in error_str for keyword in ["deadline", "timeout", "connect", "service temporarily unavailable"]):
                if attempt < max_retries:
                    delay = 3 * (2 ** attempt)  # Exponential backoff: 3s, 6s, 12s, 24s, 48s
                    print(f"Request failed ({error_str[:50]}...), retrying in {delay}s...")
                    time.sleep(delay)
                    continue
            
            raise

    raise last_exception


# Usage
result = cached_generate("What is ML?")
print(result)