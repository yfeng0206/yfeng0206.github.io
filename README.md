# yfeng0206.github.io -- Developer Reference

> This file is NOT published to the website. Jekyll on GitHub Pages auto-excludes README.md.

## Live Trading Dashboard (`_pages/live-trading.html`)

### How It Works

The live trading page is a single HTML file with inline CSS + JavaScript. It renders a full dashboard (summary cards, allocation bar, equity curve chart, positions table, trade history) from a single JSON object.

**Current state:** The JSON is hardcoded as `DUMMY_DATA` inside the `<script>` tag. All rendering is client-side -- no server, no build step.

**Data flow:**
```
JSON data (inline or fetched) --> loadData() --> render() --> DOM updates via innerHTML
                                                          --> Chart.js equity curve
```

### Code Structure

```
live-trading.html
  |
  |-- <style> (lines 8-199)         CSS for cards, tables, charts, allocation bar
  |-- HTML skeleton (lines 200-250)  Empty containers with IDs (summaryCards, allocBar, etc.)
  |-- Chart.js CDN (line 254)        Loaded with SRI hash
  |-- <script> (lines 255-534)
  |     |
  |     |-- DUMMY_DATA (lines 281-358)   The JSON schema -- this is the contract
  |     |-- loadData() (line 360)        Currently returns DUMMY_DATA. Switch this for live.
  |     |-- Helper functions             fmt$(), fmtPct(), fmtPnl(), cls()
  |     |-- render() (lines 367-523)     Async. Calls loadData(), populates all DOM elements:
  |     |     |-- Summary cards (5 cards: value, return, cash, invested, regime)
  |     |     |-- Allocation bar (stocks/bonds/gold/cash with colored segments)
  |     |     |-- Positions table (computed P&L from shares * price - shares * avg_cost)
  |     |     |-- Trade history table (BUY/SELL badges with reason text)
  |     |     |-- Equity curve (Chart.js line chart, portfolio vs SPY scaled baseline)
  |     |
  |     |-- render().catch()             Error handler shows message in summaryCards
```

### JSON Schema (the contract)

This is the shape of data that `render()` expects. When you switch to live data, your trading bot must produce this exact schema:

```json
{
  "last_updated": "2026-04-09T09:35:00-07:00",
  "strategy": "MixLLM",
  "regime": "AGGRESSIVE",
  "account": {
    "starting_capital": 100000,
    "total_value": 103842,
    "cash": 18204,
    "invested": 85638,
    "day_pnl": 487,
    "total_return_pct": 3.84,
    "total_return_usd": 3842
  },
  "allocation": {
    "stocks": 82.5,
    "cash": 17.5,
    "bonds": 0,
    "gold": 0
  },
  "positions": [
    {
      "ticker": "NVDA",
      "shares": 35,
      "avg_cost": 118.20,
      "current_price": 124.80,
      "sector": "Semis"
    }
  ],
  "trades": [
    {
      "date": "2026-04-08",
      "action": "BUY",
      "ticker": "CAT",
      "shares": 20,
      "price": 358.40,
      "reason": "Regime AGGRESSIVE, industrial strength score 82"
    }
  ],
  "equity_curve": [
    { "date": "2026-03-15", "value": 100000 },
    { "date": "2026-03-17", "value": 100180 }
  ]
}
```

**Field notes:**
- `positions[].current_price` -- P&L is computed client-side: `(shares * current_price) - (shares * avg_cost)`
- `trades[].action` -- must be `"BUY"` or `"SELL"` (controls badge color)
- `trades[].reason` -- free text, shown in gray; describes why the trade was made
- `equity_curve` -- one entry per trading day; drives the Chart.js line chart
- `allocation` -- percentages that must sum to 100; only non-zero values render in the bar

---

## How to Switch from Dummy Data to Live Data

The goal: your trading bot updates a JSON file somewhere, and the website reads it on page load. **No need to push to this repo or rebuild the site.**

### Option A: GitHub Gist (recommended -- free, no hosting, no CORS issues)

**Setup (one-time):**
```bash
# 1. Create a gist with your initial JSON
gh gist create --public -f live_portfolio.json initial_data.json
# Note the gist ID from the output URL (e.g., abc123def456)

# 2. Your raw URL will be:
# https://gist.githubusercontent.com/yfeng0206/<GIST_ID>/raw/live_portfolio.json
```

**Update from your trading bot (after each trade or daily):**
```bash
# Option 1: gh CLI
gh gist edit <GIST_ID> -f live_portfolio.json updated_data.json

# Option 2: Python (using a GitHub PAT)
import requests
requests.patch(
    f"https://api.github.com/gists/{GIST_ID}",
    headers={"Authorization": f"token {GITHUB_PAT}"},
    json={"files": {"live_portfolio.json": {"content": json.dumps(data)}}}
)

# Option 3: curl
curl -X PATCH "https://api.github.com/gists/$GIST_ID" \
  -H "Authorization: token $GITHUB_PAT" \
  -d '{"files":{"live_portfolio.json":{"content":"..."}}}'
```

**Wire it up in live-trading.html:**
Change the `loadData()` function (around line 360):
```javascript
// OLD (dummy data):
function loadData() { return Promise.resolve(DUMMY_DATA); }

// NEW (live from gist):
async function loadData() {
  try {
    const resp = await fetch('https://gist.githubusercontent.com/yfeng0206/<GIST_ID>/raw/live_portfolio.json');
    if (!resp.ok) throw new Error('Fetch failed: ' + resp.status);
    return resp.json();
  } catch (e) {
    console.warn('Live data unavailable, falling back to dummy:', e);
    return DUMMY_DATA;  // keep dummy as fallback
  }
}
```

**Pros:** Free, no hosting, CORS-friendly, gist versioned, updatable via API/CLI.
**Cons:** GitHub caches gist raw URLs for ~5 minutes. Data may be up to 5 min stale.

### Option B: Raw File in ConsensusAITrader Repo

Your trading bot commits a JSON file to the trading repo. The website reads it.

```bash
# From your trading bot, after generating the JSON:
cd /path/to/ConsensusAITrader
cp /tmp/live_portfolio.json portfolio/live_state.json
git add portfolio/live_state.json
git commit -m "Update live portfolio state"
git push
```

**Wire it up:**
```javascript
async function loadData() {
  try {
    const resp = await fetch('https://raw.githubusercontent.com/yfeng0206/ConsensusAITrader/main/portfolio/live_state.json');
    if (!resp.ok) throw new Error('Fetch failed: ' + resp.status);
    return resp.json();
  } catch (e) {
    console.warn('Live data unavailable, falling back to dummy:', e);
    return DUMMY_DATA;
  }
}
```

**Pros:** Data lives with the trading code. Natural git history of portfolio state.
**Cons:** GitHub raw caches ~5 min. Creates a commit per update (noisy git log).

### Option C: GitHub Actions (fully automated, no manual push)

Add a workflow to ConsensusAITrader that runs on a schedule, generates the JSON, and pushes to a gist.

```yaml
# .github/workflows/update-portfolio.yml
name: Update Live Portfolio
on:
  schedule:
    - cron: '30 21 * * 1-5'  # 9:30 PM UTC = 2:30 PM PST, weekdays
  workflow_dispatch:           # manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/export_live_state.py > /tmp/live_portfolio.json
      - name: Update Gist
        env:
          GH_TOKEN: ${{ secrets.GIST_PAT }}
          GIST_ID: ${{ secrets.GIST_ID }}
        run: |
          gh gist edit $GIST_ID -f live_portfolio.json /tmp/live_portfolio.json
```

**Pros:** Fully hands-off. Runs daily on schedule.
**Cons:** Need to write `export_live_state.py`. Requires GitHub Action secrets.

---

## Mapping ConsensusAITrader Output to Dashboard JSON

The trading bot (`eval/daily_loop.py`) produces these files per strategy in `runs/<run_dir>/portfolios/<strategy>/`:

| Bot Output File | Dashboard JSON Field | How to Map |
|-----------------|---------------------|------------|
| `state.json` | `account.*`, `positions[]` | `final_value` -> `total_value`, positions array directly |
| `history.json` | `equity_curve[]` | Array of `{date, total_value}` -> `{date, value}` |
| `transactions.csv` | `trades[]` | CSV columns: date, action, ticker, shares, price, total, pnl |
| `regime_history.json` | `regime` | Latest entry's regime field |
| `reasoning_log.json` | `trades[].reason` | Join on date+ticker to get reasoning text |

**Example export script (`scripts/export_live_state.py`):**
```python
import json, csv, sys
from pathlib import Path

run_dir = Path("runs/live")  # or latest run
strategy = "MixLLM"
port_dir = run_dir / "portfolios" / strategy

state = json.loads((port_dir / "state.json").read_text())
history = json.loads((port_dir / "history.json").read_text())

# Read transactions
trades = []
with open(port_dir / "transactions.csv") as f:
    for row in csv.DictReader(f):
        trades.append({
            "date": row["date"],
            "action": row["action"],
            "ticker": row["ticker"],
            "shares": int(row["shares"]),
            "price": float(row["price"]),
            "reason": row.get("reason", "")
        })

# Build dashboard JSON
output = {
    "last_updated": state.get("timestamp", ""),
    "strategy": strategy,
    "regime": state.get("regime", "UNKNOWN"),
    "account": {
        "starting_capital": 100000,
        "total_value": state["final_value"],
        "cash": state.get("cash", 0),
        "invested": state["final_value"] - state.get("cash", 0),
        "day_pnl": state.get("day_pnl", 0),
        "total_return_pct": state["total_return_pct"],
        "total_return_usd": state["final_value"] - 100000
    },
    "allocation": state.get("allocation", {"stocks": 80, "cash": 20, "bonds": 0, "gold": 0}),
    "positions": state.get("positions", []),
    "trades": trades[-20:],  # last 20 trades
    "equity_curve": [{"date": h["date"], "value": h["total_value"]} for h in history]
}

json.dump(output, sys.stdout, indent=2)
```

---

## Site Structure Quick Reference

```
_pages/
  live-trading.html   <-- The live dashboard (this doc is about this)
  about.md            <-- Bio, work experience
  portfolio-archive.md <-- Grid of all portfolio items
  publications.md     <-- Papers
  blog.md             <-- Blog post archive

_portfolio/
  consensus-ai-trader.md  <-- Backtest results, links to live trading
  ijepa-3d-oct.md         <-- I-JEPA project
  slivit-3d-oct-glaucoma.md
  ... (7 total)

_posts/
  2026-04-08-consensus-ai-trader.md  <-- Full trading blog post
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
- **Charts:** Chart.js 4.4.7 (CDN with SRI)
- **Nav caveat:** Minimal Mistakes masthead does NOT support `children` dropdowns. All nav items must be flat with a `url`.
