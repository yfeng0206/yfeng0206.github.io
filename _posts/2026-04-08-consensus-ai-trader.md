---
title: "Building ConsensusAITrader: 7 AI Strategies, 25 Years of Backtesting"
date: 2026-04-08
categories:
  - research
tags:
  - trading
  - ai
  - llm
  - backtesting
toc: true
toc_sticky: true
---

A multi-strategy AI trading system where 7 coded strategies trade independently and a consensus layer (Mix/MixLLM) reads all 7 as live sensors. Backtested across 14 market regimes spanning 25 years (2000-2026) using only free data sources.

[GitHub Repo](https://github.com/yfeng0206/ConsensusAITrader){: .btn .btn--primary}

## Why Consensus

Most trading systems run one strategy. The core insight here: running 7 strategies independently creates a sensor network. When 4+ strategies go to cash, that's a consensus danger signal no single strategy can detect. Mix reads these peer signals to allocate across stocks, bonds, gold, and cash. MixLLM adds Claude Opus as a risk monitor on top -- escalate-only, never de-escalate.

![Consensus Trading Flow](/assets/images/consensus-flow.svg)

## Strategy Results (14-Period Average)

| Strategy | Avg Return | vs SPY | Sharpe | Max Drawdown | Beats SPY |
|:---------|:---------:|:------:|:------:|:------------:|:---------:|
| **MixLLM** | **+39.1%** | **+21.6%** | **1.186** | **-16.0%** | 10/14 |
| **Mix** | +34.9% | +17.4% | 1.020 | -23.6% | 10/14 |
| Adaptive | +32.6% | +15.1% | 0.833 | -41.3% | 12/14 |
| Momentum | +27.9% | +10.4% | 0.801 | -44.4% | 12/14 |
| Balanced | +26.2% | +8.7% | 0.964 | -48.2% | 11/14 |
| Value | +20.3% | +2.8% | 0.650 | -41.9% | 8/14 |
| Defensive | +14.2% | -3.3% | 0.570 | -18.1% | 6/14 |
| EventDriven | +5.2% | -12.3% | 0.529 | -23.4% | 6/14 |
| Commodity | +3.7% | -13.8% | 0.191 | -22.7% | 5/14 |
| QQQ (baseline) | +24.7% | -- | -- | -82.9% | -- |
| SPY (baseline) | +17.5% | -- | -- | -55.1% | -- |

![Strategy Returns](/assets/images/consensus-trader-teaser.svg)

## Crash Protection

The real value of consensus: MixLLM averages **+11.5% during crashes** where SPY averages -25.0%.

| Strategy | Dot-com '00 | GFC '08 | COVID '20 | 2022 Bear | Avg |
|:---------|:-----------:|:-------:|:---------:|:---------:|:---:|
| **MixLLM** | -0.6% | **+16.5%** | **+21.3%** | +8.7% | **+11.5%** |
| **Mix** | -8.1% | -12.3% | +28.3% | -10.2% | -0.6% |
| Commodity | -5.3% | +27.6% | -2.1% | +8.5% | +7.2% |
| SPY | -33.4% | -45.1% | -3.7% | -17.9% | -25.0% |
| QQQ | -77.1% | -36.5% | +13.7% | -29.1% | -32.3% |

![Crash Protection](/assets/images/consensus-crash-protection.svg)

During the GFC, Opus caught credit stress signals (HY bonds crashing, gold surging) that coded rules missed. MixLLM gained +16.5% while SPY lost -45.1%.

## How MixLLM Uses the LLM

MixLLM is deliberately conservative in how it uses the LLM. Claude Opus acts as a risk monitor that can only **escalate** defensiveness -- pull the emergency brake -- but never reduce it. This design came from testing 4 LLM variants:

| Config | How LLM is Used | Result |
|:-------|:---------------|:-------|
| **V0 (default)** | Escalate defensiveness only | **Best Sharpe** |
| V1 | Recovery detector (de-escalate only) | LLM's value is crisis detection, not recovery |
| V2 | News interpreter | Coded scoring already captures what news provides |
| V3 | Event-triggered, bidirectional | Too much noise |

The constraint that the LLM can only escalate is what makes MixLLM work. The coded rules handle the 99% of days where nothing unusual is happening. The LLM only fires during genuine crises -- and that's where it adds the most value.

## Realistic Execution

All results use a validated execution pipeline with no lookahead bias:

1. **Signals** use T-1 data (yesterday's close)
2. **Premarket check** at 9:00 AM (proxy validated at 0.3% error vs real data, 0.0% decision delta)
3. **Gap filter**: >3% overnight gap = skip, 1-3% = half size
4. **Execute** at Open price with 5bps slippage
5. **Rebalance** biweekly (1st and 15th)

Every default is backed by ablation testing:

| Setting | Default | Why | Experiment |
|:--------|:--------|:----|:-----------|
| max-positions | 10 | Concentration drives alpha | Exp 5, 10 |
| frequency | biweekly | +8% vs monthly for MixLLM | Exp 9 |
| exec-model | premarket | 0.0% delta vs real data | Exp 7, 8 |
| stickiness | 1 | Higher values hurt Mix/MixLLM | Exp 3, 11 |
| LLM model | Opus | Better in bear markets | Exp 1 |

## What We Tested and Rejected

| Feature | Result | Why Not |
|:--------|:-------|:--------|
| Chandelier Exit trailing stop | Wider stops = bigger losses when they hit | Exp 13 |
| Cooldown timer (21-day hold) | Locks positions during regime changes | Exp 13 |
| Multi-commodity (10 ETFs) | Oil-only outperformed. Nat gas too volatile | Exp 2 |
| Congressional trading (Pelosi tracker) | 20-45 day disclosure delay kills any edge | Exp 6 |
| MixLLM recovery-only (V1) | LLM value IS crisis detection | Exp 12 |
| MixLLM bidirectional (V3) | Too much noise from LLM opinions on direction | Exp 12 |

## Live Research: Adversarial Debate

The `/stock-research` skill runs a **13-turn structured debate** between Bull and Bear analysts, then 7 strategy judges score the stock independently. A Chief Strategist synthesizes all 7 verdicts. All turns logged as structured JSON.

## Data Sources (All Free)

| Source | What It Provides |
|:-------|:----------------|
| yfinance | OHLCV prices, fundamentals, earnings, VIX |
| SEC EDGAR | 10-K, 10-Q, 8-K filings + XBRL financials |
| Wikipedia | Daily world events, categorized |
| GDELT | Global news: war, sanctions, OPEC, pandemic |
| Google News RSS | Macro headlines: Fed, tariffs, economic data |
| FRED | Treasury yields, CPI, unemployment |

## Full Period Breakdown

### Historical (2000-2018)

| Strategy | Dot-com | Post DC | Housing | GFC | Post GFC | QE Bull | Pre-COVID |
|:---------|:-------:|:-------:|:-------:|:---:|:--------:|:-------:|:---------:|
| MixLLM | -0.6% | +80.9% | +76.0% | +16.5% | +90.7% | +59.5% | +96.6% |
| Mix | -8.1% | +54.0% | +67.1% | -12.3% | +53.3% | +57.4% | +126.1% |
| SPY | -33.4% | +40.9% | +29.3% | -45.1% | +84.3% | +73.1% | +32.3% |

### Recent (2019-2026)

| Strategy | 2019 | COVID | 2022 | 2023 AI | Bull-Rec | Rec-Bull | 2025-Now |
|:---------|:----:|:-----:|:----:|:-------:|:--------:|:--------:|:--------:|
| MixLLM | +21.1% | +21.3% | +8.7% | +31.0% | +20.4% | +20.8% | +4.2% |
| Mix | +27.2% | +28.3% | -10.2% | +41.2% | +8.2% | +44.4% | +11.8% |
| SPY | +33.3% | -3.7% | -17.9% | +25.5% | -10.8% | +24.2% | +12.4% |

See the [full results](https://github.com/yfeng0206/ConsensusAITrader/blob/main/docs/RESULTS.md) and [experiments](https://github.com/yfeng0206/ConsensusAITrader/blob/main/docs/experiments/README.md) on GitHub.
