import os
import time
from dotenv_demo import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_with_rate_limit_handling(
    prompt: str,
    max_retries: int = 5
) -> str:
    """
    Generate content with rate limit handling.

    If rate limited, waits and retries automatically.​‍​‍﻿﻿‍‌﻿‍‍​‍﻿﻿﻿‌​﻿﻿‍​​‌﻿﻿‌‌‍​‍​

    Args:
        prompt: The input prompt.
        max_retries: Maximum retry attempts.

    Returns:
        The generated text.
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except errors.ClientError as e:
            error_str = str(e).lower()

            if "rate limit" in error_str or "quota" in error_str:
                # Rate limited - wait and retry
                wait_time = min(60, 2 ** attempt)
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                # Other client error - don't retry
                raise e

    raise Exception("Max retries exceeded for rate limit")

# Usage
result = generate_with_rate_limit_handling("Hello!")
print(result)