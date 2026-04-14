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
live-trading.html (552 lines)
  |
  |-- <style> (lines 8-199)         CSS for cards, tables, charts, allocation bar
  |-- HTML skeleton (lines 200-253)  Empty containers with IDs (summaryCards, allocBar, etc.)
  |-- Chart.js CDN (line 257)        Loaded with SRI hash
  |-- <script> (lines 258-552)
  |     |
  |     |-- DUMMY_DATA (lines 284-351)   The JSON schema -- this is the contract
  |     |-- loadData() (line 361)        Currently returns DUMMY_DATA. Switch this for live.
  |     |-- Helper functions             fmt$(), fmtPct(), fmtPnl(), cls()
  |     |-- render() (lines 370-545)     Async. Calls loadData(), populates all DOM elements:
  |     |     |-- Summary cards (5 cards: value, return, cash, invested, regime)
  |     |     |-- Allocation bar (stocks/bonds/gold/cash with colored segments)
  |     |     |-- Positions table (computed P&L from shares * price - shares * avg_cost)
  |     |     |-- Trade history (shows first 20, "Show All" button reveals full archive)
  |     |     |-- Equity curve (Chart.js line chart, portfolio vs SPY scaled baseline)
  |     |
  |     |-- render().catch() (line 547)  Error handler shows message in summaryCards
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
- `trades[]` -- send ALL trades in the array. The page shows the first 20 and hides the rest behind a "Show All X Trades" button. No need to truncate server-side.
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
#!/usr/bin/env python3
"""Export live portfolio state to dashboard JSON.

Usage:
  # After running daily_loop.py in live mode:
  python export_live_state.py > /tmp/live_portfolio.json
  gh gist edit <GIST_ID> -f live_portfolio.json /tmp/live_portfolio.json

  # Or pipe directly:
  python export_live_state.py | gh gist edit <GIST_ID> -f live_portfolio.json -
"""
import json, sys
from datetime import datetime
from pathlib import Path

# --- Config ---
STRATEGY = "MixLLM"
STARTING_CAPITAL = 100000
STATE_FILE = Path("portfolio/live_state.json")  # saved by save_strategies_state()

# --- Load saved state (from save_strategies_state() in daily_loop.py) ---
# The engine writes this via:
#   state = save_strategies_state(strategies, last_date)
#   json.dump(state, open("portfolio/live_state.json", "w"))
raw = json.loads(STATE_FILE.read_text())
ss = raw["strategies"][STRATEGY]

# --- Compute values ---
# Positions have: ticker, shares, avg_cost, current_price (added by engine at save time)
positions = ss.get("positions", [])
invested = sum(p["shares"] * p.get("current_price", p["avg_cost"]) for p in positions)
cash = ss["cash"]
total_value = invested + cash
total_return_pct = round((total_value - STARTING_CAPITAL) / STARTING_CAPITAL * 100, 2)
stocks_pct = round(invested / total_value * 100, 1) if total_value > 0 else 0

# --- Compute day P&L from portfolio history ---
history = ss.get("portfolio_history", [])
day_pnl = 0
if len(history) >= 2:
    day_pnl = round(history[-1].get("total_value", total_value) - history[-2].get("total_value", total_value), 2)

# --- Build trades from transactions ---
# Engine transactions have: date, action, ticker, shares, price, total, pnl, pnl_pct, cash_after
trades = []
for t in ss.get("transactions", []):
    trades.append({
        "date": t["date"],
        "action": t["action"],
        "ticker": t["ticker"],
        "shares": int(t["shares"]),
        "price": float(t["price"]),
        "reason": t.get("reason", t.get("notes", ""))
    })

# --- Build output ---
output = {
    "last_updated": datetime.now().isoformat(),
    "strategy": STRATEGY,
    "regime": ss.get("detected_regime", ss.get("_last_regime", "UNKNOWN")),
    "account": {
        "starting_capital": STARTING_CAPITAL,
        "total_value": round(total_value, 2),
        "cash": round(cash, 2),
        "invested": round(invested, 2),
        "day_pnl": day_pnl,
        "total_return_pct": total_return_pct,
        "total_return_usd": round(total_value - STARTING_CAPITAL, 2)
    },
    "allocation": {
        "stocks": stocks_pct,
        "cash": round(100 - stocks_pct, 1),
        "bonds": 0,
        "gold": 0
    },
    "positions": positions,
    "trades": trades,  # send ALL trades; frontend shows first 20 with "Show All" button
    "equity_curve": [{"date": h["date"], "value": h.get("total_value", 0)} for h in history]
}

json.dump(output, sys.stdout, indent=2)
```

### What's needed in ConsensusAITrader repo to connect

The engine (`eval/daily_loop.py`) already has `save_strategies_state()` and `live_mode=True`
but these are NOT exposed via CLI yet. To go live:

1. **Add CLI flag** to `daily_loop.py`:
   ```python
   parser.add_argument("--live-mode", action="store_true")
   parser.add_argument("--resume-from", type=str, help="Path to saved state JSON")
   ```

2. **Save state after each run** in `daily_loop.py main()`:
   ```python
   if args.live_mode:
       state = save_strategies_state(strategies, end_date)
       Path("portfolio/live_state.json").write_text(json.dumps(state, indent=2))
   ```

3. **Add `current_price` to positions at save time** (currently positions only have
   `ticker`, `shares`, `avg_cost` -- the export script needs `current_price` too):
   ```python
   # In save_strategies_state(), after building positions:
   for p in ss["positions"]:
       p["current_price"] = latest_prices.get(p["ticker"], p["avg_cost"])
   ```

4. **Add the export script** as `scripts/export_live_state.py` (the script above)

5. **Daily workflow:**
   ```bash
   # Evening after market close:
   cd ConsensusAITrader
   python eval/daily_loop.py --live-mode --resume-from portfolio/live_state.json \
     --period custom --start 2026-04-01 --end today
   
   # Export and push to gist:
   python scripts/export_live_state.py > /tmp/live_portfolio.json
   gh gist edit <GIST_ID> -f live_portfolio.json /tmp/live_portfolio.json
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
