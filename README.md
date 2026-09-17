# Weekly Reports Gallery

A single page (`index.html`) that shares the weekly PDF reports as a link for the
team: report cards hang from a sketched clothesline, and clicking one opens
the actual PDF in a new tab.

## Structure

```
pdf/
├── index.html       the gallery page (self-contained: HTML + CSS + JS)
├── update_site.py    regenerates index.html + fixes PDF titles from reports/
├── publish.ps1        one-command weekly update (runs update_site.py, commits, pushes)
├── reports/           the PDF files linked from the page
├── ceo only/           restricted reports, excluded from the repo, not on the page
└── background/         unused reference images, not part of the site
```

## Updating the reports each week

Nothing to hand-edit — `index.html` is generated from whatever is actually
in `reports/`. To publish a fresh batch, add/remove/overwrite PDFs in
`reports/` (put anything that shouldn't be public in `ceo only/` instead),
then run:

```
.\publish.ps1
```

That's the whole workflow: it regenerates `index.html` and each PDF's
browser-tab title (`update_site.py`), then commits and pushes — skipping
the commit/push if nothing actually changed.

Prefer to do it in two steps, or don't want to push yet? Run
`python update_site.py` on its own first to regenerate and preview locally,
then `git add reports/ index.html`, commit, and push whenever you're ready.

A report's title, on-page color, and position are all derived from its
filename — nothing to edit by hand unless you want to change how a title is
worded (see `make_title()` in `update_site.py`).

## Design

Style is a hand-drawn/pencil-sketch scene (inspired by the layout of
`itomdev.com/gallery`), not a generic dashboard: a sagging clothesline strung
across a sketched skyline, with each report clipped on as a colored sticky
note. Deliberate choices, so future edits don't drift from the intent:

- **Audience is older, non-technical viewers** — card titles are large, bold
  (`.card .label span`), and each card is a big, obvious click target (the
  whole sticky note, not just an icon or a small link).
- **Card color per report** is auto-assigned from the `PALETTE` list in
  `update_site.py`, cycling in filename order — edit that list, not CSS or
  `index.html` directly, since those get regenerated.
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

`background/`, `instruction.txt`, `style.txt`, `gallary.png`, and
`ceo only/` are excluded via `.gitignore` — the first four are local
reference/design material, and `ceo only/` holds reports that must not be
public.
