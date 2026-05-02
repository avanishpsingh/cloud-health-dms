"""Generate the Phase 2 PowerPoint deck from the markdown outline.

Parses report/Phase2_PPT_Outline.md (slides separated by `---`) and emits
report/CC_Project_PPT_Group23.pptx with one slide per section.

Slide layout used: a clean title + bullets template (no images), so the deck
is ready to present as-is or to drop into a corporate template later.
"""
from __future__ import annotations

import re
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "report" / "Phase2_PPT_Outline.md"
OUT = REPO / "report" / "CC_Project_PPT_Group23.pptx"

THEME_BLUE = RGBColor(0x0B, 0x3D, 0x91)
TEXT_DARK = RGBColor(0x22, 0x22, 0x22)
MUTED = RGBColor(0x66, 0x66, 0x66)


def parse_slides(text: str) -> list[dict]:
    """Split outline by horizontal rule into a list of slide dicts."""
    blocks = re.split(r"\n---+\s*\n", text)
    slides: list[dict] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # First H2 line ("## Slide N — Title") is the title
        m = re.search(r"^##\s+(.*?)\s*$", block, re.MULTILINE)
        if not m:
            continue
        full_title = m.group(1).strip()
        # Strip "Slide N —" prefix if present
        title = re.sub(r"^Slide\s+\d+\s*[—–-]\s*", "", full_title).strip()
        body = block[m.end():].strip()
        slides.append({"title": title, "body": body, "raw_title": full_title})
    return slides


def add_title_slide(prs: Presentation, title: str, subtitle: str) -> None:
    layout = prs.slide_layouts[0]   # title layout
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    slide.placeholders[1].text = subtitle
    for run in slide.shapes.title.text_frame.paragraphs[0].runs:
        run.font.color.rgb = THEME_BLUE
        run.font.bold = True


def add_content_slide(prs: Presentation, title: str, body_md: str) -> None:
    layout = prs.slide_layouts[1]   # title + content
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    for run in slide.shapes.title.text_frame.paragraphs[0].runs:
        run.font.color.rgb = THEME_BLUE
        run.font.bold = True

    body_placeholder = slide.placeholders[1]
    tf = body_placeholder.text_frame
    tf.clear()
    tf.word_wrap = True

    first = True
    in_code = False
    code_lines: list[str] = []

    def flush_code():
        nonlocal code_lines, first
        if not code_lines:
            return
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = "\n".join(code_lines)
        for r in p.runs:
            r.font.name = "Consolas"
            r.font.size = Pt(10)
            r.font.color.rgb = MUTED
        code_lines = []

    for line in body_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if not in_code:
                flush_code()
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not stripped:
            continue
        # Skip italic speaker notes lines (start with `*` AND end with `*`)
        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            # Put into slide notes instead
            notes = slide.notes_slide.notes_text_frame
            if notes.text:
                notes.text += "\n" + stripped.strip("*").strip()
            else:
                notes.text = stripped.strip("*").strip()
            continue
        # Pipe table → render as plain bullets (one row per line)
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(re.fullmatch(r"[\-:\s]+", c) for c in cells):
                continue   # divider row
            stripped = " — ".join(c for c in cells if c)

        # Headers inside slide → bolded sub-line
        is_bullet = stripped.startswith(("- ", "* "))
        text = stripped[2:] if is_bullet else stripped
        # Strip markdown emphasis to plain text
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"`(.+?)`", r"\1", text)

        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = text
        p.level = 0 if not is_bullet else 1
        for r in p.runs:
            r.font.size = Pt(16) if not is_bullet else Pt(14)
            r.font.color.rgb = TEXT_DARK

    flush_code()


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    slides = parse_slides(text)
    if not slides:
        raise SystemExit("No slides parsed from outline")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # First slide is the title slide — render it specially.
    title_block = slides[0]
    subtitle = "\n".join(
        line for line in title_block["body"].splitlines()
        if line.strip() and not line.strip().startswith("*")
    )
    add_title_slide(prs, title_block["title"], subtitle)

    for s in slides[1:]:
        add_content_slide(prs, s["title"], s["body"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"✓ Wrote {OUT}  ({OUT.stat().st_size / 1024:.0f} KB, {len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
