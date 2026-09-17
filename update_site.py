"""Regenerate index.html and fix PDF titles from whatever is in reports/.

Run this after adding, removing, or renaming any PDF in reports/ -- it is
the ONLY step needed. It reads the folder, so there is nothing else to
edit by hand:

  1. Builds a clean display title from each filename (e.g.
     "GP  sales by customer.pdf" -> "GP Sales by Customer").
  2. Writes that title into the PDF's own /Title metadata, so the browser
     tab shows the report name instead of the source Excel workbook's
     filename (every report is "Printed to PDF" from the same workbook).
  3. Rewrites the REPORTS array in index.html (between the
     "REPORTS:START" / "REPORTS:END" markers) to match exactly what's on
     disk, in alphabetical order, with a color assigned from a fixed
     palette.

Usage:  python update_site.py
"""
import re
from pathlib import Path

import pypdf

ROOT = Path(__file__).parent
REPORTS_DIR = ROOT / "reports"
INDEX_HTML = ROOT / "index.html"

# Cycles if there are more reports than colors.
PALETTE = [
    "#FFE9A8", "#AEE3FF", "#FFC2D9", "#C6F6D5",
    "#E0D1FF", "#FFD3AE", "#C7FFF0", "#D8DFFF",
]

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


def set_pdf_title(path: Path, title: str) -> None:
    reader = pypdf.PdfReader(str(path))
    writer = pypdf.PdfWriter()
    writer.append_pages_from_reader(reader)
    metadata = dict(reader.metadata or {})
    metadata["/Title"] = title
    writer.add_metadata(metadata)

    tmp_path = path.with_suffix(".tmp.pdf")
    with open(tmp_path, "wb") as f:
        writer.write(f)
    tmp_path.replace(path)


def build_reports_block(entries: list[tuple[str, str, str]]) -> str:
    lines = ["  const REPORTS = ["]
    for title, filename, color in entries:
        escaped_title = title.replace('"', '\\"')
        escaped_file = filename.replace('"', '\\"')
        lines.append(
            f'    {{ title: "{escaped_title}", file: "{escaped_file}", color: "{color}" }},'
        )
    lines.append("  ];")
    return "\n".join(lines)


def main() -> None:
    pdf_files = sorted(REPORTS_DIR.glob("*.pdf"), key=lambda p: p.name.lower())
    if not pdf_files:
        raise SystemExit(f"No PDFs found in {REPORTS_DIR}")

    entries = []
    for i, path in enumerate(pdf_files):
        title = make_title(path.name)
        color = PALETTE[i % len(PALETTE)]
        set_pdf_title(path, title)
        entries.append((title, path.name, color))
        print(f"{path.name} -> \"{title}\" ({color})")

    html = INDEX_HTML.read_text(encoding="utf-8")
    new_block = build_reports_block(entries)
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
    print(f"\nindex.html updated with {len(entries)} report(s).")


if __name__ == "__main__":
    main()
