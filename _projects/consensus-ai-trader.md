---
title: "ConsensusAITrader"
deck: "Seven AI strategies trade independently while a consensus layer reads all seven as live sensors. Backtested across 14 market regimes spanning 25 years."
period: "Mar - Apr 2026"
order: 4
group: "Applied and engineering work"
teaser: /assets/images/consensus-trader-teaser.svg
links:
  - title: "GitHub"
    url: "https://github.com/yfeng0206/ConsensusAITrader"
  - title: "Full writeup"
    url: "/writing/consensus-ai-trader/"
facts:
  - title: "Stack"
    text: "Python, yfinance, SEC EDGAR, FRED, GDELT, Claude Opus"
  - title: "Backtest"
    text: "14 market regimes, 2000-2026, free data sources only"
  - title: "Best strategy"
    text: "MixLLM, +39.1% average return, 1.186 Sharpe"
---

A multi-strategy AI trading system where seven coded strategies trade independently and a consensus
layer reads all seven as live sensors. Backtested across 14 market regimes spanning 25 years using
only free data sources.

[View on GitHub](https://github.com/yfeng0206/ConsensusAITrader){: .btn .btn--primary}

## The core idea

Most trading systems run one strategy. Running seven independently creates a sensor network: when
four or more strategies go to cash, that is a consensus danger signal no single strategy can detect.
Mix reads these peer signals to allocate across stocks, bonds, gold, and cash. MixLLM adds an LLM as
a risk monitor on top, escalate-only, never de-escalate.

| Strategy | Avg return | vs SPY | Sharpe | Max drawdown |
|:---------|:----------:|:------:|:------:|:------------:|
| **MixLLM** | **+39.1%** | +21.6% | **1.186** | **-16.0%** |
| Mix | +34.9% | +17.4% | 1.020 | -23.6% |
| Adaptive | +32.6% | +15.1% | 0.833 | -41.3% |
| SPY (baseline) | +17.5% | -- | -- | -55.1% |

The constraint that the LLM can only escalate defensiveness is what makes MixLLM work. Coded rules
handle the 99% of days where nothing unusual happens; the LLM fires only during genuine crises, and
that is where it adds the most value. During crashes MixLLM averages +11.5% where SPY averages -25.0%.

The [full writeup](/writing/consensus-ai-trader/) covers the ablations, the four LLM configurations
tested, and the features that were rejected.
