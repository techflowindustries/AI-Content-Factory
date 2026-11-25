
import json
from .gemini import generate_json


def create_scripts(items, count=1):
    if not items:
        raise RuntimeError("Nenhuma pauta foi encontrada nos feeds RSS.")

    videos = []

    for item in items[:count * 2]:
        if len(videos) >= count:
            break

        prompt = f"""
Você é editor de um canal brasileiro sobre tecnologia e inteligência artificial.

Crie UM roteiro curto e original para vídeo vertical informativo.

Use somente fatos sustentados pela pauta. Não invente números, datas,
falas, testes ou citações.

Português brasileiro natural, sem clickbait enganoso.
Duração aproximada: 35 a 45 segundos.

Retorne APENAS JSON neste formato:
{{
  "videos": [
    {{
      "title": "título",
      "hook": "gancho inicial",
      "narration": "narração completa",
      "caption": "descrição para publicação",
      "hashtags": ["#tecnologia"],
      "sources": [
        {{"title": "título da pauta", "url": "URL"}}
      ],
      "visuals": [
        "descrição visual da cena 1",
        "descrição visual da cena 2"
      ]
    }}
  ]
}}

PAUTA:
{json.dumps(item, ensure_ascii=False)}
"""

        result = generate_json(prompt)
        generated = result.get("videos", [])

        if generated:
            videos.append(generated[0])

    if not videos:
        raise RuntimeError("A IA não retornou roteiros.")

    return videos
