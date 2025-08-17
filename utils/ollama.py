import requests
import json
import os

# %%
import typing # Import typing module

def ask_ollama(
    user_prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
    model: str = "gemma3:latest",
    response_format: str = "text", # Renamed 'format' to 'response_format' to avoid conflict with built-in function
    temperature: float = 0.0, # Renamed 'temp' to 'temperature' for clarity and consistency
    max_tokens: typing.Optional[int] = None, # Changed default to None, will omit from payload if None, updated type hint
) -> str | bool:
    """
    Sends a prompt to the Ollama API and returns the response.

    Args:
        user_prompt: The main prompt for the model.
        system_prompt: The system message to guide the model's behavior.
        model: The name of the Ollama model to use.
        response_format: The desired format of the response (e.g., "json", "text").
        temperature: The temperature for the model's generation.
        max_tokens: The maximum number of tokens in the response.

    Returns:
        The model's response as a string, or False if an error occurred.
    """

    # Define the endpoint URL and headers
    # Use environment variable OLLAMA_API_URL, default to localhost
    url = os.getenv("OLLAMA_API_URL", "http://localhost:11434") + "/api/generate"
    headers = {
        "Content-Type": "application/json",
    }

    # Define the payload with the prompt or input text
    payload = {
        "model": model,
        "system": system_prompt, # Corrected system prompt formatting
        "prompt": user_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "format": response_format, # Added format to options
        },
    }

    # Add max_tokens to payload if provided
    if max_tokens is not None:
        payload["options"]["num_predict"] = max_tokens # Ollama uses num_predict for max_tokens

    # Make the POST request
    response = None # Initialize response to None
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()
        return result.get("response", "") # Use .get for safer access

    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        return False
    except json.JSONDecodeError:
        # Check if response is not None before accessing .text
        error_text = response.text if response is not None else "No response received"
        print(f"Error decoding JSON response from Ollama API: {error_text}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
