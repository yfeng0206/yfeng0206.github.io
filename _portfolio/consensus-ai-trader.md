---
title: "ConsensusAITrader"
date: 2026-04-08
excerpt: "Mar 2026 - Present - 7 AI strategies trade independently; Mix and MixLLM trade on their consensus. 25-year backtest across 14 market regimes. MixLLM averages +39.1%, beats SPY 10/14 periods."
header:
  teaser: /assets/images/consensus-trader-teaser.svg
sidebar:
  - title: "Tech Stack"
    text: "Python, Claude Opus, yfinance, SEC EDGAR, FRED"
  - title: "Universe"
    text: "93 stocks, 15 sectors"
  - title: "Backtest"
    text: "25 years, 14 market regimes (2000-2026)"
  - title: "Status"
    text: "Active Development"
---

7 AI strategies trade independently. The flagship strategies, **Mix** and **MixLLM**, read all 7 as live sensors and trade on their consensus. Free data, 93 stocks, 25 years backtested.

[View on GitHub](https://github.com/yfeng0206/ConsensusAITrader){: .btn .btn--primary}
[Trading Dashboard](/trading/){: .btn .btn--info}

## The Core Idea

Most trading systems use one strategy. We run **7 strategies independently**, then Mix and MixLLM read all 7 as live sensors and trade on their consensus. When 4+ strategies go to cash, that's a consensus danger signal no single strategy can see.

**MixLLM** adds Claude Opus as a risk monitor -- it can only escalate defensiveness (pull the emergency brake), never reduce it. During the GFC, Opus caught credit stress signals that coded rules missed, **gaining +16.5% while SPY lost -45.1%**.

![Consensus Trading Flow](/assets/images/consensus-flow.svg)

## Key Results

| Strategy | Avg Return | vs SPY | Sharpe | Beats SPY |
|:---------|:---------:|:------:|:------:|:---------:|
| **MixLLM** | **+39.1%** | **+21.6%** | **1.186** | **10/14** |
| **Mix** | +34.9% | +17.4% | 1.020 | 10/14 |
| Adaptive | +32.6% | +15.1% | 0.833 | 12/14 |
| Momentum | +27.9% | +10.4% | 0.801 | 12/14 |
| SPY | +17.5% | -- | -- | -- |

![Strategy Returns Comparison](/assets/images/consensus-trader-teaser.svg)

## Crash Protection

MixLLM averages **+11.5% during crashes** where SPY averages -25.0%.

| Strategy | Dot-com '00 | GFC '08 | COVID '20 | 2022 Bear | Avg |
|:---------|:-----------:|:-------:|:---------:|:---------:|:---:|
| **MixLLM** | -0.6% | **+16.5%** | **+21.3%** | +8.7% | **+11.5%** |
| SPY | -33.4% | -45.1% | -3.7% | -17.9% | -25.0% |

![Crash Protection](/assets/images/consensus-crash-protection.svg)

## The 9 Strategies

| Strategy | Approach | Avg Return |
|:---------|:---------|:---------:|
| **MixLLM** | Mix + Claude Opus risk monitor (escalate-only) | +39.1% |
| **Mix** | 7 peers as live sensors, multi-asset allocation | +34.9% |
| Adaptive | Switches mode by regime | +32.6% |
| Momentum | 12-minus-1 month signal, trend following | +27.9% |
| Balanced | Regime-weighted value + momentum blend | +26.2% |
| Value | Low vol, beaten-down quality | +20.3% |
| Defensive | 3-state exposure (100%/50%/20%) | +14.2% |
| EventDriven | Trades around earnings and 8-K filings | +5.2% |
| Commodity | Oil tracker (USO/XLE), binary signal | +3.7% |

## Methodology

All results use realistic execution validated across 13 ablation experiments:
- Signals from T-1 data, execution at T's Open price
- 5bps slippage, premarket gap filter, biweekly rebalancing
- Premarket proxy validated at 0.0% delta vs real data
- All data sources are free (yfinance, SEC EDGAR, GDELT, FRED)

See the [strategy deep dives](https://github.com/yfeng0206/ConsensusAITrader/blob/main/docs/strategies/README.md), [full results](https://github.com/yfeng0206/ConsensusAITrader/blob/main/docs/RESULTS.md), and [experiments log](https://github.com/yfeng0206/ConsensusAITrader/blob/main/docs/experiments/README.md) on GitHub.
