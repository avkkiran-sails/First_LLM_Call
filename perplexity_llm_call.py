import os
from typing import Optional
from dotenv_demo import load_dotenv
from openai import OpenAI


# Perplexity available models
PERPLEXITY_MODELS = [
    {
        "id": "llama-3.1-sonar-huge-128k-online",
        "name": "Llama 3.1 Sonar Huge (128K)",
        "description": "Most capable, processes up to 128K tokens, has web search"
    },
    {
        "id": "llama-3.1-sonar-large-128k-online",
        "name": "Llama 3.1 Sonar Large (128K)",
        "description": "Large model, 128K context, includes web search"
    },
    {
        "id": "llama-3.1-sonar-small-128k-online",
        "name": "Llama 3.1 Sonar Small (128K)",
        "description": "Fast and efficient, 128K context, includes web search"
    },
    {
        "id": "llama-3.1-sonar-huge-128k-chat",
        "name": "Llama 3.1 Sonar Huge (Chat)",
        "description": "Most capable chat model, optimized for conversations"
    },
    {
        "id": "llama-3.1-sonar-large-128k-chat",
        "name": "Llama 3.1 Sonar Large (Chat)",
        "description": "Large chat model, optimized for conversations"
    }
]


def display_models() -> Optional[str]:
    """
    Display available Perplexity models and let user select one.
    Returns the selected model ID or None if user cancels.
    """
    print("\n" + "="*60)
    print("Available Perplexity Models:")
    print("="*60)
    
    for i, model in enumerate(PERPLEXITY_MODELS, 1):
        print(f"{i}. {model['name']} ({model['id']})")
        print(f"   {model['description']}")
        print()
    
    # Prompt user to select a model
    while True:
        try:
            choice = input(f"Select a model (1-{len(PERPLEXITY_MODELS)}, default 1): ").strip()
            if choice == "":
                return PERPLEXITY_MODELS[0]["id"]
            model_index = int(choice) - 1
            if 0 <= model_index < len(PERPLEXITY_MODELS):
                return PERPLEXITY_MODELS[model_index]["id"]
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(PERPLEXITY_MODELS)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(PERPLEXITY_MODELS)}.")


def call_perplexity_api(prompt: str, model: str) -> str:
    """
    Calls the Perplexity API with the given prompt and returns the response.
    
    Args:
        prompt: The user's input prompt
        model: The model ID to use
    
    Returns:
        The generated response from Perplexity
    """
    load_dotenv()
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("Error: PERPLEXITY_API_KEY not found in .env file.")
        return "API call failed: Missing API key."
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai"
    )
    
    try:
        message = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.choices[0].message.content
    except Exception as e:
        print(f"Error calling Perplexity API: {e}")
        return "API call failed. See error above."


def main():
    """
    Main function to orchestrate the Perplexity LLM interaction.
    Lists models first (before prompting for user input) to avoid rate limiting issues.
    """
    print("Initializing Perplexity LLM interface...")
    
    # Display available models and let user select
    print("\nFetching available Perplexity models...")
    selected_model = display_models()
    
    if not selected_model:
        return
    
    print("="*60)
    print(f"Selected model: {selected_model}")
    print("="*60)
    
    # Now prompt the user for input
    print("\nEnter your prompt (press Enter twice to submit):")
    print("-" * 60)
    
    lines = []
    empty_lines = 0
    
    while True:
        try:
            line = input()
            if line == "":
                empty_lines += 1
                if empty_lines >= 1:  # Change to 2 if you want to require two empty lines
                    break
            else:
                empty_lines = 0
                lines.append(line)
        except EOFError:
            break
    
    prompt = "\n".join(lines)
    
    if not prompt.strip():
        print("No prompt provided. Exiting.")
        return
    
    print("\n" + "="*60)
    print("Calling Perplexity API...")
    print("="*60)
    
    # Call the Perplexity API
    response = call_perplexity_api(prompt, selected_model)
    
    print("\nResponse from Perplexity:")
    print("-" * 60)
    print(response)
    print("-" * 60)


if __name__ == "__main__":
    main()
