"""Regenerate index.html and fix PDF titles from whatever is in reports/.

reports/ holds one subfolder per period, named M.D.YY (e.g. reports/9.25.26/).
Run this after adding a period folder or changing any PDF in one -- it is
the ONLY step needed. It reads the folders, so there is nothing else to
edit by hand:

  1. Builds a clean display title from each filename (e.g.
     "GP  sales by customer.pdf" -> "GP Sales by Customer").
  2. Writes "<title> - <week>" into the PDF's own /Title metadata, so the
     browser tab shows the report name and week instead of the source Excel
     workbook's filename (every report is "Printed to PDF" from the same
     workbook), and stamps "Week of <week>" in the top-right of every page.
     Filenames are never changed.
  3. Rewrites the PERIODS array in index.html (between the
     "REPORTS:START" / "REPORTS:END" markers) to match exactly what's on
     disk: periods newest first, reports alphabetical, each with a color
     assigned from a fixed palette.

Usage:  python update_site.py
"""
import hashlib
import io
import re
from datetime import datetime
from pathlib import Path

import pypdf
from reportlab.pdfgen import canvas

ROOT = Path(__file__).parent
REPORTS_DIR = ROOT / "reports"
INDEX_HTML = ROOT / "index.html"

# Cycles if there are more reports than colors.
PALETTE = [
    "#FFE9A8", "#AEE3FF", "#FFC2D9", "#C6F6D5",
    "#E0D1FF", "#FFD3AE", "#C7FFF0", "#D8DFFF",
]

PERIOD_FORMAT = "%m.%d.%y"

# "Week of 9.25.26" drawn in the top-right corner of every PDF page.
STAMP_FONT_SIZE = 10
STAMP_MARGIN = 14  # points from the top and right edges
STAMP_KEY = "/WeekStamp"  # PDF metadata marker so a page is never stamped twice

ACRONYMS = {"gp": "GP", "ytd": "YTD"}
LOWERCASE_WORDS = {"by", "vs"}


def make_title(filename: str) -> str:
    name = filename.rsplit(".", 1)[0]
    name = re.sub(r"\s+", " ", name).strip()
    words = []
    for word in name.split(" "):
        lower = word.lower()
        if lower == "and":
            words.append("&")
        elif lower in ACRONYMS:
            words.append(ACRONYMS[lower])
        elif lower in LOWERCASE_WORDS:
            words.append(lower)
        else:
            words.append(word.capitalize())
    return " ".join(words)


def stamp_overlay(width: float, height: float, text: str) -> pypdf.PageObject:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    c.setFont("Helvetica-Bold", STAMP_FONT_SIZE)
    c.setFillGray(0.35)
    c.drawRightString(width - STAMP_MARGIN, height - STAMP_MARGIN, text)
    c.save()
    return pypdf.PdfReader(buf).pages[0]


def prepare_pdf(path: Path, title: str, period: str) -> None:
    """Set the tab title to "<title> - <period>" and stamp the period on every page."""
    reader = pypdf.PdfReader(str(path))
    metadata = dict(reader.metadata or {})
    tab_title = f"{title} - {period}"
    stamped = metadata.get(STAMP_KEY)
    prefs = reader.viewer_preferences
    shows_title = bool(prefs and prefs.display_doctitle)
    if stamped == period and metadata.get("/Title") == tab_title and shows_title:
        return  # already done; rewriting would change the file for git
    if stamped and stamped != period:
        raise SystemExit(
            f"{path} is already stamped with week {stamped}. "
            "Put the original PDF in this folder, not a copy from another week."
        )

    writer = pypdf.PdfWriter()
    writer.append_pages_from_reader(reader)
    if not stamped:
        for page in writer.pages:
            box = page.mediabox
            overlay = stamp_overlay(float(box.width), float(box.height), f"Week of {period}")
            page.merge_translated_page(overlay, float(box.left), float(box.bottom))
    metadata["/Title"] = tab_title
    metadata[STAMP_KEY] = period
    writer.add_metadata(metadata)
    # Without this, Edge/Chrome show the filename in the tab, not /Title.
    writer.create_viewer_preferences().display_doctitle = True

    tmp_path = path.with_suffix(".tmp.pdf")
    with open(tmp_path, "wb") as f:
        writer.write(f)
    tmp_path.replace(path)


def js_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_reports_block(periods: list[tuple[str, list[tuple[str, str, str, str]]]]) -> str:
    lines = ["  const PERIODS = ["]
    for label, entries in periods:
        lines.append(f"    {{ label: {js_str(label)}, reports: [")
        for title, filename, color, version in entries:
            lines.append(
                f"      {{ title: {js_str(title)}, file: {js_str(filename)}, color: {js_str(color)}, v: {js_str(version)} }},"
            )
        lines.append("    ] },")
    lines.append("  ];")
    return "\n".join(lines)


def parse_period(folder: Path) -> datetime:
    try:
        return datetime.strptime(folder.name, PERIOD_FORMAT)
    except ValueError:
        raise SystemExit(
            f"Folder name '{folder.name}' in reports/ is not a date like 9.25.26"
        ) from None


def collect_period(folder: Path) -> list[tuple[str, str, str, str]]:
    pdf_files = sorted(folder.glob("*.pdf"), key=lambda p: p.name.lower())
    entries = []
    for i, path in enumerate(pdf_files):
        title = make_title(path.name)
        color = PALETTE[i % len(PALETTE)]
        prepare_pdf(path, title, folder.name)
        # Fingerprint of the final file: new numbers -> new link, so browsers
        # never show a stale cached copy of a re-published PDF.
        version = hashlib.md5(path.read_bytes()).hexdigest()[:8]
        entries.append((title, path.name, color, version))
        print(f"  {path.name} -> \"{title}\" ({color})")
    return entries


def main() -> None:
    for stray in REPORTS_DIR.glob("*.pdf"):
        print(f"WARNING: {stray.name} is not in a dated folder -- not on the page")

    folders = sorted(
        (d for d in REPORTS_DIR.iterdir() if d.is_dir()), key=parse_period, reverse=True
    )
    if not folders:
        raise SystemExit(f"No period folders (like 9.25.26) found in {REPORTS_DIR}")

    periods = []
    for folder in folders:
        print(folder.name)
        entries = collect_period(folder)
        if entries:
            periods.append((folder.name, entries))
        else:
            print("  WARNING: no PDFs yet -- left off the page")
    if not periods:
        raise SystemExit(f"No PDFs found in any period folder of {REPORTS_DIR}")

    html = INDEX_HTML.read_text(encoding="utf-8")
    new_block = build_reports_block(periods)
    updated_html, count = re.subn(
        r"(// REPORTS:START\n).*?(\n\s*// REPORTS:END)",
        lambda m: m.group(1) + new_block + m.group(2),
        html,
        flags=re.DOTALL,
    )
    if count != 1:
        raise SystemExit(
            "Could not find REPORTS:START / REPORTS:END markers in index.html"
        )
    INDEX_HTML.write_text(updated_html, encoding="utf-8")
    print(f"\nindex.html updated with {len(periods)} period(s).")


if __name__ == "__main__":
    main()
