import os
from typing import Optional
from dotenv_demo import load_dotenv
import anthropic


def list_available_models() -> list[dict]:
    """
    Fetches and displays all available Claude models from the Anthropic API.
    Returns a list of model information.
    """
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env file.")
        return []
    
    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        models = client.models.list()
        model_list = list(models.data)
        return model_list
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []


def display_models(models: list[dict]) -> Optional[str]:
    """
    Display available models and let user select one.
    Returns the selected model ID or None if no models available.
    """
    if not models:
        print("No models available.")
        return None
    
    print("\n" + "="*60)
    print("Available Claude Models:")
    print("="*60)
    
    for i, model in enumerate(models, 1):
        print(f"{i}. {model.id}")
        if hasattr(model, 'display_name') and model.display_name:
            print(f"   Display Name: {model.display_name}")
        if hasattr(model, 'created_at') and model.created_at:
            print(f"   Created: {model.created_at}")
        print()
    
    # Prompt user to select a model
    while True:
        try:
            choice = input(f"Select a model (1-{len(models)}, default 1): ").strip()
            if choice == "":
                return models[0].id
            model_index = int(choice) - 1
            if 0 <= model_index < len(models):
                return models[model_index].id
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(models)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(models)}.")


def call_claude_api(prompt: str, model: str) -> str:
    """
    Calls the Claude API with the given prompt and returns the response.
    
    Args:
        prompt: The user's input prompt
        model: The model ID to use
    
    Returns:
        The generated response from Claude
    """
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env file.")
        return "API call failed: Missing API key."
    
    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return "API call failed. See error above."


def main():
    """
    Main function to orchestrate the Claude LLM interaction.
    Lists models first (before prompting for user input) to avoid rate limiting issues.
    """
    print("Initializing Claude LLM interface...")
    
    # List and display available models BEFORE prompting for user input
    print("\nFetching available Claude models...")
    models = list_available_models()
    
    if not models:
        print("Could not retrieve available models. Exiting.")
        return
    
    # Display models and get selection
    selected_model = display_models(models)
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
    print("Calling Claude API...")
    print("="*60)
    
    # Call the Claude API
    response = call_claude_api(prompt, selected_model)
    
    print("\nResponse from Claude:")
    print("-" * 60)
    print(response)
    print("-" * 60)


if __name__ == "__main__":
    main()
