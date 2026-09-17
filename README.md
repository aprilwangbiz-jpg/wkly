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

## Design

Style is a hand-drawn/pencil-sketch scene (inspired by the layout of
`itomdev.com/gallery`), not a generic dashboard: a sagging clothesline strung
across a sketched skyline, with each report clipped on as a colored sticky
note. Deliberate choices, so future edits don't drift from the intent:

- **Audience is older, non-technical viewers** — card titles are large, bold
  (`.card .label span`), and each card is a big, obvious click target (the
  whole sticky note, not just an icon or a small link).
- **Card color per report** is set in the `REPORTS` array in `index.html`
  (one hex value each) — change it there, not in CSS, to keep data and style
  together.
- **Mobile**: below 700px, the scene does NOT shrink to fit — it stays at a
  fixed, readable size and the page scrolls horizontally instead (with a
  "swipe to see all reports" hint). Shrinking to fit was tried first and made
  the text too small to read on a phone.
- **Fonts**: Kalam (hand-lettered, for the "WEEKLY REPORTS" banner and
  captions) and Patrick Hand (body/labels), both loaded from Google Fonts.
- The brick-door version of this page was an earlier direction, replaced
  once the actual `itomdev.com/gallery` reference (clothesline, not a door)
  was confirmed — mentioned here only so it isn't accidentally reintroduced.

## Hosting

Published via GitHub Pages from a dedicated repo (`weekly-reports`, separate
from the `yafainventory.com` dashboard). The repo is public — free GitHub
Pages requires it, the same tradeoff already made for `yafainventory.com`.

`background/`, `instruction.txt`, `style.txt`, and `gallary.png` are excluded
via `.gitignore` — they're local reference/design material, not part of the
published page.
