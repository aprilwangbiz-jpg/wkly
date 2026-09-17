"""Set each report PDF's embedded /Title metadata to its display name.

Reports get "Printed to PDF" from the same Excel workbook each week, so
every file inherits that workbook's filename as its PDF title -- which is
what browser tabs show instead of the actual report name. Run this after
dropping in a fresh batch of PDFs (before pushing) to fix the tab titles.

Keep TITLES in sync with the REPORTS list in index.html if a report is
ever renamed, added, or removed.
"""
import pypdf
from pathlib import Path

REPORTS_DIR = Path(__file__).parent / "reports"

TITLES = {
    "GP  sales by customer.pdf": "GP Sales by Customer",
    "INVENTORY BY BRAND AND COLLECTION.pdf": "Inventory by Brand & Collection",
    "SALES BY COLLECTION.pdf": "Sales by Collection",
    "gp  Sales by brand.pdf": "GP Sales by Brand",
    "monthly sales ytd vs 2025.pdf": "Monthly Sales YTD vs 2025",
    "open sales by brand and customer.pdf": "Open Sales by Brand & Customer",
    "ytd sales by brand.pdf": "YTD Sales by Brand",
    "ytd sales by customer.pdf": "YTD Sales by Customer",
}

for filename, title in TITLES.items():
    path = REPORTS_DIR / filename
    if not path.exists():
        print(f"skip (not found): {filename}")
        continue

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
    print(f"set title: {filename} -> {title}")
