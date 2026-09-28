import json
import os
from typing import List

from .models import PanelOutline


def _demo_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[PanelOutline]:
    """
    Generates a deterministic outline for local/demo testing.
    """

    return [
        PanelOutline(
            panel_number=1,
            title="The Beginning",
            scene_description=(
                f"{character_name} begins an unexpected adventure in {setting}. "
                f"The atmosphere feels {tone}."
            ),
            image_prompt=(
                f"{character_name} standing at the entrance of {setting}, "
                f"dramatic comic composition, {art_style} style, "
                f"cinematic lighting, highly detailed"
            ),
        ),
        PanelOutline(
            panel_number=2,
            title="A Strange Discovery",
            scene_description=(
                f"{character_name} discovers something mysterious while "
                f"exploring {setting}."
            ),
            image_prompt=(
                f"{character_name} discovering a mysterious object in {setting}, "
                f"expressive face, comic panel composition, {art_style} style, "
                f"cinematic lighting"
            ),
        ),
        PanelOutline(
            panel_number=3,
            title="The Challenge",
            scene_description=(
                f"A major challenge appears and {character_name} must decide "
                f"whether to continue."
            ),
            image_prompt=(
                f"{character_name} facing a dramatic challenge in {setting}, "
                f"action pose, dynamic comic composition, {art_style} style, "
                f"high detail"
            ),
        ),
        PanelOutline(
            panel_number=4,
            title="The Turning Point",
            scene_description=(
                f"{character_name} finds the courage and creativity needed "
                f"to overcome the challenge."
            ),
            image_prompt=(
                f"{character_name} overcoming a powerful challenge in {setting}, "
                f"heroic pose, emotional comic scene, {art_style} style, "
                f"cinematic atmosphere"
            ),
        ),
        PanelOutline(
            panel_number=5,
            title="A New Beginning",
            scene_description=(
                f"The adventure ends with {character_name} looking toward "
                f"a new future."
            ),
            image_prompt=(
                f"{character_name} standing proudly in {setting}, peaceful ending, "
                f"beautiful sky, inspirational comic book composition, "
                f"{art_style} style, cinematic lighting"
            ),
        ),
    ]


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[PanelOutline]:

    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    if demo_mode:
        return _demo_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style,
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file "
            "or set DEMO_MODE=true."
        )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    model_name = os.getenv(
        "GEMINI_FLASH_MODEL",
        "gemini-2.5-flash",
    )

    prompt = f"""
You are the comic outline planner for ComicCraft.

Create exactly 5 comic panels.

User story:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Create a coherent beginning, development, conflict,
turning point and ending.

Return ONLY valid JSON.

The JSON must be an array containing exactly 5 objects.

Each object must have:

panel_number
title
scene_description
image_prompt

Do not add markdown.
Do not add commentary.
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty outline.")

    raw = json.loads(response.text)

    if not isinstance(raw, list):
        raise RuntimeError("Gemini outline response is not a list.")

    panels = [
        PanelOutline.model_validate(panel)
        for panel in raw
    ]

    if len(panels) != 5:
        raise RuntimeError(
            f"Gemini returned {len(panels)} panels instead of 5."
        )

    return panels