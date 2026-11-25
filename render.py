import os, re, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

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
    title_font = ImageFont.truetype(font_path, 72) if font_path else ImageFont.load_default()
    body_font = ImageFont.truetype(font_path, 43) if font_path else ImageFont.load_default()
    small_font = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()

    draw.rounded_rectangle((70, 110, 1010, 180), radius=24, fill=(25, 45, 70))
    draw.text((105, 125), "TECNOLOGIA  •  IA", font=small_font, fill=ACCENT)

    y = 310
    for line in textwrap.wrap(title, width=22):
        draw.text((85, y), line, font=title_font, fill=WHITE)
        y += 95
    draw.rounded_rectangle((85, y + 35, 995, y + 43), radius=4, fill=ACCENT)

    excerpt = re.sub(r"\s+", " ", narration).strip()
    words = excerpt.split()
    excerpt = " ".join(words[:42])
    y += 120
    for line in textwrap.wrap(excerpt, width=34):
        draw.text((90, y), line, font=body_font, fill=MUTED)
        y += 62
    draw.text((85, 1740), "Siga para mais conteúdo sobre tecnologia", font=small_font, fill=ACCENT)
    image.save(output_path, quality=95)

def make_video(video, output_dir, index):
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.join(output_dir, f"video_{index:02d}")
    png = base + ".png"
    mp4 = base + ".mp4"
    render_card(video["title"], video["narration"], png)

    # MVP: vídeo vertical com cartão visual e narração via arquivo WAV opcional.
    # Sem WAV, cria um vídeo silencioso para validar o fluxo; TTS será adicionado na próxima etapa.
    duration = max(25, min(50, len(video["narration"].split()) / 2.4))
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", png,
        "-t", str(duration), "-r", "30",
        "-vf", "scale=1080:1920,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-movflags", "+faststart", mp4
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return mp4
