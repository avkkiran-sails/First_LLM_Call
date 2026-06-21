import os
from dotenv_demo import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def safe_generate(prompt: str) -> str:
    """
    Generate content with comprehensive error handling.

    Args:
        prompt: The input prompt.

    Returns:
        The generated text, or an error message.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text

    except errors.ClientError as e:
        # 4xx errors - client-side issues
        return f"Client error: {e.code} - {e.message}"

    except errors.ServerError as e:
        # 5xx errors - server-side issues
        return f"Server error: {e}"

    except Exception as e:
        # Catch-all for unexpected errors
        return f"Unexpected error: {e}"

# Test the function
result = safe_generate("Hello!")
print(result)