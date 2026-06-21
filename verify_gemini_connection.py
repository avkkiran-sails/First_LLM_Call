
#### Verifying the Connection

import os
from dotenv_demo import load_dotenv
from google import genai

load_dotenv()

def verify_gemini_connection() -> bool:
    """
    Verify that we can connect to the Gemini API.

    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: API key not configured")
            return False

        client = genai.Client(api_key=api_key)

        # Make a minimal API call to verify connection
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'connected' in one word."
        )

        print(f"Connection verified: {response.text}")
        return True

    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    verify_gemini_connection()