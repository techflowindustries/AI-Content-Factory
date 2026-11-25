
import os
import json
import time
import requests

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

def generate_json(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada.")

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }

    retry_codes = {408, 429, 500, 502, 503, 504}

    for attempt in range(5):
        try:
            response = requests.post(
                API_URL.format(model=model),
                params={"key": api_key},
                json=payload,
                timeout=90
            )

            if response.status_code in retry_codes:
                if attempt == 4:
                    response.raise_for_status()

                wait = 2 ** attempt
                print(
                    f"Gemini indisponível ({response.status_code}). "
                    f"Nova tentativa em {wait}s..."
                )
                time.sleep(wait)
                continue

            response.raise_for_status()

            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]

            return json.loads(text)

        except requests.exceptions.Timeout:
            if attempt == 4:
                raise

            wait = 2 ** attempt
            print(f"Timeout. Tentando novamente em {wait}s...")
            time.sleep(wait)

    raise RuntimeError("Não foi possível gerar conteúdo após 5 tentativas.")
