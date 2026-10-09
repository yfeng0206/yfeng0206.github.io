# yfeng0206.github.io -- Developer Reference

> This file is NOT published to the website. Jekyll on GitHub Pages auto-excludes README.md.

## Site Structure Quick Reference

```
index.md               <-- Home: short bio, links row, Experience summary (layout: home)
_pages/
  research.md          <-- /research/: Publications + Active research (layout: researchindex)
  projects.md          <-- /projects/: projects and writeups (layout: worklist)
  cv.md                <-- /cv/: resume image linked to the PDF
  404.md

_data/
  navigation.yml       <-- Top nav bar items
  publications.yml     <-- Papers shown under Research > Publications, newest first
  work.yml             <-- Experience rows on the home page

_research/             <-- Active research pages (/research/<name>/), sorted by `order`
  ijepa-3d-oct.md         <-- I-JEPA OCT project (NeurIPS 2026 GenAI4Health workshop paper)
  copilot-world-lab.md    <-- V-JEPA 2-AC manipulation world model

_projects/             <-- Project pages (/projects/<name>/)
_posts/                <-- Writeups, served at /writing/<slug>/

_config.yml            <-- Site config and author email
assets/images/         <-- All images (teasers, charts, demo GIFs)
assets/resume/         <-- Resume print source (HTML) + generated PDF and page image
```

## Publications

Each entry in `_data/publications.yml` needs `title`, `authors` (wrap Gary's name in
`**...**`), `venue`, `venue_short` (badge), `year`, `role`, `url`, `teaser` (960x600,
panels on a light background), `teaser_alt`, and `summary` in plain words. Use `doi` when
there is one; otherwise `link_label` names the main link (for example "OpenReview").
Optional `links` adds extra links such as the project page or code, and `teaser_credit`
holds figure attribution. Add new papers to the resume HTML too and regenerate the PDF.

## Theme & Build

- **Theme:** custom layouts in `_layouts/` and styles in `assets/css/main.scss` (no remote theme)
- **Build:** GitHub Pages (automatic on push to main)
- **Fonts:** Inter + Fira Code (Google Fonts)
- **Local preview:** `bundle install` then `bundle exec jekyll serve`

## Conventions

- **No em dashes** in site copy. Use hyphens or commas. Use `x` rather than the multiplication sign.
- **Nav** is flat: each item in `_data/navigation.yml` needs a `url`.
- **Research ordering** uses the `order` key in each `_research/` item's front matter.
- **Post permalinks** are `/writing/:title/`. Cross-links must use that path.
- **No personal contact details beyond email** on the public site (no phone, no street address).

## Contact email

The email address appears in exactly **two** places. Change both, then regenerate
the resume PDF and page image:

1. `_config.yml` -> `author.email`. This drives the homepage links row, the site
   footer, and the CV page (which reads `{{ site.author.email }}`).
2. `assets/resume/gary-feng-resume.html` -> the `.contact` block. This file is a
   standalone print source and is **not** processed by Liquid, so it cannot read
   the config value and must be edited by hand.

## Resume

There is now a **single source of truth** for resume content:
`assets/resume/gary-feng-resume.html`, the print source. It generates both the PDF
and the page image.

- `_pages/cv.md` shows the rendered page image linked to the PDF. It contains no
  resume text of its own, so it cannot drift.
- `index.md` and `_data/work.yml` carry a deliberately condensed summary and link to `/cv/`.
  Do not paste full resume bullets back into them.
- The upstream master is Gary's `Resume 2026.docx`. The site version adds the published
  Science Robotics citation, the NeurIPS 2026 GenAI4Health workshop paper, and
  CopilotWorldLab, and **omits the phone number** because the PDF is served publicly.

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
