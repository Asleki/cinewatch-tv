#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "nexvox" / "engineering"


def default_output() -> Path:
    downloads = Path.home() / "storage" / "downloads" / "cinewatch-nexvox"
    if downloads.parent.exists():
        downloads.mkdir(parents=True, exist_ok=True)
        return downloads / "CineWatch_NexVox_Engineering_Knowledge_LATEST.pdf"
    local = ROOT.parent / "cinewatch-nexvox-local"
    local.mkdir(parents=True, exist_ok=True)
    return local / "CineWatch_NexVox_Engineering_Knowledge_LATEST.pdf"


def clean_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return text.replace("→", "->").replace("—", "-").replace("–", "-")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local-only human-readable PDF projection of the NexVox engineering corpus.")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    output = args.output or default_output()
    try:
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
    except ImportError:
        print("FAIL  reportlab is required only for the local PDF projection; the tracked NexVox corpus does not depend on it", file=sys.stderr)
        return 2

    sync = (CORPUS / "manifests" / "sync-state.yaml").read_text(encoding="utf-8")
    m = re.search(r'^source_commit:\s*"([0-9a-f]{40})"', sync, re.M)
    source = m.group(1) if m else "unknown"

    docs = [
        CORPUS / "DATASET_CARD.md",
        CORPUS / "narratives" / "engineering-history.md",
        CORPUS / "narratives" / "architecture-decisions.md",
        CORPUS / "narratives" / "failures-corrections-lessons.md",
        CORPUS / "narratives" / "engineering-methods.md",
        CORPUS / "narratives" / "glossary.md",
    ]
    for path in docs:
        if not path.is_file():
            print(f"FAIL  missing corpus narrative: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("CWTitle", parent=styles["Title"], alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=20, leading=24, spaceAfter=12)
    h1 = ParagraphStyle("CWH1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=19, spaceBefore=10, spaceAfter=6)
    h2 = ParagraphStyle("CWH2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("CWBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=5)
    code = ParagraphStyle("CWCode", parent=body, fontName="Courier", fontSize=8, leading=10, leftIndent=8*mm, rightIndent=4*mm)
    meta = ParagraphStyle("CWMeta", parent=body, fontSize=8, leading=10)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.drawString(18*mm, 10*mm, f"CineWatch NexVox Engineering Knowledge - source {source[:12]}")
        canvas.drawRightString(A4[0]-18*mm, 10*mm, f"Page {doc.page}")
        canvas.restoreState()

    story = [
        Paragraph("CineWatch NexVox Engineering Knowledge", title),
        Paragraph(f"Local-only preservation projection<br/>Source commit: {source}<br/>This PDF is not repository or training authority.", meta),
        Spacer(1, 8*mm),
    ]
    in_code = False
    for di, path in enumerate(docs):
        if di:
            story.append(PageBreak())
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.rstrip()
            if line.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                if line:
                    story.append(Paragraph(clean_inline(line).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), code))
                continue
            if not line:
                story.append(Spacer(1, 2.5*mm))
                continue
            if line.startswith("# "):
                story.append(Paragraph(clean_inline(line[2:]), h1))
            elif line.startswith("## "):
                story.append(Paragraph(clean_inline(line[3:]), h2))
            elif line.startswith("### "):
                story.append(Paragraph(clean_inline(line[4:]), h2))
            elif line.startswith("- "):
                story.append(Paragraph("• " + clean_inline(line[2:]), body))
            elif line.startswith("|"):
                story.append(Paragraph(clean_inline(line).replace("|", " &nbsp; | &nbsp; "), meta))
            else:
                safe = clean_inline(line).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(safe, body))

    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=17*mm, title="CineWatch NexVox Engineering Knowledge", author="CineWatch TV")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PASS  wrote local-only PDF: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
