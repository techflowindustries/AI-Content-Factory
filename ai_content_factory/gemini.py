
import os
import json
import time
import requests

API_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_json(prompt):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY não configurada.")

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    for attempt in range(5):
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=90
        )

        if response.status_code in [429, 500, 502, 503, 504] and attempt < 4:
            time.sleep(2 ** (attempt + 1))
            continue

        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)

    raise RuntimeError("Não foi possível gerar conteúdo com o Groq.")
