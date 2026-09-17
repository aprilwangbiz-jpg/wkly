# Weekly Reports Gallery

A single page (`index.html`) that shares the weekly PDF reports as a link for the
team: 8 report cards hang from a sketched clothesline, and clicking one opens
the actual PDF in a new tab.

## Structure

```
pdf/
├── index.html          the gallery page (self-contained: HTML + CSS + JS)
├── set_pdf_titles.py   fixes each PDF's browser-tab title
├── reports/            the 8 PDF files linked from the page
└── background/         unused reference images, not part of the site
```

## Updating the reports each week

The filenames in `reports/` stay the same from week to week — only the
content changes. To publish a fresh batch:

1. Drop the new week's PDFs into `reports/`, overwriting the same filenames.
2. Run the title fix (each PDF gets "Printed to PDF" from the same Excel
   workbook, so without this step every tab title shows the workbook's
   filename instead of the report name):
   ```
   python set_pdf_titles.py
   ```
3. Commit and push:
   ```
   git add reports/
   git commit -m "reports update <date>"
   git push
   ```

If a report is ever renamed, added, or removed, update both:
- the `REPORTS` array near the top of the `<script>` block in `index.html`
- the `TITLES` dict in `set_pdf_titles.py`

## Hosting

Published via GitHub Pages from a dedicated repo (`weekly-reports`, separate
from the `yafainventory.com` dashboard). The repo is public — free GitHub
Pages requires it, the same tradeoff already made for `yafainventory.com`.

`background/`, `instruction.txt`, `style.txt`, and `gallary.png` are excluded
via `.gitignore` — they're local reference/design material, not part of the
published page.
