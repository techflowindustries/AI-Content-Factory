"""ElevenLabs text-to-speech adapter for What-If narration."""
import os
from pathlib import Path

import requests


API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


def generate_elevenlabs_audio(text: str, output_path: str) -> str:
    """Generate an MP3 from the English narrator script.

    Required GitHub Actions secrets:
      ELEVENLABS_API_KEY
    Required repository variable or secret:
      ELEVENLABS_VOICE_ID (choose a voice in the ElevenLabs Voice Library)

    Optional environment variables:
      ELEVENLABS_MODEL_ID (default: eleven_v4)
      ELEVENLABS_OUTPUT_FORMAT (default: mp3_44100_128)
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v4")
    output_format = os.getenv("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")

    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY não configurada.")
    if not voice_id:
        raise RuntimeError(
            "ELEVENLABS_VOICE_ID não configurado. Escolha uma voz na Voice Library "
            "e cadastre o ID como variável/secret no GitHub."
        )
    if not text or not text.strip():
        raise RuntimeError("O texto da narração está vazio.")

    response = requests.post(
        API_URL.format(voice_id=voice_id),
        params={"output_format": output_format},
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": text.strip(),
            "model_id": model_id,
            "language_code": "en",
        },
        timeout=180,
    )
    if not response.ok:
        # Never include request headers or the API key in error output.
        raise RuntimeError(
            f"ElevenLabs retornou HTTP {response.status_code}: "
            f"{response.text[:1200]}"
        )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)

    if not destination.exists() or destination.stat().st_size < 1000:
        raise RuntimeError("A ElevenLabs não retornou um arquivo de áudio válido.")

    return str(destination)
