"""Render report/Phase2_Report.md to a polished PDF using ReportLab.

Heuristic markdown → PDF rendering tuned for our report (no images, no tables
beyond simple pipe tables, ASCII diagrams kept as preformatted code).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Preformatted, PageBreak, Spacer, Table, TableStyle
    )
except ImportError:
    sys.exit("reportlab missing — run: python -m pip install reportlab")

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "report" / "Phase2_Report.md"
OUT = REPO / "report" / "CC_Project_Report_Group23.pdf"


def parse_table(lines: list[str]) -> list[list[str]] | None:
    """Parse a GitHub-style pipe table; return rows or None if not a table."""
    rows = []
    for line in lines:
        if "|" not in line:
            return None
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return None
    # Drop the divider row (all dashes / colons)
    if all(re.fullmatch(r"[\-:\s]+", c) for c in rows[1]):
        rows.pop(1)
    return rows


def render(md_text: str):
    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10, leading=13)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, leading=22, spaceBefore=8, spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, leading=18, spaceBefore=6, spaceAfter=4)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, leading=14, spaceBefore=4, spaceAfter=2)
    code = ParagraphStyle("Code", parent=styles["Code"], fontName="Courier", fontSize=8, leading=9)

    story = []
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        # Code fences
        if line.startswith("```"):
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].startswith("```"):
                buf.append(lines[j])
                j += 1
            story.append(Preformatted("\n".join(buf), code))
            story.append(Spacer(1, 3 * mm))
            i = j + 1
            continue

        # Heading
        if line.startswith("### "):
            story.append(Paragraph(line[4:].strip(), h3))
            i += 1; continue
        if line.startswith("## "):
            story.append(Paragraph(line[3:].strip(), h2))
            i += 1; continue
        if line.startswith("# "):
            story.append(Paragraph(line[2:].strip(), h1))
            i += 1; continue

        # Tables — accumulate lines starting with |
        if line.lstrip().startswith("|"):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            data = parse_table(block)
            if data:
                # Wrap each cell in Paragraph for wrapping
                wrapped = [[Paragraph(c, body) for c in row] for row in data]
                t = Table(wrapped, repeatRows=1, hAlign="LEFT")
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]))
                story.append(t)
                story.append(Spacer(1, 3 * mm))
                continue
            # not a table — fall through

        # Horizontal rule
        if re.match(r"^---+\s*$", line):
            story.append(Spacer(1, 3 * mm))
            i += 1; continue

        # Bullet list
        if line.lstrip().startswith(("- ", "* ")):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith(("- ", "* ")):
                item = lines[i].lstrip()[2:]
                block.append(f"• {inline(item)}")
                i += 1
            for b in block:
                story.append(Paragraph(b, body))
            story.append(Spacer(1, 2 * mm))
            continue

        if not line.strip():
            i += 1; continue

        # Paragraph (collapse following non-blank lines)
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "```", "- ", "* ")):
            para.append(lines[i])
            i += 1
        story.append(Paragraph(inline(" ".join(para)), body))
        story.append(Spacer(1, 2 * mm))

    return story


def inline(text: str) -> str:
    """Bare-minimum inline markdown → reportlab markup."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r"<link href='\2'>\1</link>", text)
    return text


def main():
    md = SRC.read_text(encoding="utf-8")
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title="Cloud-Native Healthcare DMS — Phase 2 Report (Group 23)",
    )
    doc.build(render(md))
    print(f"✓ Wrote {OUT}  ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
