from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.config import settings
from app.schemas import ComicLayoutPanel
from app.utils.files import safe_filename


def _pdf_text(value: str) -> str:
    # Built-in FPDF fonts are not full Unicode fonts. Replace common problematic
    # characters so the default PDF remains portable without bundling a font.
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "’": "'",
        "…": "...",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value.encode("latin-1", "replace").decode("latin-1")


def save_pdf(title: str, layout: list[ComicLayoutPanel]) -> Path:
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(
        f"{title}-{datetime.now().strftime('%Y%m%d-%H%M%S')}", "pdf"
    )
    output = settings.exports_dir / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_x(15)
        pdf.multi_cell(180, 10, _pdf_text(f"Panel {panel.panel_number}: {panel.title}"))

        image_file = settings.static_dir.parent / panel.image_path.lstrip("/").replace(
            "static/", "", 1
        )
        if image_file.exists():
            pdf.image(str(image_file), x=15, y=35, w=180)

        pdf.ln(118)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_x(15)
        pdf.multi_cell(180, 6, _pdf_text(panel.scene_description))

        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_x(15)
        pdf.multi_cell(180, 6, _pdf_text("Caption:"))
        pdf.set_font("Helvetica", size=10)
        pdf.set_x(15)
        pdf.multi_cell(180, 6, _pdf_text(panel.caption))

        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_x(15)
        pdf.multi_cell(180, 6, _pdf_text("Narration:"))
        pdf.set_font("Helvetica", size=10)
        pdf.set_x(15)
        pdf.multi_cell(180, 6, _pdf_text(panel.narration))

        if panel.dialogue:
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_x(15)
            pdf.multi_cell(180, 6, _pdf_text("Dialogue:"))
            pdf.set_font("Helvetica", size=10)
            for line in panel.dialogue:
                pdf.set_x(15)
                pdf.multi_cell(180, 6, _pdf_text(f"- {line}"))

    pdf.output(str(output))
    return output
