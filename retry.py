import os
import time
from dotenv_demo import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_with_retry(
    prompt: str,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> str:
    """
    Generate content with automatic retry on transient failures.

    Uses exponential backoff: delay doubles after each retry.

    Args:
        prompt: The input prompt.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay between retries in seconds.

    Returns:
        The generated text.

    Raises:
        Exception: If all retries are exhausted.
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except errors.ServerError as e:
            # Server errors are often transient - retry
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
                time.sleep(delay)

        except errors.ClientError as e:
            # Client errors usually won't be fixed by retry
            raise e

    raise last_exception

# Usage
result = generate_with_retry("What is the capital of France?")
print(result)