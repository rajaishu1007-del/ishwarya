import os
import re
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent.parent

PANELS_DIR = BASE_DIR / "static" / "panels"

PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def _safe_filename(text: str) -> str:

    cleaned = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text,
    )

    cleaned = cleaned.strip("_")

    return cleaned[:80] or "panel"


def _create_mock_image(
    prompt: str,
    output_path: Path,
    panel_number: int | None = None,
) -> str:

    width = int(os.getenv("IMAGE_WIDTH", "768"))
    height = int(os.getenv("IMAGE_HEIGHT", "768"))

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(image)

    # Border
    draw.rectangle(
        (20, 20, width - 20, height - 20),
        outline="black",
        width=8,
    )

    title = (
        f"COMIC PANEL {panel_number}"
        if panel_number
        else "COMIC PANEL"
    )

    draw.text(
        (50, 60),
        title,
        fill="black",
    )

    # Simple comic speech bubble
    bubble_x1 = 80
    bubble_y1 = 180
    bubble_x2 = width - 80
    bubble_y2 = 350

    draw.rounded_rectangle(
        (
            bubble_x1,
            bubble_y1,
            bubble_x2,
            bubble_y2,
        ),
        radius=30,
        outline="black",
        width=5,
    )

    text = prompt[:250]

    draw.multiline_text(
        (110, 220),
        text,
        fill="black",
        spacing=8,
    )

    # Character placeholder
    center_x = width // 2
    center_y = height // 2 + 100

    draw.ellipse(
        (
            center_x - 90,
            center_y - 90,
            center_x + 90,
            center_y + 90,
        ),
        outline="black",
        width=6,
    )

    draw.line(
        (
            center_x,
            center_y + 90,
            center_x,
            center_y + 260,
        ),
        fill="black",
        width=6,
    )

    draw.line(
        (
            center_x,
            center_y + 140,
            center_x - 90,
            center_y + 210,
        ),
        fill="black",
        width=6,
    )

    draw.line(
        (
            center_x,
            center_y + 140,
            center_x + 90,
            center_y + 210,
        ),
        fill="black",
        width=6,
    )

    image.save(
        output_path,
        format="PNG",
    )

    return str(output_path)


def _generate_huggingface(
    prompt: str,
    output_path: Path,
) -> str:

    token = os.getenv("HF_TOKEN")

    if not token:
        raise RuntimeError(
            "HF_TOKEN is missing. Add it to .env."
        )

    from huggingface_hub import InferenceClient

    model = os.getenv(
        "HF_IMAGE_MODEL",
        "stabilityai/stable-diffusion-xl-base-1.0",
    )

    client = InferenceClient(
        provider="hf-inference",
        api_key=token,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=model,
    )

    image.save(output_path)

    return str(output_path)


def _generate_local(
    prompt: str,
    output_path: Path,
) -> str:

    import torch
    from diffusers import StableDiffusionPipeline

    model_name = os.getenv(
        "LOCAL_IMAGE_MODEL",
        "runwayml/stable-diffusion-v1-5",
    )

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    pipe = StableDiffusionPipeline.from_pretrained(
        model_name,
        torch_dtype=(
            torch.float16
            if device == "cuda"
            else torch.float32
        ),
    )

    pipe = pipe.to(device)

    result = pipe(
        prompt=prompt,
        num_inference_steps=20,
        guidance_scale=7.5,
    )

    image = result.images[0]

    image.save(output_path)

    return str(output_path)


def generate_image(
    image_prompt: str,
    panel_number: int | None = None,
) -> str:

    provider = os.getenv(
        "IMAGE_PROVIDER",
        "mock",
    ).lower()

    unique_id = uuid.uuid4().hex[:10]

    panel_text = (
        f"panel_{panel_number}"
        if panel_number
        else "panel"
    )

    filename = (
        f"{panel_text}_"
        f"{_safe_filename(image_prompt)}_"
        f"{unique_id}.png"
    )

    output_path = PANELS_DIR / filename

    if provider == "mock":
        return _create_mock_image(
            image_prompt,
            output_path,
            panel_number,
        )

    if provider == "huggingface":
        return _generate_huggingface(
            image_prompt,
            output_path,
        )

    if provider == "local":
        return _generate_local(
            image_prompt,
            output_path,
        )

    raise ValueError(
        "IMAGE_PROVIDER must be one of: "
        "mock, huggingface, local."
    )