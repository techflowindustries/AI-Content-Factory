
import asyncio
from pathlib import Path
import edge_tts

VOICE = "pt-BR-AntonioNeural"


async def _generate_audio(text, output_path):
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="+0%",
        volume="+0%",
        pitch="+0Hz"
    )

    await communicate.save(str(output_path))


def generate_audio(text, output_path):
    if not text or not text.strip():
        raise RuntimeError("O texto da narração está vazio.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    asyncio.run(
        _generate_audio(text.strip(), output_path)
    )

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("O Edge TTS não conseguiu gerar o áudio.")

    return str(output_path)
