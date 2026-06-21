import os
from dotenv_demo import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv()

# Configure client with timeout
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options={"timeout": 60.0}  # 30 second timeout
)

def generate_with_timeout(prompt: str) -> str:
    """
    Generate content with a configured timeout.

    Args:
        prompt: The input prompt.

    Returns:
        The generated text.

    Raises:
        TimeoutError: If the request times out.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        if "timeout" in str(e).lower():
            raise TimeoutError(f"Request timed out: {e}")
        raise

# Usage
result = generate_with_timeout("Tell me a short story.")
print(result)