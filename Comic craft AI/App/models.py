from typing import List

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Main idea of the comic story.",
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the main character.",
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Location or world where the story happens.",
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tone of the story.",
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Visual style of the comic.",
    )


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class StoryPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    dialogue: str


class ComicResponse(BaseModel):
    success: bool
    message: str
    panels: List[StoryPanel]
    pdf_url: str | None = None