import logging
import json
from datetime import datetime

logger = logging.getLogger("llm_client")

def logged_generate(prompt: str, client) -> dict:
    """Generate with comprehensive logging."""
    start_time = datetime.now()

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        usage = response.usage_metadata
        duration = (datetime.now() - start_time).total_seconds()

        log_entry = {
            "timestamp": start_time.isoformat(),
            "status": "success",
            "duration_seconds": duration,
            "prompt_tokens": usage.prompt_token_count,
            "response_tokens": usage.candidates_token_count,
            "total_tokens": usage.total_token_count,
            "model": "gemini-2.0-flash"
        }
        logger.info(json.dumps(log_entry))

        return {"text": response.text, "usage": log_entry}

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()

        log_entry = {
            "timestamp": start_time.isoformat(),
            "status": "error",
            "duration_seconds": duration,
            "error": str(e),
            "model": "gemini-2.0-flash"
        }
        logger.error(json.dumps(log_entry))

        raise