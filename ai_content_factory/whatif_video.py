"""Gemini Omni video generation with chained last-frame continuity."""
import base64
import os
import subprocess
from pathlib import Path

import requests

INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT_MODEL = "gemini-omni-1.2-flash"


def _run_ffmpeg(args: list[str]) -> None:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
        capture_output=True, text=True
    )
    if result.returncode:
        raise RuntimeError(f"FFmpeg falhou: {result.stderr[-1800:]}")


def extract_last_frame(video_path: str | Path, image_path: str | Path) -> str:
    """Extract the actual final decoded frame from a generated clip."""
    destination = Path(image_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg([
        "-sseof", "-0.08", "-i", str(video_path),
        "-frames:v", "1", "-q:v", "2", str(destination)
    ])
    if not destination.exists() or destination.stat().st_size < 1000:
        raise RuntimeError(f"Não foi possível extrair o último frame de {video_path}.")
    return str(destination)


def _video_from_response(payload: dict) -> bytes:
    for step in payload.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for item in step.get("content", []):
            if item.get("type") == "video" and item.get("data"):
                return base64.b64decode(item["data"])
    raise RuntimeError(
        "A Gemini não retornou MP4 inline. "
        f"Status: {payload.get('status', 'desconhecido')}; "
        f"resposta: {str(payload)[:1000]}"
    )


def generate_clip(prompt: str, output_path: str | Path,
                  first_frame_path: str | Path | None = None) -> str:
    """Generate a 10-second 9:16 clip; optionally condition on a prior final frame."""
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_VIDEO_MODEL", DEFAULT_MODEL)
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada nos Secrets do GitHub.")

    if first_frame_path:
        image_bytes = Path(first_frame_path).read_bytes()
        inputs = [
            {
                "type": "image",
                "data": base64.b64encode(image_bytes).decode("ascii"),
                "mime_type": "image/png" if str(first_frame_path).lower().endswith(".png") else "image/jpeg",
            },
            {"type": "text", "text": prompt},
        ]
        task = "image_to_video"
    else:
        inputs = prompt
        task = "text_to_video"

    body = {
        "model": model,
        "input": inputs,
        "generation_config": {"video_config": {"task": task}},
        "response_format": {
            "type": "video",
            "duration": "10s",
            "resolution": os.getenv("GEMINI_VIDEO_RESOLUTION", "720p"),
            "aspect_ratio": "9:16",
        },
    }
    response = requests.post(
        INTERACTIONS_URL,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json=body,
        timeout=900,
    )
    if not response.ok:
        raise RuntimeError(
            f"Gemini vídeo retornou HTTP {response.status_code}: {response.text[:1800]}"
        )

    video_bytes = _video_from_response(response.json())
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(video_bytes)
    if destination.stat().st_size < 10_000:
        raise RuntimeError("O arquivo de vídeo retornado é pequeno demais.")
    return str(destination)


def normalize_clip(source: str | Path, destination: str | Path) -> str:
    """Standardize each generated clip to silent 1080x1920 H.264, 24 fps, 10 sec."""
    _run_ffmpeg([
        "-i", str(source), "-an",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,setsar=1",
        "-t", "10", "-r", "24", "-c:v", "libx264", "-preset", "medium",
        "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(destination),
    ])
    return str(destination)


def assemble_final_video(clips: list[str], narration_audio: str,
                         output_path: str | Path) -> str:
    """Concatenate three silent clips and lay the separate narration over them."""
    if len(clips) != 3:
        raise RuntimeError("A montagem exige exatamente três clipes.")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    concat_file = output.parent / "clips_concat.txt"
    concat_file.write_text(
        "".join(f"file '{Path(p).resolve().as_posix()}'\n" for p in clips),
        encoding="utf-8"
    )
    _run_ffmpeg([
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(narration_audio),
        "-filter_complex", "[1:a]apad=pad_dur=30[a]",
        "-map", "0:v:0", "-map", "[a]",
        "-t", "30", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(output),
    ])
    if not output.exists() or output.stat().st_size < 100_000:
        raise RuntimeError("O MP4 final não foi criado corretamente.")
    return str(output)
