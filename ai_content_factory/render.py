
import os
import re
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from .tts import generate_audio

W, H = 1080, 1920

BG = (12, 18, 30)
WHITE = (245, 247, 250)
ACCENT = (86, 170, 255)
MUTED = (170, 185, 205)


def find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


def render_card(title, narration, output_path):
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)

    font_path = find_font()

    title_font = (
        ImageFont.truetype(font_path, 72)
        if font_path else ImageFont.load_default()
    )

    body_font = (
        ImageFont.truetype(font_path, 43)
        if font_path else ImageFont.load_default()
    )

    small_font = (
        ImageFont.truetype(font_path, 30)
        if font_path else ImageFont.load_default()
    )

    draw.rounded_rectangle(
        (70, 110, 1010, 180),
        radius=24,
        fill=(25, 45, 70)
    )

    draw.text(
        (105, 125),
        "TECNOLOGIA  •  IA",
        font=small_font,
        fill=ACCENT
    )

    y = 310

    for line in textwrap.wrap(title, width=22):
        draw.text(
            (85, y),
            line,
            font=title_font,
            fill=WHITE
        )
        y += 95

    draw.rounded_rectangle(
        (85, y + 35, 995, y + 43),
        radius=4,
        fill=ACCENT
    )

    excerpt = re.sub(r"\s+", " ", narration).strip()
    words = excerpt.split()
    excerpt = " ".join(words[:42])

    y += 120

    for line in textwrap.wrap(excerpt, width=34):
        draw.text(
            (90, y),
            line,
            font=body_font,
            fill=MUTED
        )
        y += 62

    draw.text(
        (85, 1740),
        "Siga para mais conteúdo sobre tecnologia",
        font=small_font,
        fill=ACCENT
    )

    image.save(output_path)


def make_video(video, output_dir, index):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base = output_dir / f"video_{index:02d}"

    png = base.with_suffix(".png")
    mp3 = base.with_suffix(".mp3")
    mp4 = base.with_suffix(".mp4")

    title = video["title"]
    narration = video["narration"]

    # 1. Criar a imagem do vídeo
    render_card(title, narration, str(png))

    # 2. Gerar a narração masculina brasileira
    generate_audio(narration, str(mp3))

    # 3. Combinar imagem e áudio
    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-framerate", "30",
        "-i", str(png),
        "-i", str(mp3),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(mp4)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Erro ao montar vídeo com FFmpeg: {result.stderr[-3000:]}"
        )

    if not mp4.exists() or mp4.stat().st_size == 0:
        raise RuntimeError("O vídeo MP4 não foi criado.")

    return str(mp4)
