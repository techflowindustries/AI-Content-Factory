
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
        "model": "openai/gpt-oss-120b",
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

        if response.status_code in [429, 500, 502, 503, 504]:
            if attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue

        if not response.ok:
            raise RuntimeError(
                f"Erro Groq {response.status_code}: {response.text}"
            )

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return json.loads(content)

    raise RuntimeError("Não foi possível gerar conteúdo com o Groq.")
    
