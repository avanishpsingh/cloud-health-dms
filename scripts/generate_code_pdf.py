"""Generate a single PDF containing all source code (rubric requirement).

Usage:
    python scripts/generate_code_pdf.py

Output:
    report/CC_Project_Code_Group23.pdf

The PDF preserves filenames as headers and ships every file as
fixed-width text. We use ReportLab (pure Python, MIT) so contributors
don't need LaTeX or wkhtmltopdf installed.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Preformatted, PageBreak, Spacer
    )
except ImportError:
    sys.exit(
        "reportlab is required:\n  python -m pip install reportlab"
    )


REPO = Path(__file__).resolve().parent.parent
INCLUDE_DIRS = [
    "app",
    "tests",
    "scripts",
    "infra/terraform",
]
INCLUDE_FILES = [
    "Dockerfile",
    "requirements.txt",
    "README.md",
    "report/Phase2_Report.md",
    "report/Phase2_PPT_Outline.md",
    "report/Demo_Video_Script.md",
]
EXTS = {".py", ".tf", ".sh", ".md", ".txt", ".dockerfile", ""}


def collect_files() -> list[Path]:
    files: list[Path] = []
    for d in INCLUDE_DIRS:
        for p in sorted((REPO / d).rglob("*")):
            if p.is_file() and (p.suffix in EXTS or p.name == "Dockerfile"):
                files.append(p)
    for f in INCLUDE_FILES:
        p = REPO / f
        if p.exists():
            files.append(p)
    return files


def build_pdf(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
        title="Cloud-Native Healthcare DMS — Source Code (Group 23)",
    )
    styles = getSampleStyleSheet()
    code_style = ParagraphStyle(
        "Code", parent=styles["Code"],
        fontName="Courier", fontSize=7, leading=8,
    )
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]

    story = []
    story.append(Paragraph("Cloud-Native Healthcare Data Management System", h1))
    story.append(Paragraph("Phase 2 — Complete Source Code", h2))
    story.append(Paragraph(
        "BITS Pilani · Cloud Computing (CSIZG527) · Group 23<br/>"
        "Karan Rawat · Vikas Kumar · Kriti Tripathi · Avanish Pratap Singh",
        body,
    ))
    story.append(PageBreak())

    for f in collect_files():
        rel = f.relative_to(REPO).as_posix()
        story.append(Paragraph(f"<b>{rel}</b>", h2))
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = f.read_bytes().decode("utf-8", errors="replace")
        # Keep page-break friendly: split on blank lines so reportlab can flow.
        for chunk in text.split("\n\n"):
            if not chunk.strip():
                continue
            # Escape < > & for reportlab Preformatted is not needed; it's literal.
            story.append(Preformatted(chunk, code_style))
            story.append(Spacer(1, 2 * mm))
        story.append(PageBreak())

    doc.build(story)
    print(f"✓ Wrote {out_path}  ({out_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build_pdf(REPO / "report" / "CC_Project_Code_Group23.pdf")
