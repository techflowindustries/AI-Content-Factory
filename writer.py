import json
from .gemini import generate_json

def create_scripts(items, count=1):
    if not items:
        raise RuntimeError("Nenhuma pauta foi encontrada nos feeds RSS.")
    prompt = f"""
Você é editor de um canal brasileiro sobre tecnologia e inteligência artificial.
Crie {count} roteiros CURTOS e originais para vídeos verticais informativos.
Use somente fatos sustentados pelas pautas abaixo. Não invente números, datas,
falas, testes ou citações. Se a pauta não tiver informação suficiente, descarte-a.
Não copie títulos ou textos das fontes. Transforme o assunto em explicação original.
Cada roteiro deve ter gancho inicial, desenvolvimento claro e conclusão.
Português brasileiro natural, sem clickbait enganoso.
Duração aproximada: 35 a 45 segundos.
Retorne APENAS JSON no formato:
{{
  "videos": [
    {{
      "title": "título",
      "hook": "gancho falado",
      "narration": "texto integral da narração",
      "caption": "descrição para publicação",
      "hashtags": ["#tecnologia"],
      "sources": [{{"title": "título da pauta", "url": "URL"}}],
      "visuals": ["descrição visual da cena 1", "descrição visual da cena 2"]
    }}
  ]
}}
PAUTAS:
{json.dumps(items[:25], ensure_ascii=False)}
"""
    result = generate_json(prompt)
    videos = result.get("videos", [])
    if not videos:
        raise RuntimeError("A IA não retornou roteiros.")
    return videos[:count]
