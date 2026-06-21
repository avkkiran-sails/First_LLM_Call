# OpenAI ChatGPT API Call

This Python script demonstrates how to interact with OpenAI's ChatGPT models using the OpenAI API. The API key is securely loaded from environment variables.

## Prerequisites

- Python 3.7 or higher
- An OpenAI API key

## Setup

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key as an environment variable:**
   - On Windows (Command Prompt):
     ```
     set OPENAI_API_KEY=your_api_key_here
     ```
   - On Windows (PowerShell):
     ```
     $env:OPENAI_API_KEY="your_api_key_here"
     ```
   - On Linux/macOS:
     ```
     export OPENAI_API_KEY=your_api_key_here
     ```

   Replace `your_api_key_here` with your actual OpenAI API key.

## Usage

Run the script:
```
python openai_chatgpt_call.py
```

This will make a sample chat completion call to GPT-3.5-turbo and print the response.

## Customization

- To use a different model (e.g., GPT-4), change the `model` parameter in the script.
- Modify the `messages` list to change the conversation.
- Adjust `max_tokens` and `temperature` for different response behaviors.

## Troubleshooting

- If you get an "API key not set" error, ensure the environment variable is properly set.
- Check your OpenAI account for API usage limits and billing.
- For more details, refer to the [OpenAI API documentation](https://platform.openai.com/docs).