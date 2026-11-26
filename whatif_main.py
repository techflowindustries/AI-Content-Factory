"""Daily What-If video pipeline: ideas -> story -> 3 chained clips -> narration."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from ai_content_factory.whatif_writer import create_story_package
from ai_content_factory.whatif_tts import generate_elevenlabs_audio
from ai_content_factory.whatif_video import (
    assemble_final_video, extract_last_frame, generate_clip, normalize_clip
)


ROOT = Path(__file__).resolve().parent


def main() -> None:
    load_dotenv(ROOT / ".env")
    output_dir = Path(os.getenv("OUTPUT_DIR", ROOT / "output"))
    work_dir = Path(os.getenv("WORK_DIR", ROOT / "work"))
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    print("1/5 — Criando 10 ideias e selecionando a melhor...")
    story = create_story_package()
    (work_dir / "story.json").write_text(
        json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    normalized = []
    previous_frame = None
    for number, clip in enumerate(story["clips"], start=1):
        raw_path = work_dir / f"clip_{number}_raw.mp4"
        frame_path = work_dir / f"clip_{number}_first_frame.jpg"
        normalized_path = work_dir / f"clip_{number}.mp4"

        print(f"2/5 — Gerando clipe {number}/3...")
        prompt = clip["prompt"]
        if number > 1:
            prompt += (
                "\n\nCONTINUITY REQUIREMENT: The supplied image is the exact final "
                "frame of the immediately preceding clip. Treat it as the literal first "
                "frame of this clip. Continue the same shot state, character designs, "
                "positions, props, lighting and environment. Do not redesign or restart."
            )
        generate_clip(prompt, raw_path, previous_frame)
        normalize_clip(raw_path, normalized_path)
        normalized.append(str(normalized_path))

        if number < 3:
            previous_frame = extract_last_frame(normalized_path, frame_path)

    print("3/5 — Gerando narração em inglês com a voz Roger...")
    audio_path = work_dir / "narration.mp3"
    generate_elevenlabs_audio(story["full_narration"], str(audio_path))

    print("4/5 — Montando o MP4 vertical de 30 segundos...")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in story["title"])[:60]
    final_path = output_dir / f"{safe_title or 'what_if_story'}.mp4"
    assemble_final_video(normalized, str(audio_path), final_path)

    story["final_video"] = str(final_path)
    (output_dir / "manifest.json").write_text(
        json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"5/5 — Concluído. Vídeo pronto para revisão: {final_path}")


if __name__ == "__main__":
    main()
