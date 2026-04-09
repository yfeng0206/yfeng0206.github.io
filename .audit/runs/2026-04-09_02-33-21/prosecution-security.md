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
