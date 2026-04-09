# Prosecution Brief -- Logic, Contracts, Dead Code, Integration Gaps

**Prosecutor**: Logic/Contract/Integration Specialist
**Scope**: Navigation and page rendering for Trading / Live Trading nav items
**Date**: 2026-04-09
**Theme**: Minimal Mistakes v4.28.0 remote theme, GitHub Pages

---

## FINDING-B1: HIGH -- Minimal Mistakes masthead.html does NOT support `children` dropdown navigation (ROOT CAUSE)

**Category**: Contract Violation
**Severity**: HIGH
**Confidence**: HIGH
**Location**: `_data/navigation.yml` (as of commit 91ed4e1), `mmistakes/minimal-mistakes@4.28.0/_includes/masthead.html`
**CWE**: N/A

**The Claim** (what the commit message says should happen):
> "Navigation updated: Trading is now a dropdown (Backtest Results + Live Trading)" -- commit 91ed4e1

**The Reality** (what the code actually does):
The Minimal Mistakes v4.28.0 `masthead.html` template iterates `site.data.navigation.main` with:
```liquid
{%- for link in site.data.navigation.main -%}
  <li class="masthead__menu-item">
    <a href="{{ link.url | relative_url }}" ...>{{ link.title }}</a>
  </li>
{%- endfor -%}
```
There is NO handling of a `children` key. No conditional check, no nested loop, no dropdown rendering. The template blindly accesses `link.url` for every item.

When the "Trading" nav entry had `children` instead of `url`:
```yaml
- title: "Trading"
  children:
    - title: "Backtest Results"
      url: /trading/
    - title: "Live Trading"
      url: /live-trading/
```
`link.url` resolved to `nil`. The Liquid filter `relative_url` on `nil` produces the baseurl (empty string `""`). The rendered HTML became:
```html
<a href="">Trading</a>
```
Clicking this navigates to the current page (effectively doing nothing). The "Backtest Results" and "Live Trading" sub-items were completely invisible -- never rendered anywhere in the DOM.

**The Gap**:
The commit message claimed dropdown navigation was implemented, but the theme's masthead template has no dropdown support for the `main` navigation list. Minimal Mistakes only supports `children` for sidebar navigation (via `_includes/nav_list`), not for the top masthead navigation. The fix in commit 7a36784 switched to flat nav items, which correctly resolved the issue.

**Evidence**:
- Full `masthead.html` source for v4.28.0 (fetched via curl): zero occurrences of "children"
- The broken navigation.yml from commit 91ed4e1 (verified via `git show 91ed4e1:_data/navigation.yml`)
- Deployed site navigation after the fix (commit 7a36784) confirmed correct via `curl -s https://yfeng0206.github.io/about/ | grep Trading` showing proper `href="/trading/"` and `href="/live-trading/"` links
- Both `/trading/` and `/live-trading/` return HTTP 200 on the deployed site

**Impact**:
This was the ROOT CAUSE of the reported bug. The "Trading" link rendered as `href=""` (does nothing), and the "Live Trading" sub-item was never rendered at all. Users could not access either trading page via navigation.

---

## FINDING-B2: HIGH -- Broken navigation was deployed to production without pre-deploy validation

**Category**: Logic Gap
**Severity**: HIGH
**Confidence**: HIGH
**Location**: Git history: commits 91ed4e1 through 7a36784
**CWE**: N/A

**The Claim** (what should happen):
> Navigation changes should be tested before deploying to production.

**The Reality** (what the code actually does):
The git history shows:
1. Commit 91ed4e1 (02:23:16) -- introduced broken `children` YAML for dropdown nav
2. Commit 7a36784 (02:30:25) -- fixed navigation back to flat items

Both commits were pushed to `origin/main` and deployed via GitHub Pages. The GitHub Actions runs confirm three successful builds around this time. The broken navigation was deployed live because:
1. The `children` YAML was assumed to work without verifying the theme template
2. No local Jekyll build was run to preview the change (or if it was, the dropdown failure was not caught)
3. Jekyll does NOT fail when `link.url` is nil -- it silently renders `href=""`
4. No CI check validates `navigation.yml` structure against the theme's expected format

**The Gap**:
There is no pre-deployment validation step. Changes go directly from commit to production via GitHub Pages auto-build. The GitHub Pages build reported "success" because Jekyll treats nil href values as valid. The build system cannot distinguish between a working navigation and a broken one.

**Evidence**:
- `git log --oneline -5` shows 91ed4e1 and 7a36784 as consecutive commits to main
- `gh run list --limit 5` shows three builds around this time, all "completed success"
- The commit message for 7a36784 explicitly says "Dropdown wasn't rendering properly" confirming the issue was discovered post-deploy

**Impact**:
Any user visiting the site during the deployment window experienced broken navigation. More importantly, the deployment pipeline has no safeguards against this class of error. Future configuration mistakes will also go straight to production with a "success" build status.

---

## FINDING-B3: MEDIUM -- Greedy navigation hides Trading/Live Trading on medium viewports

**Category**: Logic Gap
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_data/navigation.yml:1-13`, `mmistakes/minimal-mistakes@4.28.0/assets/js/plugins/jquery.greedy-navigation.js`
**CWE**: N/A

**The Claim** (what should happen):
> All 6 navigation items (About, Portfolio, Publications, Trading, Live Trading, Blog) should be accessible to users.

**The Reality** (what the code actually does):
Minimal Mistakes uses a "greedy navigation" JavaScript plugin that dynamically measures available horizontal space and moves nav items that don't fit into a hidden hamburger menu. The plugin removes items from the END of the visible list first:
```javascript
$vlinks.children().last().prependTo($hlinks);
```

With 6 nav items, on viewports between approximately 768px and ~1100px, "Blog", "Live Trading", and possibly "Trading" will be pushed into the overflow `hidden-links` list. The hamburger toggle button (`greedy-nav__toggle`) only appears when items overflow, but:
1. Users may not notice the hamburger icon
2. If jQuery or the greedy-nav JS fails to load, `hidden-links` stays permanently hidden (it starts with `class="hidden-links hidden"`)
3. The site title "Yunchu (Gary) Feng" plus subtitle "ML Engineer" consumes significant horizontal space

**The Gap**:
Adding two new nav items (Trading, Live Trading) to a previously 4-item navigation significantly increases the chance of overflow. A user on a tablet or non-maximized browser could reasonably report "clicking Trading does nothing" if they're actually seeing the items only in the hamburger overflow menu, or if the items are hidden entirely due to JS issues.

**Evidence**:
- greedy-navigation.js source shows last-to-first removal order
- 6 nav items totaling ~49 characters of text plus padding/margins
- Deployed site `<ul class="hidden-links hidden"></ul>` starts empty, populated by JS

**Impact**:
On tablet-sized viewports (768-1100px), some trading nav items are hidden behind a hamburger menu. This is not a bug per se, but with 6 items it's a significant usability concern that contributes to the "Trading does nothing" perception.

---

## FINDING-B4: MEDIUM -- No cross-link between Trading and Live Trading pages

**Category**: Integration Gap
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_pages/trading.html`, `_pages/live-trading.html`
**CWE**: N/A

**The Claim** (what should happen):
> Commit 91ed4e1 message: "Trading is now a dropdown (Backtest Results + Live Trading)" -- implying these are related pages that should be easily navigable between each other.

**The Reality** (what the code actually does):
- `trading.html` contains zero references to `/live-trading/` or "Live Trading"
- `live-trading.html` contains zero references to `/trading/` or "Backtest"
- The only way to navigate between them is via the top masthead navigation
- The original intent to group them as a dropdown was abandoned

**The Gap**:
Since the dropdown approach was abandoned in favor of flat nav items, the two related trading pages are presented as independent top-level items with no in-page cross-reference. If a user lands on one page via a direct link, search engine, or bookmark, they have no indication the other page exists.

**Evidence**:
- `grep "live-trading" _pages/trading.html` returns 0 matches
- `grep "/trading/" _pages/live-trading.html` returns 0 matches
- Commit 91ed4e1 originally grouped them as sub-items of a "Trading" parent

**Impact**:
User experience gap. The trading page discusses backtest results for MixLLM, and the live trading page shows MixLLM live performance, but neither links to the other. Related content is siloed.

---

## FINDING-B5: MEDIUM -- Chart.js CDN dependency with no fallback, SRI, or graceful degradation

**Category**: Integration Gap
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_pages/live-trading.html:252`, `_pages/trading.html:799`
**CWE**: CWE-829 (Inclusion of Functionality from Untrusted Control Sphere)

**The Claim** (what should happen):
> Pages with charts should render reliably, and external scripts should be integrity-verified.

**The Reality** (what the code actually does):
Both trading pages load Chart.js from jsDelivr CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
```
No `integrity` or `crossorigin` attributes are present (Subresource Integrity is absent).

In `live-trading.html`, the `render()` function populates ALL dynamic content: summary cards (line 383), allocation bar (line 401), positions table (line 421), trades table (line 439), and the equity chart (line 457). If Chart.js fails to load, the `render()` function will throw `ReferenceError: Chart is not defined` at line 457, but by that point the non-chart content has already been rendered. However, the equity chart canvas will be empty.

In `trading.html`, the chart construction at lines 816 and 866 will fail, leaving two empty chart canvases. The strategy cards and detail views are static HTML and will still render.

**The Gap**:
No SRI hash means a CDN compromise could inject arbitrary JavaScript. No fallback means charts fail silently on networks where jsDelivr is blocked (corporate firewalls, certain countries).

**Evidence**:
- `_pages/live-trading.html:252`: `<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>`
- `_pages/trading.html:799`: identical CDN include
- No `integrity` attribute on either script tag

**Impact**:
On restricted networks, chart sections appear as blank canvases. Security: a CDN compromise could serve malicious JavaScript to all site visitors.

---

## FINDING-B6: MEDIUM -- Fix commit leaves no guard against navigation regression

**Category**: Logic Gap
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_data/navigation.yml:1-13`
**CWE**: N/A

**The Claim** (what should happen):
> Navigation configuration should be validated to prevent the `children` mistake from recurring.

**The Reality** (what the code actually does):
The fix in commit 7a36784 switched from the broken `children` syntax to flat nav items. However:
1. No comment in `navigation.yml` documents that `children` is unsupported in masthead nav
2. No CI validation checks that every nav entry has a `url` field
3. No check that all `url` values correspond to pages with matching `permalink` values
4. The Minimal Mistakes documentation for sidebar navigation DOES describe `children` as valid syntax, creating confusion

**The Gap**:
The same mistake could be made again by anyone editing the navigation. The Minimal Mistakes documentation actively documents `children` for sidebar nav, making it a natural assumption that it works for masthead nav too.

**Evidence**:
- Current `navigation.yml` has no comments warning against `children`
- The same mistake was already made once (commit 91ed4e1)
- Minimal Mistakes sidebar nav docs show `children` syntax

**Impact**:
Latent regression risk. The next person to edit navigation may try `children` again.

---

## FINDING-B7: LOW -- `layout: none` in index.html is incorrect; should be `layout: null`

**Category**: Contract Violation
**Severity**: LOW
**Confidence**: HIGH
**Location**: `index.html:2`
**CWE**: N/A

**The Claim** (what should happen):
> Jekyll's documented way to skip layout processing is `layout: null` (YAML null value).

**The Reality** (what the code actually does):
```yaml
layout: none
```
This is the string `"none"`, not YAML null. Jekyll looks for a layout file named `none.html` in `_layouts/`. It doesn't exist in Minimal Mistakes (verified: HTTP 404 on `https://raw.githubusercontent.com/mmistakes/minimal-mistakes/4.28.0/_layouts/none.html`). Jekyll 3.x silently falls back to no layout wrapping when the specified layout doesn't exist, producing a build warning.

**The Gap**:
The page works by accident, not by design. It relies on Jekyll's undocumented fallback behavior for missing layouts.

**Evidence**:
- `index.html` line 2: `layout: none`
- Minimal Mistakes v4.28.0 has no `none.html` layout
- Jekyll docs specify `layout: null` for no layout
- Deployed output is correct (raw HTML redirect) despite the incorrect layout value

**Impact**:
Build warning in logs. A future Jekyll version could change the behavior for missing layouts. Cosmetic issue with no current behavioral impact.

---

## FINDING-B8: LOW -- GitHub Pages reports `custom_404: false` despite custom 404.md existing

**Category**: Contract Violation
**Severity**: LOW
**Confidence**: LOW
**Location**: `_pages/404.md`, GitHub Pages configuration
**CWE**: N/A

**The Claim** (what should happen):
> The custom 404 page at `_pages/404.md` (permalink: `/404.html`) should be served for non-existent URLs.

**The Reality** (what the code actually does):
The GitHub Pages API response shows `"custom_404": false`. This may simply indicate that no explicit 404 configuration was set via the GitHub Pages settings UI, while Jekyll's convention of outputting a `404.html` at the root may still be respected by GitHub Pages. The `custom_404` API field may track UI-configured 404s, not Jekyll-generated ones.

**Evidence**:
- `gh api repos/yfeng0206/yfeng0206.github.io/pages` returned `"custom_404":false`
- `_pages/404.md` exists with `permalink: /404.html`

**Impact**:
Likely no impact -- Jekyll-generated 404.html is typically respected by GitHub Pages regardless of this API field. LOW confidence this is an actual issue.

---

## Summary Table

| ID | Severity | Confidence | Category | Title |
|---|---|---|---|---|
| FINDING-B1 | HIGH | HIGH | Contract Violation | Masthead does NOT support `children` dropdown (ROOT CAUSE) |
| FINDING-B2 | HIGH | HIGH | Logic Gap | Broken nav deployed without pre-deploy validation |
| FINDING-B3 | MEDIUM | HIGH | Logic Gap | Greedy nav hides Trading items on medium viewports |
| FINDING-B4 | MEDIUM | HIGH | Integration Gap | No cross-link between Trading and Live Trading pages |
| FINDING-B5 | MEDIUM | HIGH | Integration Gap | Chart.js CDN with no fallback or SRI |
| FINDING-B6 | MEDIUM | HIGH | Logic Gap | No guard against navigation regression |
| FINDING-B7 | LOW | HIGH | Contract Violation | `layout: none` should be `layout: null` |
| FINDING-B8 | LOW | LOW | Contract Violation | `custom_404: false` vs custom 404.md |

**Stats**: 2 HIGH, 4 MEDIUM, 2 LOW
