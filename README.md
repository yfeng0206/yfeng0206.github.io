# yfeng0206.github.io -- Developer Reference

> This file is NOT published to the website. Jekyll on GitHub Pages auto-excludes README.md.

## Site Structure Quick Reference

```
_pages/
  about.md             <-- Bio, work experience
  portfolio-archive.md <-- Grid of all portfolio items
  publications.md      <-- Papers
  blog.md              <-- Blog post archive
  404.md

_portfolio/
  ijepa-3d-oct.md         <-- I-JEPA OCT foundation model project
  slivit-3d-oct-glaucoma.md
  object-permanence-detection.md
  mot17-object-tracking.md
  ivalet-parking.md
  gesture-car.md
  self-driving-car.md

_posts/
  2026-04-08-consensus-ai-trader.md
  2026-03-18-ijepa-oct-training-log.md
  2026-03-12-slivit-glaucoma-training-log.md

_data/navigation.yml   <-- Top nav bar items
_config.yml            <-- Site config, portfolio order, theme settings
assets/images/         <-- All images (teasers, charts, SVGs)
```

## Theme & Build

- **Theme:** Minimal Mistakes v4.28.0 (remote theme, dark skin)
- **Build:** GitHub Pages (automatic on push to main)
- **Fonts:** Inter + Fira Code (Google Fonts)
- **Nav caveat:** Minimal Mistakes masthead does NOT support `children` dropdowns. All nav items must be flat with a `url`.
