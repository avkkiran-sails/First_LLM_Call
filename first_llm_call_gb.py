import os
from dotenv_demo import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

def create_gemini_client() -> genai.Client:
    """
    Create and return a configured Gemini client.

    Raises:
        ValueError: If the API key is not configured.

    Returns:
        A configured Gemini Client instance.
    """
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Set it in your environment or .env file."
        )

    return genai.Client(api_key=api_key)

# Create the client
client = create_gemini_client()
print("Gemini client initialized successfully!")
