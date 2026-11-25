import json, os, sys
from pathlib import Path
from dotenv import load_dotenv
from ai_content_factory.research import collect_items
from ai_content_factory.writer import create_scripts
from ai_content_factory.render import make_video

ROOT = Path(__file__).resolve().parent

def main():
    load_dotenv(ROOT / ".env")
    settings = json.loads((ROOT / "config/settings.json").read_text(encoding="utf-8"))
    data_dir = Path(os.getenv("DATA_DIR", ROOT / "data"))
    output_dir = Path(os.getenv("OUTPUT_DIR", ROOT / "output"))
    data_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    feeds = settings["sources"]
    items = collect_items(feeds)
    if not items:
        raise RuntimeError("Não foi possível coletar pautas dos feeds.")
    (data_dir / "research.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    count = int(os.getenv("VIDEOS_PER_RUN", "1"))
    scripts = create_scripts(items, count=count)
    manifest = []
    for index, video in enumerate(scripts, start=1):
        path = make_video(video, output_dir, index)
        record = {**video, "video_path": str(path)}
        manifest.append(record)

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Concluído: {len(manifest)} vídeo(s) gerado(s).")
    for item in manifest:
        print(item["video_path"])

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise
