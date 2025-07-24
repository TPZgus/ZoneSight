
import requests
import json

OLLAMA_HOST = "http://localhost:11434"

def analyze_text_with_gemma(prompt, model="gemma:2b"):
    """
    Analyzes text using a local Gemma model served by Ollama.
    """
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        
        # Extract the JSON content from the response
        response_json = response.json()
        return response_json.get("response", "")

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return None
