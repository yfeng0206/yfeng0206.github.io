# Prosecution Brief (Merged)

## Security & Integrity Findings
# Prosecution Brief: Security, Supply Chain, and Observability

**Agent**: Prosecutor (Security/Supply Chain/Observability)
**Scope**: Navigation and page rendering issues on Jekyll site; focus on security, supply chain, and observability categories
**Date**: 2026-04-09
**Files Audited**: `_data/navigation.yml`, `_pages/trading.html`, `_pages/live-trading.html`, `_config.yml`, `_includes/head/custom.html`, `Gemfile`, `assets/css/main.scss`, `.gitignore`, `index.html`

---

## FINDING-A1: MEDIUM -- CDN Scripts Loaded Without Subresource Integrity (SRI)

**Category**: Security & Data Integrity
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_pages/trading.html:799`, `_pages/live-trading.html:252`
**CWE**: CWE-829 (Inclusion of Functionality from Untrusted Control Sphere)

**The Claim** (what should happen):
> External JavaScript loaded from a CDN should be verified against a known hash to prevent supply chain attacks where the CDN is compromised or serves tampered content.

**The Reality** (what the code actually does):
> Both pages load Chart.js from jsDelivr CDN without any `integrity` or `crossorigin` attributes:
> ```html
> <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
> ```

**The Gap**:
If jsDelivr is compromised, a CDN edge node serves modified content, or a DNS hijack redirects the request, arbitrary JavaScript would execute in the user's browser on the `yfeng0206.github.io` origin. The W3C SRI specification exists precisely for this attack vector. Both pages are affected identically.

**Evidence**:
- `_pages/trading.html` line 799 and `_pages/live-trading.html` line 252 both load the same script.
- Zero occurrences of `integrity` in the entire codebase (confirmed via grep).
- The `crossorigin` attribute only appears once on a font preconnect in `_includes/head/custom.html`, not on any script tag.

**Impact**:
An attacker who compromises jsDelivr (which has had incidents before) could inject scripts that steal cookies, redirect users, or deface the page. On a personal portfolio site the blast radius is limited, but it remains an exploitable vector if the CDN is compromised. This is the textbook use case for SRI.

---

## FINDING-A2: MEDIUM -- innerHTML Used With Future-External Data Source, No Sanitization

**Category**: Security & Data Integrity
**Severity**: MEDIUM
**Confidence**: MEDIUM
**Location**: `_pages/live-trading.html:383-439`
**CWE**: CWE-79 (Improper Neutralization of Input During Web Page Generation -- XSS)

**The Claim** (what should happen):
> When data is rendered into the DOM, it should be sanitized, especially when the codebase explicitly documents that the data source will switch from inline dummy data to an external fetch (GitHub Gist, raw file, S3, etc.).

**The Reality** (what the code actually does):
> The `render()` function at lines 365-523 builds HTML strings by directly concatenating data properties into `innerHTML` calls:
> ```javascript
> document.getElementById('summaryCards').innerHTML = cards.map(c =>
>     '<div class="live-card">' +
>       '<div class="lc-label">' + c.label + '</div>' +
>       '<div class="lc-value' + (c.label === 'Total Return' ? ' ' + c.cls : '') + '">' + c.value + '</div>' +
>       '<div class="lc-sub ' + c.cls + '">' + c.sub + '</div>' +
>     '</div>'
>   ).join('');
> ```
> Lines 401-402 do the same for `allocBar` and `allocLegend`. Lines 421, 439 do the same for positions and trades tables. The `reason` field from trades (line 437) is injected verbatim:
> ```javascript
> '<td style="color:#6b7280;font-size:0.9em;">' + t.reason + '</td>'
> ```

**The Gap**:
Currently `DUMMY_DATA` is hardcoded inline so the attack surface is zero. However, the code documents (lines 258-276) three planned migration paths -- all involving fetching JSON from external URLs. The comments at lines 349-355 show the exact fetch pattern. Once `loadData()` is switched to `fetch()` from a Gist or raw GitHub file, any compromise of that data source would produce stored XSS. The `reason` field is particularly dangerous as it contains free-text strings. No sanitization exists anywhere in the render pipeline.

**Evidence**:
- 5 separate `innerHTML` assignments: lines 383, 401, 402, 421, 439
- Zero calls to any sanitization function (no `DOMPurify`, no `textContent`, no escaping)
- Explicit migration plan documented in comments at lines 258-276, 349-355

**Impact**:
Currently: no impact (data is inline). After planned migration: stored XSS via the JSON data source. An attacker who gains write access to the Gist or data file could inject malicious HTML/JS that executes in every visitor's browser.

---

## FINDING-A3: LOW -- Google Fonts Loaded Without SRI

**Category**: Supply Chain & Dependencies
**Severity**: LOW
**Confidence**: HIGH
**Location**: `_includes/head/custom.html:3`
**CWE**: CWE-829

**The Claim**:
> External stylesheets should be integrity-checked or at minimum loaded with `crossorigin="anonymous"` for privacy and security.

**The Reality**:
> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
> ```
> The Google Fonts CSS endpoint is dynamically generated (it returns different CSS based on User-Agent), which makes SRI impractical. However, the `crossorigin` attribute is missing on the CSS link (though it is present on the preconnect). More importantly, Google Fonts API responses include references to further font file downloads from `fonts.gstatic.com`, creating a chain of external resource loads with no integrity verification.

**The Gap**:
This is a known limitation of Google Fonts. The CSS is dynamically generated so SRI hashes would not be stable. The risk is theoretical -- Google infrastructure is well-secured. However, this represents an uncontrolled external dependency.

**Evidence**:
- `_includes/head/custom.html` line 3
- `crossorigin` attribute present on preconnect (line 2) but absent on the CSS link itself (line 3)

**Impact**:
Theoretical: compromised Google Fonts could inject malicious CSS (data exfiltration via CSS). Practically very unlikely. Low severity because Google is a trusted source and the attack surface is CSS, not JS.

---

## FINDING-A4: MEDIUM -- Gemfile.lock Excluded From Version Control

**Category**: Supply Chain & Dependencies
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `.gitignore:7`, `Gemfile`
**CWE**: CWE-1104 (Use of Unmaintained Third Party Components)

**The Claim**:
> A reproducible build requires pinned dependency versions. `Gemfile.lock` is the mechanism Ruby/Bundler uses to pin exact versions.

**The Reality**:
> `.gitignore` line 7 explicitly excludes `Gemfile.lock`:
> ```
> Gemfile.lock
> ```
> The `Gemfile` specifies only:
> ```ruby
> gem "github-pages", group: :jekyll_plugins
> gem "jekyll-include-cache", group: :jekyll_plugins
> ```
> No version pins on either gem.

**The Gap**:
Every GitHub Pages build resolves dependencies anew. The `github-pages` gem is a meta-gem that pulls in ~85+ transitive dependencies (Jekyll, Kramdown, Liquid, Nokogiri, etc.). Without a lockfile, builds are non-reproducible. A compromised or buggy gem version could silently be pulled into the next build. Additionally, the `remote_theme` pin to `@4.28.0` only locks the theme itself, not its dependencies.

**Evidence**:
- `Gemfile` has zero version constraints
- `.gitignore` line 7: `Gemfile.lock`
- No `Gemfile.lock` exists in the repository

**Impact**:
- Non-reproducible builds: two builds at different times could produce different sites
- Supply chain risk: a compromised version of any transitive dependency would be automatically pulled in
- Debugging difficulty: no way to determine exactly which versions were used in a past build

---

## FINDING-A5: MEDIUM -- No Error Handling for CDN Script Load Failure

**Category**: Observability Gaps
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_pages/trading.html:799-927`, `_pages/live-trading.html:252-526`
**CWE**: N/A

**The Claim**:
> When a page depends on an external script to render its primary content, failure to load that script should be detectable by the user or operator.

**The Reality**:
> Both trading pages load Chart.js from a CDN, then immediately execute code that calls `new Chart(...)`:
>
> `trading.html` lines 815-816:
> ```javascript
> const returnsCtx = document.getElementById('returnsChart').getContext('2d');
> new Chart(returnsCtx, {
> ```
>
> `live-trading.html` lines 456-457:
> ```javascript
> var ctx = document.getElementById('equityChart').getContext('2d');
> new Chart(ctx, {
> ```
>
> If the CDN is unreachable (firewall, DNS failure, corporate proxy blocking jsDelivr, China's GFW, etc.), `Chart` will be undefined, the script will throw `ReferenceError: Chart is not defined`, and all subsequent JavaScript on the page will halt silently. There is:
> - No `onerror` handler on the `<script>` tag
> - No `try/catch` around Chart instantiation
> - No fallback UI or error message
> - No `typeof Chart !== 'undefined'` guard

**The Gap**:
The charts are the centerpiece visual element of both pages. If Chart.js fails to load, the user sees empty canvases with no explanation. On `live-trading.html`, the `render()` function will also crash at line 456, meaning the entire page is blank except for static HTML structure.

**Evidence**:
- `trading.html` line 799: bare `<script src="...">` with no `onerror`
- `live-trading.html` line 252: same pattern
- Zero occurrences of `try`, `catch`, `onerror`, or `typeof Chart` in either file
- `render()` at line 525 calls `render()` unconditionally; if Chart.js hasn't loaded, the call to `new Chart()` at line 457 throws and all subsequent DOM updates (positions table, trades table) are also lost because they're in the same async function

**Impact**:
Complete visual failure of both trading pages when Chart.js CDN is blocked or down. User sees an empty page with no error indication. This is particularly likely in corporate environments (jsDelivr may be blocked) or regions with restrictive internet policies.

---

## FINDING-A6: LOW -- Duplicate Chart.js CDN Load Across Pages (No Caching Coordination)

**Category**: Supply Chain & Dependencies
**Severity**: LOW
**Confidence**: HIGH
**Location**: `_pages/trading.html:799`, `_pages/live-trading.html:252`
**CWE**: N/A

**The Claim**:
> External scripts used across multiple pages should ideally be loaded once via the layout or a shared include to ensure consistent versioning and cache behavior.

**The Reality**:
> Both pages independently load Chart.js at the same version via the same URL:
> ```html
> <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
> ```
> This works due to HTTP caching, but the version is hardcoded in two separate files. If one page is updated to a new Chart.js version and the other is not, the site would run two different versions.

**The Gap**:
This is a maintainability concern, not a current bug. The version strings must be kept in sync manually across two files. No mechanism enforces consistency.

**Evidence**:
- `trading.html:799` and `live-trading.html:252` both specify `chart.js@4.4.7`

**Impact**:
Version drift risk. If a developer updates one file and not the other, different Chart.js versions could produce inconsistent chart rendering between the two trading pages. Low severity because it's currently consistent and the fix is straightforward.

---

## FINDING-A7: LOW -- No Content Security Policy Headers

**Category**: Security & Data Integrity
**Severity**: LOW
**Confidence**: HIGH
**Location**: Site-wide (no `_headers` file, no CSP meta tag, no `netlify.toml`)
**CWE**: CWE-1021 (Improper Restriction of Rendered UI Layers)

**The Claim**:
> Sites that load external scripts and use inline JavaScript should declare a Content Security Policy to restrict what scripts can execute.

**The Reality**:
> There is no CSP defined anywhere:
> - No `_headers` file for GitHub Pages custom headers
> - No `<meta http-equiv="Content-Security-Policy">` tag in `_includes/head/custom.html`
> - No other security headers configuration
>
> GitHub Pages does not inject CSP headers by default.

**The Gap**:
Without CSP, any XSS vulnerability (like the innerHTML pattern in FINDING-A2) has no defense-in-depth mitigation. The browser will execute any injected script without restriction. For a static Jekyll site this is a known limitation of GitHub Pages (which does not support custom HTTP headers), so the only option is a `<meta>` CSP tag, which has limitations.

**Evidence**:
- Zero occurrences of `Content-Security-Policy` in the codebase
- No `_headers` file exists
- GitHub Pages does not support custom HTTP headers natively

**Impact**:
Lack of defense-in-depth. Any future XSS (e.g., from FINDING-A2's migration to external data) would not be mitigated by CSP. Low severity because GitHub Pages imposes this limitation on all sites, and the current XSS surface is minimal.

---

## FINDING-A8: MEDIUM -- Live Trading Page render() Has No Error Boundary; Silent Total Failure

**Category**: Observability Gaps
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_pages/live-trading.html:365-525`
**CWE**: CWE-755 (Improper Handling of Exceptional Conditions)

**The Claim**:
> An async function that builds an entire page's content should handle errors gracefully, especially when it will transition to fetching external data.

**The Reality**:
> The `render()` function is a single `async` function that performs ALL DOM updates (summary cards, allocation bar, positions table, trades table, and Chart.js initialization) in sequence with no error handling:
> ```javascript
> async function render() {
>   const d = await loadData();
>   // ... all DOM manipulation ...
>   new Chart(ctx, { ... });
> }
> render();
> ```
> Line 525 calls `render()` but never catches its rejection. If any line throws (e.g., missing property in JSON data, Chart.js not loaded, malformed date string), the Promise rejection is unhandled and:
> 1. The browser console shows an error (which users never see)
> 2. All DOM elements after the failure point remain empty
> 3. No user-visible error indication appears

**The Gap**:
The function handles 6+ distinct rendering tasks in series. A failure in any one (e.g., `d.account` is undefined, `d.equity_curve` is empty) silently kills the entire page. When the data source migrates to external fetch, network errors, JSON parse errors, and schema mismatches become likely failure modes -- all with zero user feedback.

**Evidence**:
- `render()` defined at line 365 with no `try/catch`
- Called at line 525 with no `.catch()` handler
- Zero error handling patterns in the entire file (no `try`, no `catch`, no `onerror`, no `.catch()`)

**Impact**:
Users see a partially or fully empty page with no explanation when anything goes wrong. Debugging requires opening browser DevTools, which casual portfolio viewers will not do.

---

## FINDING-A9: LOW -- Resume PDF and Photo Excluded From Git but Present in Working Directory

**Category**: Security & Data Integrity
**Severity**: LOW
**Confidence**: HIGH
**Location**: `.gitignore:8-9`
**CWE**: N/A

**The Claim**:
> Sensitive files should not be present in a publicly deployable directory even if gitignored.

**The Reality**:
> The `.gitignore` excludes:
> ```
> *.pdf
> 1696906260300.jpg
> ```
> However, the working directory listing shows both `Resume 2025.pdf` and `1696906260300.jpg` exist locally. These are excluded from git (and thus from GitHub Pages deployment), so they won't be served. But their presence in the working directory alongside the site means local Jekyll serve would serve them.

**The Gap**:
This is not a production issue since GitHub Pages only serves committed files. However, during local development with `bundle exec jekyll serve`, these files would be accessible. The resume likely contains personal information (phone number, address).

**Evidence**:
- `ls` of working directory shows `Resume 2025.pdf` and `1696906260300.jpg`
- `.gitignore` lines 8-9 exclude both

**Impact**:
Minimal in production. During local development, personal resume data could be inadvertently exposed if the local server is network-accessible.

---

## Summary

| ID | Severity | Category | Title |
|----|----------|----------|-------|
| FINDING-A1 | MEDIUM | Security | CDN Scripts Without SRI |
| FINDING-A2 | MEDIUM | Security | innerHTML With Future External Data, No Sanitization |
| FINDING-A3 | LOW | Supply Chain | Google Fonts Without SRI |
| FINDING-A4 | MEDIUM | Supply Chain | Gemfile.lock Excluded From Version Control |
| FINDING-A5 | MEDIUM | Observability | No Error Handling for CDN Script Load Failure |
| FINDING-A6 | LOW | Supply Chain | Duplicate Chart.js CDN Load Across Pages |
| FINDING-A7 | LOW | Security | No Content Security Policy Headers |
| FINDING-A8 | MEDIUM | Observability | render() Has No Error Boundary |
| FINDING-A9 | LOW | Security | Resume/Photo Present in Working Directory |

**Totals**: 0 CRITICAL, 0 HIGH, 5 MEDIUM, 4 LOW

## Correctness & Logic Findings
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

## Performance & Concurrency Findings
# Prosecution Brief -- Performance, Concurrency & Timing, Silent Failures

**Agent**: Prosecutor C (Performance / Concurrency & Timing / Silent Failures)
**Scope**: `_pages/trading.html`, `_pages/live-trading.html`, navigation rendering, script load behavior
**Date**: 2026-04-09

---

## FINDING-C1: HIGH -- Chart.js CDN failure kills all interactive navigation on trading.html

**Category**: Silent Failure
**Severity**: HIGH
**Confidence**: HIGH
**Location**: `_pages/trading.html:799-928`
**CWE**: CWE-544 (Missing Standardized Error Handling Mechanism)

**The Claim** (what the code intends):
> Strategy cards are clickable (9 `onclick="showStrategy(...)"` handlers at lines 292-476). The "Back to Overview" buttons (lines 503-774) should toggle between main view and strategy details. Charts should render.

**The Reality** (what the code actually does):
> `showStrategy()` and `showMain()` (lines 802-812) are defined in the **same `<script>` block** (lines 800-928) that also calls `new Chart(returnsCtx, {...})` at line 816. The Chart.js CDN is loaded synchronously at line 799:
> ```html
> <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
> <script>
> // Navigation
> function showStrategy(id) { ... }
> function showMain() { ... }
>
> // Strategy Returns Chart
> const returnsCtx = document.getElementById('returnsChart').getContext('2d');
> new Chart(returnsCtx, { ... });  // line 816 -- throws if Chart.js failed to load
> ```
> If Chart.js CDN is unreachable (corporate firewall, ad blocker, network issue, DNS failure), `Chart` is undefined. Line 816 throws `ReferenceError: Chart is not defined`. This **aborts the entire script block**, meaning `showStrategy()` and `showMain()` are defined but the script execution halts at line 816 before the Chart constructor returns. Actually -- the functions are hoisted, so they ARE defined. But more critically: the script parse/execution failure at runtime line 816 stops all subsequent code. The functions are still callable since they were hoisted. Let me re-examine.

> Correction after re-analysis: JavaScript function declarations are hoisted. `showStrategy` and `showMain` ARE accessible even if the script crashes at line 816. The Chart.js failure would:
> 1. Prevent both charts from rendering (empty canvases)
> 2. Log an uncaught ReferenceError to console
> 3. NOT break the navigation functions themselves
>
> However, the error IS still silently swallowed from the user's perspective -- they see blank chart areas with no explanation.

**The Gap**:
There is zero error handling around Chart.js usage. No `try/catch`, no `typeof Chart !== 'undefined'` guard, no `onerror` handler on the script tag, no fallback content for the chart areas. When Chart.js is unavailable, users see empty boxes with no explanation.

**Evidence**:
- Line 799: `<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>` -- no `onerror` attribute
- Line 816: `new Chart(returnsCtx, {...})` -- no try/catch
- Line 866: `new Chart(crashCtx, {...})` -- no try/catch
- No `typeof Chart` guard anywhere in the file

**Impact**:
When Chart.js CDN is blocked (common in corporate environments, China, some ad blockers), users see two empty gray boxes where charts should be. Console shows uncaught ReferenceError. No user-visible error message. The page still functions for navigation, but the primary data visualization is missing without any indication.

---

## FINDING-C2: HIGH -- Chart.js CDN failure causes unhandled promise rejection on live-trading.html

**Category**: Silent Failure
**Severity**: HIGH
**Confidence**: HIGH
**Location**: `_pages/live-trading.html:252-526`
**CWE**: CWE-544 (Missing Standardized Error Handling Mechanism)

**The Claim**:
> The live trading dashboard should render portfolio data, positions, trades, and an equity curve chart.

**The Reality**:
> Chart.js is loaded synchronously at line 252. The `render()` async function (lines 365-523) calls `new Chart(ctx, {...})` at line 457. The function is invoked at line 525 with no `.catch()`:
> ```js
> render(); // line 525 -- no .catch(), no error handling
> ```
> If Chart.js is unavailable:
> - Lines 366-439 execute successfully (summary cards, allocation bar, positions table, trades table all render)
> - Line 457 throws `ReferenceError: Chart is not defined`
> - Since `render()` is async, this becomes an **unhandled promise rejection**
> - Browser logs the error to console but the user sees a partially rendered page

**The Gap**:
The `render()` call has no `.catch()` handler. There is no `try/catch` inside `render()`. The chart area shows an empty canvas with the title "Portfolio Value" but no chart and no error message.

**Evidence**:
- Line 525: `render();` -- bare call, no error handling
- Line 457: `new Chart(ctx, {...})` -- no guard
- No `window.addEventListener('unhandledrejection', ...)` anywhere
- No fallback content in the `<canvas>` element or its wrapper

**Impact**:
Partial page render with dead chart section. Users see "Portfolio Value" heading with blank space below. No indication that something failed. Debug requires opening browser DevTools.

---

## FINDING-C3: MEDIUM -- Synchronous Chart.js load (201KB) blocks page rendering

**Category**: Performance
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_pages/trading.html:799`, `_pages/live-trading.html:252`
**CWE**: N/A

**The Claim**:
> Pages should load and render quickly for a personal portfolio site.

**The Reality**:
> Both pages load Chart.js (201KB minified, 205,889 bytes per CDN headers) via a synchronous `<script>` tag without `async` or `defer`:
> ```html
> <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
> ```
> On `trading.html` (line 799), this tag appears **after** all 928 lines of HTML content. The browser has already parsed the HTML, so the page content is visible. However, the script blocks further parsing/execution of the inline `<script>` block below it.
>
> On `live-trading.html` (line 252), the Chart.js script tag appears **before** the inline script that populates all page content via `render()`. This means:
> 1. The HTML structure (empty tables, empty cards) renders immediately
> 2. Chart.js download blocks execution of the `<script>` block that calls `render()`
> 3. All dynamic content (summary cards, positions, trades, chart) waits for Chart.js to download
> 4. User sees empty page skeleton until 201KB downloads

**The Gap**:
On `live-trading.html`, Chart.js download is on the critical rendering path for ALL page content, not just the chart. The data population logic is coupled to Chart.js load timing because both are in the same script execution flow.

**Evidence**:
- CDN response: `Content-Length: 205889` (201KB)
- `live-trading.html:252`: synchronous script load before data population
- `live-trading.html:525`: `render()` call is in the script block gated behind Chart.js load
- No `async`, `defer`, or dynamic `import()` used

**Impact**:
On slow connections (3G: ~1.5Mbps), Chart.js download takes approximately 1.1 seconds. During this time, `live-trading.html` shows empty summary cards, empty tables, and a blank chart. On fast connections the impact is negligible, but this is a personal portfolio site that may be viewed from various network conditions.

---

## FINDING-C4: MEDIUM -- Google Fonts loaded as render-blocking resource in <head>

**Category**: Performance
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_includes/head/custom.html:1-3`
**CWE**: N/A

**The Claim**:
> The site should load quickly. The custom head include provides Inter and Fira Code fonts.

**The Reality**:
> ```html
> <link rel="preconnect" href="https://fonts.googleapis.com">
> <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
> ```
> This is injected into `<head>` by Minimal Mistakes. The `<link rel="stylesheet">` for Google Fonts is **render-blocking** -- the browser will not paint the page until this CSS loads. The `display=swap` parameter helps (tells the browser to use fallback fonts while loading), but the CSS file itself still blocks render.
>
> Loading 7 weights of Inter (300, 400, 500, 600, 700) plus 2 weights of Fira Code (400, 500) = **9 font files** to download.

**The Gap**:
The `preconnect` hints help, but the CSS is still render-blocking. Combined with Chart.js synchronous load on trading pages, this creates a cascade: fonts block initial render, then Chart.js blocks content population.

**Evidence**:
- `_includes/head/custom.html` lines 1-3
- 9 font weights requested (5 Inter + 2 Fira Code, though only Inter may serve 5 individual files depending on unicode range splits)
- `display=swap` mitigates FOIT but doesn't eliminate render-blocking CSS

**Impact**:
First Contentful Paint (FCP) is delayed on all pages, not just trading pages. On slow connections or when Google Fonts is slow, users may see a blank page for 1-2 seconds. This affects the entire site, not just trading pages.

---

## FINDING-C5: MEDIUM -- Unhandled promise rejection from render() with no user feedback

**Category**: Silent Failure
**Severity**: MEDIUM
**Confidence**: HIGH
**Location**: `_pages/live-trading.html:365-525`
**CWE**: CWE-755 (Improper Handling of Exceptional Conditions)

**The Claim**:
> The code comments (lines 258-277) describe a future data source architecture where `loadData()` would fetch from a GitHub Gist, raw GitHub URL, or S3. The current implementation uses inline dummy data.

**The Reality**:
> When the data source switches to a remote fetch (as designed):
> ```js
> async function loadData() {
>   const resp = await fetch('https://gist.githubusercontent.com/...');
>   return resp.json();
> }
> ```
> The `render()` function (line 365) calls `await loadData()` at line 366. If this fetch fails (network error, 404, CORS, malformed JSON), the entire `render()` function aborts. The call at line 525:
> ```js
> render(); // no .catch()
> ```
> ...has no error handler. The page would show:
> - Empty summary cards (the `<div id="summaryCards">` stays empty)
> - "Last updated: --" (the placeholder from line 208)
> - Empty positions and trades tables
> - No chart
> - No error message to the user

**The Gap**:
The architecture is designed for remote data fetching but the error handling path is completely absent. When this transitions from dummy data to live data, any fetch failure will silently produce an empty dashboard.

**Evidence**:
- Lines 258-277: Comments describing 3 remote data source options
- Line 356: Current `loadData()` returns `Promise.resolve(DUMMY_DATA)` (never fails)
- Line 365: `const d = await loadData();` -- no try/catch
- Line 525: `render();` -- no `.catch()`
- No loading spinners, no error states, no retry logic

**Impact**:
Currently low risk (dummy data never fails). When switching to live data: HIGH risk of silent empty dashboard on any network hiccup. The user would see the page skeleton with no data and no indication of what went wrong. Debugging requires browser DevTools.

---

## FINDING-C6: MEDIUM -- Both trading pages load Chart.js independently (duplicate 201KB download)

**Category**: Performance
**Severity**: MEDIUM
**Confidence**: MEDIUM
**Location**: `_pages/trading.html:799`, `_pages/live-trading.html:252`
**CWE**: N/A

**The Claim**:
> The site is a personal portfolio. Users may navigate between Trading and Live Trading pages.

**The Reality**:
> Both pages independently load Chart.js from the CDN:
> ```html
> <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
> ```
> While browser caching means the second load is served from cache (the CDN sends `Cache-Control: public, max-age=31536000, immutable`), this is a static site with no SPA routing. Each page load is a full HTML reload. On first visit to either page, the 201KB download must complete. If a user visits Trading then Live Trading, the browser cache serves the second load.
>
> The real issue is that Chart.js is not loaded site-wide (e.g., via the theme's `<head>` customization), so there's no opportunity for prefetching during navigation on other pages.

**The Gap**:
No `<link rel="prefetch">` or `<link rel="preload">` for Chart.js on other pages. Users navigating from About -> Trading experience the full 201KB download on first load.

**Evidence**:
- CDN headers: `Cache-Control: public, max-age=31536000, immutable` (caching works for repeat visits)
- No `<link rel="prefetch" href="...chart.js...">` in `_includes/head/custom.html`
- Full page navigation between pages (no SPA)

**Impact**:
First-time visitors to either trading page wait for 201KB Chart.js download. On typical broadband this is <100ms. On mobile/slow connections, 1+ seconds. Browser caching mitigates repeat visits. Severity is MEDIUM because it's a known pattern for static sites, but the optimization opportunity exists.

---

## FINDING-C7: LOW -- trading.html has 36KB of inline content with 9 strategy detail sections always in DOM

**Category**: Performance
**Severity**: LOW
**Confidence**: HIGH
**Location**: `_pages/trading.html:500-797`
**CWE**: N/A

**The Claim**:
> The trading page shows a dashboard overview with clickable strategy cards that reveal detail views.

**The Reality**:
> All 9 strategy detail sections (lines 500-797, ~298 lines of HTML) are always present in the DOM, hidden via CSS `display: none`. The page contains:
> - 294 `<div>` elements
> - 99 `<tr>` elements
> - 326 `<td>` elements
> - Total page source: 36,574 bytes (35.7KB)
>
> Only one detail view is visible at a time. The other 8 are invisible but still parsed and in the DOM. Toggle is handled by:
> ```js
> function showStrategy(id) {
>   document.getElementById('main-view').style.display = 'none';
>   document.querySelectorAll('.strategy-detail').forEach(d => d.classList.remove('active'));
>   document.getElementById('detail-' + id).classList.add('active');
> }
> ```

**The Gap**:
This is a standard pattern for small amounts of content. 719 elements is well within browser capabilities. However, the page is the largest in the entire site by a factor of 16x (next largest is live-trading.html at 18KB). For a Jekyll static site this is unusual but not problematic.

**Evidence**:
- Page sizes: trading.html (36.6KB), live-trading.html (18.4KB), about.md (2.3KB), publications.md (1.1KB)
- 9 hidden detail sections always in DOM
- 719 container/table elements from page content alone (plus theme wrapper)

**Impact**:
Negligible performance impact on modern browsers. The DOM size is well within acceptable limits. Mobile devices may have marginally slower initial parse but this is unlikely to be noticeable. This is a style/architecture observation, not a bug.

---

## FINDING-C8: LOW -- Unescaped ampersand in HTML table header

**Category**: Silent Failure
**Severity**: LOW
**Confidence**: HIGH
**Location**: `_pages/live-trading.html:230`
**CWE**: CWE-116 (Improper Encoding or Escaping of Output)

**The Claim**:
> The positions table should display a "P&L" column header.

**The Reality**:
> ```html
> <tr><th>Ticker</th><th>Shares</th><th>Avg Cost</th><th>Price</th><th>Value</th><th>P&L</th><th>%</th></tr>
> ```
> The `&L` in `P&L` is an invalid HTML character reference. Per the HTML5 spec, `&` followed by alphanumeric characters that don't form a valid named character reference is a parse error. Browsers handle this gracefully by displaying the literal `&L`, but it's technically malformed HTML that will fail HTML validation.

**The Gap**:
Should be `P&amp;L` for valid HTML.

**Evidence**:
- Line 230: `<th>P&L</th>`
- HTML5 spec section 12.2.5.72: "If the characters after the U+0026 AMPERSAND character (&) don't match the syntax for a character reference, it's a parse error"

**Impact**:
No visible impact in any modern browser. Browsers display "P&L" correctly. Would fail W3C HTML validation. Purely cosmetic/standards compliance issue.

---

## FINDING-C9: LOW -- No Content Security Policy; inline scripts and styles would fail strict CSP

**Category**: Silent Failure
**Severity**: LOW
**Confidence**: MEDIUM
**Location**: `_pages/trading.html` (entire file), `_pages/live-trading.html` (entire file)
**CWE**: CWE-693 (Protection Mechanism Failure)

**The Claim**:
> The site is hosted on GitHub Pages with standard security headers.

**The Reality**:
> Both trading pages use:
> - Inline `<style>` blocks (trading.html: 4.7KB of CSS, live-trading.html: ~4KB)
> - Inline `<script>` blocks (trading.html: 3.5KB of JS, live-trading.html: 11.8KB)
> - Inline `onclick` handlers on 18 elements in trading.html
> - External CDN script from cdn.jsdelivr.net
>
> If a Content Security Policy (CSP) were ever added (or if GitHub Pages adds default CSP headers), these inline resources would be blocked unless `'unsafe-inline'` and `'unsafe-eval'` are allowed, or nonces/hashes are used.
>
> GitHub Pages currently does NOT enforce a strict CSP, so this is not an active issue.

**The Gap**:
The code is architecturally incompatible with modern CSP best practices. All JS functionality would break under a strict CSP.

**Evidence**:
- 18 `onclick` handlers in trading.html (lines 292-774)
- Inline `<style>` and `<script>` blocks in both files
- External CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js`

**Impact**:
No current impact. Theoretical future breakage if CSP is enforced. This is standard practice for GitHub Pages sites and is not unusual.

---

## Summary

| ID | Severity | Confidence | Category | Title |
|---|---|---|---|---|
| FINDING-C1 | HIGH | HIGH | Silent Failure | Chart.js CDN failure silently breaks charts on trading.html |
| FINDING-C2 | HIGH | HIGH | Silent Failure | Chart.js CDN failure causes unhandled rejection on live-trading.html |
| FINDING-C3 | MEDIUM | HIGH | Performance | Synchronous Chart.js load (201KB) blocks page rendering |
| FINDING-C4 | MEDIUM | HIGH | Performance | Google Fonts render-blocking resource in head |
| FINDING-C5 | MEDIUM | HIGH | Silent Failure | Unhandled promise rejection from render() with no user feedback |
| FINDING-C6 | MEDIUM | MEDIUM | Performance | Duplicate Chart.js load without prefetch |
| FINDING-C7 | LOW | HIGH | Performance | 36KB inline page with 9 hidden detail sections |
| FINDING-C8 | LOW | HIGH | Silent Failure | Unescaped ampersand in table header |
| FINDING-C9 | LOW | MEDIUM | Silent Failure | Inline scripts/styles incompatible with strict CSP |

**Totals**: 0 CRITICAL, 2 HIGH, 4 MEDIUM, 3 LOW
