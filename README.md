# yfeng0206.github.io -- Developer Reference

> This file is NOT published to the website. Jekyll on GitHub Pages auto-excludes README.md.

## Site Structure Quick Reference

```
_pages/
  about.md             <-- Bio, work experience, recent highlights
  portfolio-archive.md <-- Grid of all portfolio items
  publications.md      <-- Papers (published + in progress)
  resume.md            <-- Web resume; links to the PDF
  blog.md              <-- Blog post archive
  404.md

_portfolio/
  copilot-world-lab.md    <-- V-JEPA 2-AC manipulation world model
  ijepa-3d-oct.md         <-- I-JEPA OCT foundation model project
  slivit-3d-oct-glaucoma.md
  object-permanence-detection.md
  mot17-object-tracking.md
  ivalet-parking.md
  gesture-car.md
  self-driving-car.md

_posts/
  2026-08-14-anatomy-guided-masking-oct.md
  2026-07-10-reproducing-vjepa2-ac.md
  2026-04-08-consensus-ai-trader.md
  2026-03-18-ijepa-oct-training-log.md
  2026-03-12-slivit-glaucoma-training-log.md

_data/navigation.yml   <-- Top nav bar items
_config.yml            <-- Site config, theme settings, author sidebar links
assets/images/         <-- All images (teasers, charts, SVGs, demo GIFs)
assets/resume/         <-- Resume print source (HTML) + generated PDF
```

## Theme & Build

- **Theme:** Minimal Mistakes v4.28.0 (remote theme, dark skin)
- **Build:** GitHub Pages (automatic on push to main)
- **Fonts:** Inter + Fira Code (Google Fonts)
- **Local preview:** `bundle install` then `bundle exec jekyll serve`

## Conventions

- **No em dashes** in site copy. Use hyphens or commas. Use `x` rather than the multiplication sign.
- **Nav caveat:** Minimal Mistakes masthead does NOT support `children` dropdowns. All nav
  items must be flat with a `url`.
- **Portfolio ordering** is by the `date` in each item's front matter, newest first.
  There is no `collections.*.order` key in Minimal Mistakes; do not add one.
  Bump an item's `date` when its content is materially updated.
- **Blog permalinks** are `/:categories/:title/`, so a post with `categories: [research]`
  lives at `/research/<slug>/`. Cross-links must include the category segment.
- **No personal contact details beyond email** on the public site (no phone, no street address).

## Resume

There is now a **single source of truth** for resume content:
`assets/resume/gary-feng-resume.html`, the print source. It generates both the PDF
and the page image.

- `_pages/resume.md` shows the rendered page image linked to the PDF. It contains no
  resume text of its own, so it cannot drift.
- `_pages/about.md` carries a deliberately condensed summary and links to `/resume/`.
  Do not paste full resume bullets back into it.
- The upstream master is Gary's `Resume 2026.docx`. The site version adds the published
  Science Robotics citation and CopilotWorldLab, and **omits the phone number** because
  the PDF is served publicly.

**Do not embed the PDF with `<object>`/`<iframe>`.** It was tried and reverted: Chrome's
"Download PDFs instead of automatically opening them" setting makes the embed render
nothing, and because the resource technically loaded, it never falls through to the
element's fallback content. The visitor just sees an empty box. A rendered image always
displays, including on mobile.

Regenerate both artifacts after editing the HTML (it is tuned to fit exactly one page):

```powershell
$base = "C:\Users\Gary\yfeng0206.github.io\assets\resume\gary-feng-resume"
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu `
  --print-to-pdf="$base.pdf" --no-pdf-header-footer `
  "file:///C:/Users/Gary/yfeng0206.github.io/assets/resume/gary-feng-resume.html"

python -c "import pymupdf; from PIL import Image; d=pymupdf.open(r'$base.pdf'); d[0].get_pixmap(dpi=200).save(r'$base.raw.png'); Image.open(r'$base.raw.png').convert('P', palette=Image.ADAPTIVE, colors=64).save(r'$base.png', optimize=True)"
```

**Use an absolute `--print-to-pdf` path.** With a relative path Chrome headless
silently writes nothing and still exits 0, so the committed PDF goes stale while the
HTML moves on. Always verify afterwards:

```powershell
python -c "import pymupdf; d=pymupdf.open(r'assets\resume\gary-feng-resume.pdf'); print(len(d)); print(d[0].get_text()[:200])"
```

Note that headless Chrome cannot rasterise PDFs, so screenshotting `/resume/` or a PDF
URL always yields a blank frame. Verify the PDF with pymupdf text extraction instead.

`.gitignore` ignores `*.pdf` globally with an explicit negation for
`assets/resume/gary-feng-resume.pdf`. Keep that negation if the filename ever changes,
otherwise the resume will silently stop shipping.
