# AUDIT VERDICT REPORT

**Judge**: Claude Opus 4.6 (1M context)
**Date**: 2026-04-09
**Scope**: Navigation fix audit + full audit of cited files for Jekyll personal portfolio site (Minimal Mistakes v4.28.0, GitHub Pages)
**Git Commit**: 7a3678447343b355f2ad4ac1daf26b0fdea21cd3

---

## Executive Summary

This is a well-functioning personal portfolio site. The original bug (Trading/Live Trading nav items not working) has been correctly fixed. The codebase has no CRITICAL issues. The most actionable improvements are: (1) add error handling around Chart.js usage so charts degrade gracefully when the CDN is blocked, (2) add SRI hashes to the Chart.js CDN script tags, and (3) fix `layout: none` to `layout: null` in index.html. Most findings are LOW severity observations appropriate for a one-person portfolio site -- cosmetic, theoretical, or describing intended framework behavior.

---

## VERDICT: FINDING-1 -- Minimal Mistakes masthead does NOT support children dropdown (ROOT CAUSE)

**Ruling**: ACCEPT
**Final Severity**: MEDIUM (historical)

**Evidence Verified**: YES -- quotes match code. Current `navigation.yml` has flat items, no `children` key. Fix is deployed.

**Prosecutor's Argument**: The masthead template does not support `children` nav items; this was the root cause of the original bug.
**Defender's Argument**: Correct analysis, but the bug is already fixed in commit 7a36784; this is historical documentation.
**My Independent Observation**: `navigation.yml` currently has 6 flat nav items with proper URLs. The fix is correct and deployed.

**My Assessment**:
The Prosecutor's root cause analysis is accurate and valuable documentation. However, this is a resolved issue. The current code is correct. No further action needed.

**Ruling Rationale**:
The bug is fixed. Litmus test: "Would this block a release?" No -- the release is out and working. This finding served its purpose as root cause documentation.

---

## VERDICT: FINDING-2 -- Broken navigation deployed to production without validation

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- git history confirms 7-minute fix window.

**Prosecutor's Argument**: No CI validation caught the broken navigation before deployment; future config mistakes will also go straight to production.
**Defender's Argument**: This is a personal portfolio site; the deploy-and-check cycle IS the testing strategy; CI validation of YAML nav structure is disproportionate.
**My Independent Observation**: This is a single-developer personal site on GitHub Pages. The "deployment pipeline" is git push. This is normal.

**My Assessment**:
The Prosecutor is technically right that there is no CI, but this is a personal portfolio site. Adding CI/CD validation for a 13-line YAML file maintained by one person would be over-engineering. The bug was noticed and fixed in 7 minutes. The Defender's argument holds.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Maybe, as a suggestion. But the cost-benefit of CI for this site does not justify action. LOW -- process observation, not a defect.

---

## VERDICT: FINDING-3 -- Chart.js CDN failure silently breaks charts on trading.html

**Ruling**: FIX
**Final Severity**: MEDIUM

**Evidence Verified**: YES -- line 799 loads Chart.js without `onerror`; lines 816 and 866 call `new Chart()` with no try/catch. Functions `showStrategy` and `showMain` are hoisted and DO survive the crash (Prosecutor self-corrected).

**Prosecutor's Argument**: Chart.js CDN failure leaves empty chart canvases with no error message.
**Defender's Argument**: Navigation and static content still work; charts are supplementary; jsDelivr is reliable; MEDIUM not HIGH.
**My Independent Observation**: I traced the code path. If `Chart` is undefined at line 816, a `ReferenceError` is thrown. The functions at lines 802-812 are hoisted and survive. Lines 862-927 (crash chart) also fail. Users see two empty gray boxes. Static HTML (strategy cards, tables, detail sections) all render fine. This is degraded, not broken.

**My Assessment**:
Both sides are partially right. The Prosecutor identified a real issue: empty charts with no explanation. The Defender correctly notes that navigation and static content survive. I agree with MEDIUM: the happy path works, but an edge case (CDN blocked) produces a confusing experience with no feedback. The fix is trivial -- wrap Chart instantiation in try/catch and show a fallback message.

**Ruling Rationale**:
Litmus test: "Would you file a ticket for this?" Yes. Users in corporate environments or countries with CDN restrictions would see unexplained blank chart areas. MEDIUM.

**Recommended Direction**: Add `try { new Chart(...) } catch(e) { /* show fallback text in canvas container */ }` around both Chart instantiations in trading.html. Optionally add `onerror` on the script tag to show a message if Chart.js fails to load entirely.
**Priority**: NEXT_SPRINT

---

## VERDICT: FINDING-4 -- Chart.js CDN failure + render() no error boundary on live-trading.html

**Ruling**: FIX
**Final Severity**: MEDIUM

**Evidence Verified**: YES -- line 252 loads Chart.js; line 365 defines `async function render()` with no try/catch; line 525 calls `render()` with no `.catch()`. Lines 366-439 execute before the Chart call at line 457.

**Prosecutor's Argument**: CDN failure causes unhandled promise rejection; chart section dies silently.
**Defender's Argument**: Summary cards, allocation bar, positions table, and trades table all render successfully before the chart call; only the equity chart fails; page has WIP banner; future data migration is speculative.
**My Independent Observation**: I confirmed: `render()` populates DOM elements sequentially. Lines 366-439 handle summary cards, allocation, positions, and trades BEFORE the Chart call at line 457. If Chart.js is missing, those elements render correctly and only the chart fails. The Prosecutor's claim that "all DOM updates after the failure point remain empty" is misleading -- the chart is the LAST thing rendered, so nothing after it is lost.

**My Assessment**:
The Defender is right that most content survives. But the missing `.catch()` on `render()` at line 525 is a genuine code quality issue. When the data source eventually migrates to a remote fetch (as documented in comments at lines 258-276), a network failure would produce an empty page with no feedback. Adding a try/catch inside render() and a `.catch()` on the invocation is trivial and future-proofs the page.

**Ruling Rationale**:
Litmus test: "Would you file a ticket for this?" Yes -- both for the current Chart.js error boundary and for the clearly planned data migration path. MEDIUM.

**Recommended Direction**: Add try/catch inside `render()` with a user-visible error message in a designated error container. Add `.catch()` on the `render()` call at line 525. Guard the Chart instantiation separately so data tables still render if Chart.js is missing.
**Priority**: NEXT_SPRINT

---

## VERDICT: FINDING-5 -- CDN scripts loaded without Subresource Integrity (SRI)

**Ruling**: FIX
**Final Severity**: MEDIUM

**Evidence Verified**: YES -- both trading.html:799 and live-trading.html:252 load Chart.js without `integrity` or `crossorigin` attributes. Zero occurrences of `integrity` in codebase.

**Prosecutor's Argument**: CDN compromise could inject arbitrary JavaScript; SRI is the standard mitigation.
**Defender's Argument**: Agrees; fix cost is low.
**My Independent Observation**: Both sides agree. SRI is a best practice for CDN scripts. The fix is adding two attributes to two script tags.

**My Assessment**:
Straightforward improvement. Both sides agree. The blast radius on a personal site is limited, but the fix cost is near-zero.

**Ruling Rationale**:
Litmus test: "Would you file a ticket for this?" Yes. Standard security practice with trivial implementation cost. MEDIUM.

**Recommended Direction**: Generate SRI hash for Chart.js 4.4.7 UMD bundle and add `integrity="sha384-..."` and `crossorigin="anonymous"` to both script tags.
**Priority**: NEXT_SPRINT

---

## VERDICT: FINDING-6 -- innerHTML with future external data source, no sanitization

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- 5 innerHTML assignments at lines 383, 401, 402, 421, 439 of live-trading.html. Data source is inline `DUMMY_DATA` at line 356.

**Prosecutor's Argument**: When data source migrates to external fetch, innerHTML without sanitization creates stored XSS risk.
**Defender's Argument**: Data is currently inline and owner-controlled; vulnerability is theoretical for code that does not yet exist.
**My Independent Observation**: The data is hardcoded. The Prosecutor is flagging a future risk in code that has not been written yet. This is a valid note for when the migration happens, but not an actionable finding now.

**My Assessment**:
The Defender is right. This is a valid reminder for the future, but the current code has zero XSS surface. When `loadData()` is changed to fetch external data, sanitization should be added at that time. Rating theoretical future vulnerabilities in unwritten code inflates severity.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Yes, as a "remember to sanitize when you add the fetch." That makes it LOW. No current action needed.

---

## VERDICT: FINDING-7 -- Gemfile.lock excluded from version control

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- `.gitignore` line 7 excludes `Gemfile.lock`; `Gemfile` has no version pins.

**Prosecutor's Argument**: Non-reproducible builds from unpinned dependencies; supply chain risk.
**Defender's Argument**: GitHub Pages pins gem versions server-side; excluding Gemfile.lock is standard practice for GitHub Pages sites.
**My Independent Observation**: The Defender's argument is correct. The `github-pages` gem is a meta-gem maintained by GitHub that pins specific compatible versions. GitHub Pages builds use a fixed environment. Committing Gemfile.lock for GitHub Pages sites often causes more problems than it solves (version conflicts with the GitHub Pages build environment).

**My Assessment**:
The Defender is right. This is standard practice for GitHub Pages. The `github-pages` gem exists precisely to manage version compatibility. Supply chain risk is managed by GitHub, not by the site owner.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Only for non-GitHub-Pages Ruby projects. For this site, it is correct as-is.

---

## VERDICT: FINDING-8 -- Greedy navigation hides Trading items on medium viewports

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- 6 nav items in navigation.yml. Minimal Mistakes uses greedy navigation JS.

**Prosecutor's Argument**: 6 nav items push Trading/Live Trading to hamburger menu on medium viewports.
**Defender's Argument**: This is intended theme behavior; hamburger menu is a standard responsive design pattern.
**My Independent Observation**: The greedy navigation plugin is a deliberate feature of Minimal Mistakes. It gracefully handles overflow by moving items to a hamburger menu. This is not a bug.

**My Assessment**:
The Defender is right. This is the theme working as designed. Every responsive website with a nav bar has this behavior. The Prosecutor is describing a feature, not a defect.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Perhaps as an FYI. Not a bug.

---

## VERDICT: FINDING-9 -- No cross-link between Trading and Live Trading pages

**Ruling**: FIX
**Final Severity**: LOW

**Evidence Verified**: YES -- grep confirms zero cross-references between the two pages.

**Prosecutor's Argument**: Related trading pages have no in-page cross-reference; content is siloed.
**Defender's Argument**: Both pages accessible via top navigation; cross-links are a minor UX suggestion.
**My Independent Observation**: The trading page discusses backtest results for MixLLM, and live-trading shows MixLLM live performance. These are clearly related. A simple cross-link would improve discoverability.

**My Assessment**:
Both sides have merit. The top nav works, but a small inline link ("See also: Live Trading Dashboard" on the trading page, and "See also: Backtest Results" on the live-trading page) would be a genuine UX improvement. This is LOW severity but worth doing.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Yes. Quick UX win.

**Recommended Direction**: Add a brief cross-link sentence or button near the top of each trading page pointing to the other.
**Priority**: BACKLOG

---

## VERDICT: FINDING-10 -- No guard against navigation regression

**Ruling**: FIX
**Final Severity**: LOW

**Evidence Verified**: YES -- `navigation.yml` has no comments. 13 lines, single developer.

**Prosecutor's Argument**: No comments or CI prevent using `children` syntax again; the same mistake was already made once.
**Defender's Argument**: Single developer who now knows the constraint; a YAML comment is sufficient; CI is overkill.
**My Independent Observation**: A one-line comment in the YAML file costs nothing and prevents a known footgun.

**My Assessment**:
The Defender is right that CI is overkill. The Prosecutor is right that a comment is worthwhile since the mistake already happened once. Agree on adding a comment.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Yes, as a one-line suggestion.

**Recommended Direction**: Add a comment to `navigation.yml`: `# NOTE: Minimal Mistakes masthead does NOT support 'children' dropdown. Keep items flat.`
**Priority**: BACKLOG

---

## VERDICT: FINDING-11 -- Synchronous Chart.js (201KB) blocks page rendering

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- trading.html:799 loads Chart.js synchronously after all HTML. live-trading.html:252 loads it before the inline script that populates content.

**Prosecutor's Argument**: On live-trading.html, Chart.js download blocks all dynamic content population.
**Defender's Argument**: Script tag is after HTML content on trading.html; impact is under 100ms on normal connections; CDN caching handles repeats.
**My Independent Observation**: On trading.html, the script is at line 799 AFTER all static HTML -- minimal impact. On live-trading.html, the script is at line 252 but all static HTML structure (tables, headings, canvas) is already in the DOM above it. Only the dynamic data population (via `render()`) is delayed. On any reasonable connection, this is imperceptible.

**My Assessment**:
The Prosecutor correctly identifies the pattern, but the real-world impact for a personal portfolio site is negligible. Using `defer` or `async` would be a minor optimization but adds complexity (need to ensure render() runs after Chart.js loads). Not worth the effort for this site.

**Ruling Rationale**:
Litmus test: "Would you file a ticket for this?" No. This is an optimization that provides minimal benefit for this site.

---

## VERDICT: FINDING-12 -- Google Fonts render-blocking in head

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- `head/custom.html` line 3 loads Google Fonts with `display=swap`. Preconnect hints on lines 1-2.

**Prosecutor's Argument**: Google Fonts CSS is render-blocking; delays First Contentful Paint.
**Defender's Argument**: `display=swap` prevents blank page (shows fallback fonts immediately); `preconnect` reduces latency; this is standard Google Fonts practice.
**My Independent Observation**: The `display=swap` parameter means the browser renders text immediately with fallback fonts and swaps in custom fonts when loaded. This is the recommended approach per Google's documentation. Users see content immediately, possibly with a brief font swap.

**My Assessment**:
The Defender is right. `display=swap` plus `preconnect` is the recommended pattern. The Prosecutor conflates "render-blocking CSS" (true technically) with "users see a blank page" (false due to `display=swap`). The actual user impact is a brief FOUT, which is standard and expected.

**Ruling Rationale**:
Litmus test: "Would you file a ticket for this?" No. This is the standard, recommended approach.

---

## VERDICT: FINDING-13 -- Duplicate Chart.js load without prefetch

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- both pages load Chart.js independently. CDN returns immutable cache headers.

**Prosecutor's Argument**: No prefetch/preload for Chart.js on non-trading pages; version drift risk between two files.
**Defender's Argument**: Browser caching handles repeat loads; CDN returns `max-age=31536000, immutable`; standard static site pattern.
**My Independent Observation**: Two independent pages each declaring their own dependency is normal for static sites. Browser caching means the second page load is instant. Adding a prefetch on non-trading pages would load 201KB on pages that do not need it.

**My Assessment**:
The Defender is right. This is not a real issue. Browser caching works. Adding a prefetch would waste bandwidth on most page views.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" No. Standard pattern.

---

## VERDICT: FINDING-14 -- Google Fonts loaded without SRI

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- Google Fonts CSS link at head/custom.html:3 has no `integrity` attribute.

**Prosecutor's Argument**: External stylesheet without SRI; theoretical supply chain risk.
**Defender's Argument**: SRI is impractical for Google Fonts since CSS is dynamically generated per User-Agent. Both sides agree on LOW.
**My Independent Observation**: SRI cannot work with Google Fonts because the CSS content varies by browser. This is a known limitation, not an actionable finding.

**My Assessment**:
Both sides agree. No action possible.

**Ruling Rationale**:
Not actionable. SRI is incompatible with Google Fonts' dynamic CSS generation.

---

## VERDICT: FINDING-15 -- No Content Security Policy headers

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- no CSP anywhere in the codebase. GitHub Pages does not support custom HTTP headers.

**Prosecutor's Argument**: No defense-in-depth against XSS.
**Defender's Argument**: GitHub Pages does not support custom HTTP headers; meta CSP has limitations; platform constraint, not site-specific.
**My Independent Observation**: GitHub Pages is the platform. Adding a meta CSP would require `unsafe-inline` for the inline scripts/styles that are standard for this theme, which would largely negate the protection.

**My Assessment**:
Platform constraint. Not actionable in a meaningful way.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Only as awareness. No practical fix for GitHub Pages.

---

## VERDICT: FINDING-16 -- Resume PDF and photo in working directory

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- `.gitignore` lines 8-9 exclude `*.pdf` and `1696906260300.jpg`. Not in git, not deployed.

**Prosecutor's Argument**: Personal files could be exposed during local development.
**Defender's Argument**: Not in version control, not deployed. Only theoretical local dev exposure.
**My Independent Observation**: These files are gitignored and not deployed. The risk is limited to someone accessing your local Jekyll dev server, which typically binds to localhost.

**My Assessment**:
Non-issue for production. Minimal theoretical risk during local development.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Probably not. Standard gitignore practice.

---

## VERDICT: FINDING-17 -- layout: none should be layout: null in index.html

**Ruling**: FIX
**Final Severity**: LOW

**Evidence Verified**: YES -- `index.html` line 2 uses `layout: none`. Jekyll convention is `layout: null`.

**Prosecutor's Argument**: Works by accident via Jekyll's fallback behavior for missing layouts; could break in future Jekyll versions.
**Defender's Argument**: Agrees; genuine code quality issue; LOW severity.
**My Independent Observation**: `layout: none` is the string "none", not YAML null. Jekyll looks for `none.html` layout, does not find it, and falls back to no layout. This works but is incorrect. The fix is changing one word.

**My Assessment**:
Both sides agree. Trivial fix, genuine code quality issue.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Yes. One-word fix.

**Recommended Direction**: Change `layout: none` to `layout: null` in `index.html` front matter.
**Priority**: BACKLOG

---

## VERDICT: FINDING-18 -- GitHub Pages custom_404: false despite 404.md

**Ruling**: ACCEPT (DISPUTED finding resolved in Defender's favor)
**Final Severity**: N/A (not a real issue)

**Evidence Verified**: YES -- `_pages/404.md` has `permalink: /404.html`. Prosecutor's own confidence was LOW.

**Prosecutor's Argument**: GitHub Pages API reports `custom_404: false`, which may indicate the custom 404 page is not active.
**Defender's Argument**: The `custom_404` API field reflects UI configuration, not Jekyll behavior; GitHub Pages automatically serves any `404.html` at the root.

**Dispute Resolution -- My Independent Investigation**:
1. I read `_pages/404.md`: it has `permalink: /404.html` and `layout: single`. Jekyll will generate `404.html` at the site root.
2. GitHub Pages documentation confirms: "If you create a file called 404.html in the root of your repository, GitHub Pages will use it as your 404 error page." Jekyll generating `404.html` via `permalink: /404.html` satisfies this requirement.
3. The `custom_404` API field in the GitHub Pages API is a metadata flag for the UI-based 404 configuration, not for Jekyll-generated files.
4. The Prosecutor expressed LOW confidence and stated "Likely no impact."

**My Assessment**:
The Defender is correct. The `custom_404` API field does not govern Jekyll-generated 404 pages. The `404.md` file with the correct permalink will produce a working custom 404 page. This is not a bug.

**Ruling Rationale**:
Not a real issue. The Prosecutor's own LOW confidence was warranted.

---

## VERDICT: FINDING-19 -- 36KB trading page with 9 hidden detail sections in DOM

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- 9 strategy detail sections (lines 500-797) hidden via CSS, toggled by JS.

**Prosecutor's Argument**: 36KB page with 719 elements always in DOM; architecture observation.
**Defender's Argument**: Agrees; trivial for modern browsers; style/architecture observation, not a bug. Prosecutor also rated LOW.
**My Independent Observation**: 36KB of HTML is nothing for a browser. This is a standard show/hide pattern for small amounts of content.

**My Assessment**:
Both sides agree this is not a problem. Standard pattern.

**Ruling Rationale**:
Not actionable. Standard pattern within acceptable limits.

---

## VERDICT: FINDING-20 -- Unescaped ampersand in P&L table header

**Ruling**: FIX
**Final Severity**: LOW

**Evidence Verified**: YES -- line 230: `<th>P&L</th>`.

**Prosecutor's Argument**: Invalid HTML; `&` should be `&amp;`.
**Defender's Argument**: Agrees; no visible impact; standards compliance.
**My Independent Observation**: Confirmed at line 230. Trivial fix. No visual impact but fails HTML validation.

**My Assessment**:
Both sides agree. One-character fix.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" Yes.

**Recommended Direction**: Change `P&L` to `P&amp;L` on line 230 of live-trading.html.
**Priority**: BACKLOG

---

## VERDICT: FINDING-21 -- Inline scripts/styles incompatible with strict CSP

**Ruling**: ACCEPT
**Final Severity**: LOW

**Evidence Verified**: YES -- inline styles, scripts, and onclick handlers throughout both trading pages. GitHub Pages does not enforce CSP.

**Prosecutor's Argument**: Code is incompatible with strict CSP; would break if CSP is ever added.
**Defender's Argument**: GitHub Pages does not enforce CSP; inline scripts/styles are standard for GitHub Pages sites and the Minimal Mistakes theme itself.
**My Independent Observation**: This is how GitHub Pages sites work. The Minimal Mistakes theme itself uses inline elements. Refactoring to external scripts/styles for a theoretical future CSP is not practical.

**My Assessment**:
Not actionable. This is the standard architecture for GitHub Pages + Minimal Mistakes.

**Ruling Rationale**:
Litmus test: "Would you mention this in a code review?" No. Standard practice for the platform.

---

## Action Items (ordered by priority)

### Immediate (fix now)
None. No CRITICAL or HIGH issues found.

### Soon (next sprint)
1. **FINDING-3 + FINDING-4**: Add error handling around Chart.js usage on both trading pages. Wrap `new Chart()` calls in try/catch, add `.catch()` to `render()` call, and provide fallback text when charts fail to render.
2. **FINDING-5**: Add SRI hashes to Chart.js CDN script tags on both trading pages. Generate hash for Chart.js 4.4.7 and add `integrity` and `crossorigin` attributes.

### Eventually (tech debt backlog)
3. **FINDING-9**: Add cross-links between trading.html and live-trading.html.
4. **FINDING-10**: Add a comment to `navigation.yml` warning that `children` is not supported in masthead nav.
5. **FINDING-17**: Change `layout: none` to `layout: null` in index.html.
6. **FINDING-20**: Change `P&L` to `P&amp;L` in live-trading.html line 230.

### Escalations Requiring Human Decision
None.

### Investigations Needed
None.

### Dismissed Findings
- **FINDING-1**: Already fixed; historical root cause documentation.
- **FINDING-2**: Process observation for a personal site; 7-minute fix.
- **FINDING-6**: Theoretical future XSS in code that does not exist yet.
- **FINDING-7**: Gemfile.lock exclusion is standard practice for GitHub Pages.
- **FINDING-8**: Greedy navigation is intended theme behavior.
- **FINDING-11**: Synchronous script load has negligible real-world impact.
- **FINDING-12**: Google Fonts with `display=swap` is the recommended pattern.
- **FINDING-13**: Browser caching handles duplicate CDN loads.
- **FINDING-14**: SRI is incompatible with Google Fonts dynamic CSS.
- **FINDING-15**: GitHub Pages does not support custom HTTP headers; meta CSP impractical.
- **FINDING-16**: Files are gitignored and not deployed.
- **FINDING-18**: API field does not govern Jekyll-generated 404 behavior.
- **FINDING-19**: 36KB page is trivial for modern browsers.
- **FINDING-21**: Standard architecture for GitHub Pages.

### Metrics
- Total findings reviewed: 21
- Fix: 6 (Critical: 0, High: 0, Medium: 3, Low: 3)
- Accept: 15
- Escalate: 0
- Investigate: 0
- Prosecutor accuracy: 29% (6 of 21 findings survived as FIX)
- Defender accuracy: 100% (1 dispute was upheld as ACCEPT)
- Evidence accuracy: 100% (all cited code matched reality; Prosecutor self-corrected on FINDING-3 hoisting analysis)
