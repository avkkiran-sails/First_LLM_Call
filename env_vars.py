import os
from dotenv import load_dotenv

def load_environment():
    """
    Load environment variables with environment-specific support.

    Loads .env.{ENVIRONMENT} if ENVIRONMENT is set,
    otherwise falls back to .env.
    """
    environment = os.environ.get("ENVIRONMENT", "development")

    # Try environment-specific file first
    env_file = f".env.{environment}"
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"Loaded {env_file}")
    else:
        load_dotenv()  # Fall back to .env
        print("Loaded .env")

# Usage
load_environment()
api_key = os.environ.get("GEMINI_API_KEY")