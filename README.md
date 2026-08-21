# yfeng0206.github.io -- Developer Reference

> Not published. Jekyll on GitHub Pages excludes README.md.

Custom Jekyll theme (no external theme gem), built by GitHub Pages' native
Jekyll. Pushing to `main` publishes within about a minute.

## Working on this site

**Do not commit directly to `main`.** Branch, push, open a pull request:

```powershell
git switch -c change-description
# ...edit...
python tools\validate_site.py   # front matter, layouts, links, assets, nav
python tools\css_audit.py       # every class used in a layout has a rule
git add -A
git commit -F .git\COMMIT_MSG.txt
git push -u origin change-description
```

Merge the PR on GitHub. `backup-before-redesign` holds the pre-2026 site
(Minimal Mistakes, dark skin) and is pushed to GitHub; leave it alone.

### Checks before pushing

- `tools\validate_site.py` must pass. It resolves every internal link, teaser
  and asset against real permalinks, confirms layouts and includes exist, and
  checks the nav resolves.
- `tools\css_audit.py` lists classes used in layouts with no CSS rule. `.prev`
  is expected: it is a marker on the post-nav link, styled via `.pn`.
- For visual changes, screenshot at real widths (1440, 1280, 520) before
  pushing. Do not judge layout from tall synthetic windows.
- Headless Chrome enforces a **minimum window width** of roughly 485px, so
  `--window-size=390` produces a cropped screenshot, not a reflowed one. It
  looks broken when it is not. Detect real overflow by comparing
  `document.documentElement.scrollWidth` to `clientWidth` inside the page.

## Structure

```
index.md                 Home: bio, links row, Experience, Full CV link
_pages/
  research.md            /research/  publication + active research
  projects.md            /projects/  projects, grouped, plus Writeups
  cv.md                  /cv/        rendered CV image linked to the PDF
  404.md
_research/               2 items, full entries with teasers
_projects/               6 items, compact rows, grouped by `group`
_posts/                  5 writeups, surfaced on /projects/
_data/
  navigation.yml         Home, Research, Project, CV
  work.yml               Experience timeline on the home page
  publications.yml       The Science Robotics entry
_layouts/                default, home, page, post, work, worklist,
                         researchindex, postlist
_includes/work-row.html  Shared listing row (full and compact variants)
assets/css/main.scss     The entire stylesheet
assets/resume/           CV print source (HTML) + generated PDF and PNG
tools/                   validate_site.py, css_audit.py
```

## Conventions

- **No em dashes.** Use hyphens or commas. Use `x` not the multiplication sign.
- **Two reading layers.** Each research/project item has a plain-English
  `summary` and a technical `deck`. Listings lead with `summary` and show
  `deck` underneath in muted text. Keep `summary` free of jargon.
- **Monochrome.** Colour comes only from images. Links and titles use the text
  colour with a grey underline. Do not reintroduce coloured links or badges.
- **Scale.** 17px body on a 42rem measure, roughly 72 characters per line.
- **Ordering** is by the `order` key in front matter; `group` drives the
  headings on /projects/.
- **Do not duplicate facts** across Home, Research and the CV. Home carries the
  bio and experience summary; Research carries the work; the CV PDF is the
  complete record.

## URLs

Every pre-rebuild URL is preserved with `jekyll-redirect-from`:
`/about/` -> `/`, `/blog/` and `/writing/` -> `/projects/`, `/resume/` -> `/cv/`,
`/portfolio/`, `/publications/` and `/projects/` -> `/research/`, each
`/portfolio/<item>/` -> its new page, and old `/research/<post>/` -> `/writing/<post>/`.
Post URLs are `/writing/<slug>/` and must not change.

## Contact email

Two places, then regenerate the CV:

1. `_config.yml` -> `author.email` (drives home links row, footer, CV page)
2. `assets/resume/gary-feng-resume.html` -> `.contact` block. Standalone print
   source, not processed by Liquid, so it cannot read the config value.

## CV

`assets/resume/gary-feng-resume.html` is the single source. Regenerate both
artifacts after editing:

```powershell
$base = "C:\Users\Gary\yfeng0206.github.io\assets\resume\gary-feng-resume"
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu `
  --print-to-pdf="$base.pdf" --no-pdf-header-footer `
  "file:///C:/Users/Gary/yfeng0206.github.io/assets/resume/gary-feng-resume.html"

python -c "import pymupdf; from PIL import Image; d=pymupdf.open(r'$base.pdf'); d[0].get_pixmap(dpi=200).save(r'$base.raw.png'); Image.open(r'$base.raw.png').convert('P', palette=Image.ADAPTIVE, colors=64).save(r'$base.png', optimize=True)"
```

**Use an absolute `--print-to-pdf` path.** With a relative path Chrome headless
writes nothing and still exits 0, so the committed PDF silently goes stale.
Verify after generating:

```powershell
python -c "import pymupdf; d=pymupdf.open(r'assets\resume\gary-feng-resume.pdf'); print(len(d)); print(d[0].get_text()[:200])"
```

Headless Chrome cannot rasterise PDFs, so screenshotting `/cv/` or a PDF URL
always yields a blank frame. Verify with pymupdf text extraction instead.
The CV is tuned to fit exactly one page.

`.gitignore` ignores `*.pdf` with an explicit negation for
`assets/resume/gary-feng-resume.pdf`. Keep that negation if the filename
changes, or the CV stops shipping.

## Images

- `assets/images/sel-*` are purpose-built 16:10 teasers.
- The publication teaser is Figure 1 from the paper. Its robot photography is
  credited to Unitree in the figure caption, so the entry carries that credit.
- Do not embed a PDF with `<object>`/`<iframe>`. Chrome's "download PDFs instead
  of opening them" setting renders nothing and does not fall through to the
  fallback, leaving an empty box. Use a rendered image, as `/cv/` does.
