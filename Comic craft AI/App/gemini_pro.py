import json
import os
from typing import List

from .models import PanelOutline, StoryPanel


def _demo_story(
    outline: List[PanelOutline],
    character_name: str,
    tone: str,
) -> List[StoryPanel]:

    demo_dialogues = [
        f"{character_name}: I have a feeling this adventure is only beginning.",
        f"{character_name}: What could this strange discovery mean?",
        f"{character_name}: I can't turn back now.",
        f"{character_name}: I finally understand what I have to do!",
        f"{character_name}: Every adventure teaches us something new.",
    ]

    demo_captions = [
        "A mysterious journey begins...",
        "Something unexpected appears.",
        "The danger grows closer.",
        "Everything changes in an instant.",
        "The adventure reaches its peaceful conclusion.",
    ]

    panels: List[StoryPanel] = []

    for index, item in enumerate(outline):

        panels.append(
            StoryPanel(
                panel_number=item.panel_number,
                title=item.title,
                scene_description=item.scene_description,
                image_prompt=item.image_prompt,
                caption=demo_captions[index],
                narration=(
                    f"{character_name} moves through the scene with a "
                    f"{tone} determination. "
                    f"The events of this moment push the story forward."
                ),
                dialogue=demo_dialogues[index],
            )
        )

    return panels


def generate_story(
    outline: List[PanelOutline],
    character_name: str,
    tone: str,
    story_prompt: str,
) -> List[StoryPanel]:

    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    if demo_mode:
        return _demo_story(
            outline,
            character_name,
            tone,
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to .env "
            "or enable DEMO_MODE."
        )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    model_name = os.getenv(
        "GEMINI_PRO_MODEL",
        "gemini-2.5-pro",
    )

    outline_json = [
        item.model_dump()
        for item in outline
    ]

    prompt = f"""
You are the professional comic writer for ComicCraft.

Original story idea:
{story_prompt}

Main character:
{character_name}

Tone:
{tone}

Here is the approved five-panel outline:

{json.dumps(outline_json, indent=2)}

Expand every panel into a polished comic scene.

Return ONLY valid JSON.

Return an array of exactly 5 objects.

Every object must contain:

panel_number
title
scene_description
image_prompt
caption
narration
dialogue

Requirements:

1. Keep the same panel numbers.
2. Keep the same basic story progression.
3. Make narration concise enough for a comic page.
4. Make dialogue natural.
5. Keep the main character consistent.
6. Make each image_prompt visually descriptive.
7. Do not add markdown.
8. Do not add explanations outside JSON.
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty story.")

    raw = json.loads(response.text)

    if not isinstance(raw, list):
        raise RuntimeError("Gemini story response is not a list.")

    panels = [
        StoryPanel.model_validate(panel)
        for panel in raw
    ]

    if len(panels) != 5:
        raise RuntimeError(
            f"Gemini returned {len(panels)} panels instead of 5."
        )

    return panels