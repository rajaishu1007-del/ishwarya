from datetime import datetime
from pathlib import Path

from fpdf import FPDF


BASE_DIR = Path(__file__).resolve().parent.parent

EXPORT_DIR = BASE_DIR / "static" / "exports"

EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def _clean_text(value: str) -> str:

    if not value:
        return ""

    replacements = {
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "-",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return value.encode(
        "latin-1",
        errors="replace",
    ).decode("latin-1")


def save_pdf(
    layout: list[dict],
    title: str = "ComicCraft Comic",
) -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"comiccraft_{timestamp}.pdf"
    )

    output_path = EXPORT_DIR / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        # Title
        pdf.set_font(
            "Helvetica",
            "B",
            20,
        )

        pdf.cell(
            0,
            12,
            _clean_text(
                f"Panel {panel['panel_number']}: "
                f"{panel['title']}"
            ),
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.ln(4)

        # Image
        image_path = Path(
            panel["image_path"]
        )

        if image_path.exists():

            max_width = 170
            max_height = 115

            pdf.image(
                str(image_path),
                x=20,
                y=35,
                w=max_width,
                h=max_height,
            )

            pdf.ln(120)

        # Scene description
        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                panel["scene_description"]
            ),
        )

        pdf.ln(3)

        # Caption
        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                f"Caption: {panel['caption']}"
            ),
        )

        pdf.ln(2)

        # Narration
        pdf.set_font(
            "Helvetica",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                f"Narration: {panel['narration']}"
            ),
        )

        pdf.ln(2)

        # Dialogue
        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                f"Dialogue: {panel['dialogue']}"
            ),
        )

    pdf.output(
        str(output_path)
    )

    return str(output_path)