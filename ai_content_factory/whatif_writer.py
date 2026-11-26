"""What-If story planning for the automated 30-second video workflow.

This module only generates structured text. It does not call the video-generation
endpoint, so adding it to the repository does not incur video-generation costs.
"""
import json
import os
import re
from typing import Any

import requests


GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_TEXT_MODEL = "gemini-2.5-flash"

VISUAL_STYLE = """
MANDATORY VISUAL STYLE — repeat this specification in every clip prompt:
People are strictly flat 2D illustrated animation cels composited into a
dimensional stylized 3D environment. Each character has a solid white circular
face with a thick consistent dark outline, flat black oval eyes, separate
graphic eyebrows, a simple drawn mouth, flat solid-color hair and clothing,
a small narrow torso, extremely thin black line arms and legs, small flat
rounded hands, and minimal feet. No character thickness, sculpted cheeks,
spherical skulls, cylindrical limbs, volumetric clothing, realistic anatomy,
skin texture, gradients, highlights, or ambient shading on characters.
Characters may cast shadows onto the 3D ground, but faces and clothes remain
flat and unshaded. Animate like expressive 2D puppets using joint rotations,
small body bounces, deliberate head tilts, and replacement facial expressions.
Only environments and props are shaded 3D: dimensional scenery, perspective,
material textures, gentle ambient shading, directional light, and contact
shadows. Use rich readable colors and strong foreground/background separation.
Use smooth camera tracks, dollies, gentle push-ins, high-angle inserts,
reaction close-ups, and clean cuts. Never use rounded 3D characters, anime
faces, photoreal people, whiteboard animation, or flat vector environments.
All clips are silent: no dialogue, lip-sync, narration, music, sound effects,
captions, speech bubbles, logos, watermarks, or unnecessary written labels.
"""


def _gemini_json(prompt: str) -> dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_TEXT_MODEL", DEFAULT_TEXT_MODEL)
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada nos Secrets do GitHub.")

    response = requests.post(
        f"{GEMINI_API_BASE}/models/{model}:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.8,
            },
        },
        timeout=120,
    )
    if not response.ok:
        detail = response.text[:1500]
        raise RuntimeError(f"Gemini ({response.status_code}): {detail}")

    payload = response.json()
    try:
        raw = payload["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("A Gemini não retornou JSON válido.") from exc


def _word_count(text: str) -> int:
    return len(re.findall(r"\\b[\\w’'-]+\\b", text))


def choose_best_idea() -> dict[str, Any]:
    """Generate ten What-If premises, score them, and select the strongest."""
    prompt = """
You are the story editor for a short-form What-If animated story channel.
Invent exactly 10 distinct, original fictional What-If premises suitable for
a 30-second vertical animated story. Vary locations, objects, rules and stakes.
Avoid repeatedly using buttons, mirrors, time-freeze devices or horror.
Every premise must be understandable visually and achievable in three clips.

Score each idea from 1 to 10 on:
- hook_strength
- originality
- visual_potential
- retention_and_escalation
- ending_payoff

Choose the idea with the strongest combined score, not merely the most shocking.
Do not present invented events as real facts. Viral performance is uncertain;
do not claim that any idea is guaranteed to go viral.

Return JSON only:
{
  "ideas": [
    {
      "id": 1,
      "title": "short title",
      "hook": "one-sentence curiosity hook",
      "premise": "clear one-sentence What-If premise",
      "scores": {
        "hook_strength": 1,
        "originality": 1,
        "visual_potential": 1,
        "retention_and_escalation": 1,
        "ending_payoff": 1
      },
      "total_score": 0
    }
  ],
  "selected_idea_id": 1,
  "selection_reason": "brief explanation"
}
"""
    result = _gemini_json(prompt)
    ideas = result.get("ideas", [])
    if len(ideas) != 10:
        raise RuntimeError(f"A Gemini deveria retornar 10 ideias; retornou {len(ideas)}.")
    selected_id = result.get("selected_idea_id")
    selected = next((idea for idea in ideas if idea.get("id") == selected_id), None)
    if not selected:
        raise RuntimeError("A Gemini não selecionou uma das 10 ideias.")
    return {"ideas": ideas, "selected_idea": selected, "selection_reason": result.get("selection_reason", "")}


def create_30_second_story(selection: dict[str, Any]) -> dict[str, Any]:
    """Expand the selected premise into three connected 10-second clips."""
    idea = selection["selected_idea"]
    prompt = f"""
Create a complete production package for this selected fictional What-If story.
Do not change its central premise. The final video is exactly 30 seconds:
exactly THREE connected clips, each exactly 10 seconds, vertical 9:16.

Selected premise:
{json.dumps(idea, ensure_ascii=False)}

Story requirements:
- Plan a clear curiosity hook, escalation, and satisfying visual twist/ending.
- Keep the cast manageable and designs unmistakable.
- Establish a story rule and obey it consistently.
- The ending of clip 1 must exactly match the opening of clip 2; same for 2 to 3.
- Clip 1 starts without a reference image. Clips 2 and 3 start from the previous
  clip's actual final clean frame, which the workflow will extract.
- Each clip prompt must stand alone and explicitly describe every visible
  character, the current setting, lighting, props and their current states.
- Each clip prompt must include 2–4 timed beats totalling exactly 10 seconds,
  camera framing/movement, expressions, action and a precise final-frame state.
- End clips 1 and 2 with a readable, unobscured composition held for about
  half a second. Clip 2 and 3 must resume the movement without replaying the hold.
- Preserve positions, movement direction, expressions, clothes, lighting,
  prop placement and environmental changes at clip boundaries.
- Vanished/destroyed objects and characters stay gone unless the story restores
  them explicitly. Do not reset the environment.
- Include the complete visual specification below in EVERY clip prompt, not
  a shortcut such as "same style as before".
- Clips must be silent, with no dialogue, lip-sync, narration, music, sound
  effects, captions, speech bubbles, logos, watermarks or unnecessary text.
- Narration is English, separate from the video, approximately 20–25 words
  for each 10-second clip. Align spoken events with visible action. Do not pad.
- The complete narration is the three sections joined, with no timestamps.

VISUAL SPECIFICATION TO INCLUDE VERBATIM IN EACH CLIP PROMPT:
{VISUAL_STYLE}

Return JSON only with this shape:
{{
  "title": "story title",
  "summary": "brief story summary",
  "duration_seconds": 30,
  "aspect_ratio": "9:16",
  "clip_count": 3,
  "continuity_guide": {{
    "cast": ["complete fixed character designs"],
    "setting": "location, palette, lighting and spatial layout",
    "story_rule": "what causes consequences and what changes"
  }},
  "clips": [
    {{
      "clip_number": 1,
      "timeline": "00:00-00:10",
      "prompt": "complete detailed generation prompt, including visual specification",
      "final_frame": "precise composition to carry into next clip",
      "narration": "20-25 English words"
    }}
  ],
  "voice_direction": "English narrator tone, pace, emotional progression and pauses",
  "full_narration": "all three narration sections joined cleanly"
}}

There must be exactly 3 clips. Include every required field. Do not put any
narration, subtitles, music or sound effects inside the video prompts.
"""
    story = _gemini_json(prompt)
    clips = story.get("clips", [])
    if len(clips) != 3:
        raise RuntimeError(f"A história precisa ter 3 clipes; recebidos: {len(clips)}.")

    for expected, clip in enumerate(clips, start=1):
        if clip.get("clip_number") != expected:
            raise RuntimeError("Os clipes precisam estar numerados em ordem de 1 a 3.")
        narration = (clip.get("narration") or "").strip()
        count = _word_count(narration)
        if not 16 <= count <= 28:
            raise RuntimeError(
                f"Narração do clipe {expected} tem {count} palavras; esperado cerca de 20–25."
            )
        clip_prompt = clip.get("prompt", "")
        if "MANDATORY VISUAL STYLE" not in clip_prompt or "flat 2D" not in clip_prompt.lower():
            raise RuntimeError(f"O prompt do clipe {expected} não contém o estilo visual obrigatório.")
        if expected > 1 and "previous clip" not in clip_prompt.lower():
            raise RuntimeError(f"O clipe {expected} não instrui a continuidade por frame anterior.")

    story["duration_seconds"] = 30
    story["aspect_ratio"] = "9:16"
    story["clip_count"] = 3
    story["selected_idea"] = idea
    story["idea_scores"] = idea.get("scores", {})
    story["full_narration"] = " ".join(
        clip["narration"].strip() for clip in clips
    )
    return story


def create_story_package() -> dict[str, Any]:
    selection = choose_best_idea()
    story = create_30_second_story(selection)
    story["idea_selection_reason"] = selection["selection_reason"]
    story["all_candidate_ideas"] = selection["ideas"]
    return story
