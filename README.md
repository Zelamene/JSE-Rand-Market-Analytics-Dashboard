# JSE & Rand Market Analytics Dashboard

A Python/Streamlit dashboard analysing JSE Top 40 constituents and USD/ZAR
behaviour: rand-hedge correlation, rolling volatility, and a 50/200-day SMA
crossover backtest against buy-and-hold, with realistic transaction costs
and next-day execution to avoid lookahead bias.

**Live demo:** [https://jse-rand-market-analytics-dashboard-3w8ntex9xejyesphdwaqtm.streamlit.app/]
**Analysis period:** 2 Jan 2019 – 14 Jul 2026 (1,879 trading days)

## Key findings

### 1. The rand-hedge effect is episodic, not constant

Full-period average of the rolling 60-day correlation with USD/ZAR returns:

| Basket | Avg correlation |
|---|---|
| Rand hedges (Naspers, Anglo) | -0.04 |
| SA Inc (Standard Bank, Shoprite, Nedbank, FirstRand) | -0.09 |

The long-run averages are near zero — but that hides the pattern that
matters. During sharp rand sell-offs the baskets diverge dramatically.
In March 2020, USD/ZAR jumped +13.7% (the rand collapsed) and:

| | March 2020 return |
|---|---|
| Shoprite | +5.7% |
| Naspers | +4.2% |
| Satrix 40 | -11.9% |
| Anglo | -16.7% |
| FirstRand | -26.6% |
| Standard Bank | -31.6% |
| Nedbank | -52.8% |

That is a ~36-point gap between Naspers (+4.2%) and Standard Bank (-31.6%)
in a single month — and 57 points against Nedbank. In quiet markets the
rand link is weak; in risk-off episodes, structural exposure (offshore
earnings vs domestic credit) drives price action. The rand hedge is a
tactical signal, not a constant portfolio tilt.

Two decompositions in that table were the most instructive:

- **Anglo is a commodity stock first, a rand hedge second.** The March
  2020 commodity crash overwhelmed its rand-hedge status — it fell 16.7%
  despite a collapsing rand.
- **"SA Inc" hides heterogeneity.** The banks — geared to domestic credit —
  were the true casualties (-26.6% to -52.8%), while Shoprite, a defensive
  food staple, actually *rose* 5.7% during the panic. Revenue currency
  alone doesn't classify a stock; cyclicality matters as much.

### 2. Backtest: 50/200 SMA crossover on the Satrix 40

| Metric | Buy & Hold | Strategy (0.3% cost per position change) |
|---|---|---|
| CAGR | 11.34% | 4.75% |
| Max drawdown | -34.42% | -21.92% |
| Trades | — | 10 |

The trade log makes the downside-protection story precise. The strategy
went long on 7 Feb 2020 — two weeks before the COVID crash began — and
the death cross printed on 10 Mar 2020, putting it flat from 11 March.
That sidestepped three of the four worst days in the sample (12, 16 and
18 March) while still catching the 9 March fall and the slide before it,
which is why it still carries a -21.9% max drawdown of its own. The cost
of the protection: re-entry only came on 7 Jul 2020, after the sharpest
part of the rebound, and an Oct–Dec 2021 whipsaw (out 11 Oct, back in
2 Dec) paid two rounds of transaction costs for nothing. The classic
trend-following trade-off, made worse by costs.

Signal dates (positions change on the next trading day):
2020-02-07 in · 2020-03-10 out · 2020-07-07 in · 2021-10-11 out ·
2021-12-02 in · 2022-06-15 out · 2022-12-13 in · 2023-08-28 out ·
2024-05-08 in · 2026-07-01 out. The model has been in cash since the
1 July 2026 death cross.

Worst 5 trading days in the sample, and whether the strategy was exposed:

| Date | Satrix 40 return | Strategy position |
|---|---|---|
| 12 Mar 2020 | -9.84% | flat |
| 16 Mar 2020 | -7.96% | flat |
| 18 Mar 2020 | -7.01% | flat |
| 09 Mar 2020 | -6.53% | long |
| 04 Apr 2025 | -4.83% | long |

### 3. Volatility snapshot (annualised 30-day rolling)

| Ticker | Volatility |
|---|---|
| Naspers | 49.6% |
| Anglo | 40.1% |
| Standard Bank | 24.7% |
| FirstRand | 21.6% |
| Satrix 40 | 18.6% |
| Nedbank | 18.6% |
| Shoprite | 15.0% |
| USD/ZAR | 10.4% |

Naspers runs at nearly 50% annualised volatility versus 18.6% for the
index — a reminder that "rand hedge" does not mean low risk. Its dual
exposure to global tech sentiment and the currency makes it the riskiest
single name in the sample.

## What I learned

- **Lookahead bias can make any backtest look brilliant.** Signals are
  executed via `signal.shift(1)` — on the next trading day's close, not
  the day the crossover printed.
- **Transaction costs matter.** 0.3% per position change (~0.6% per round
  trip: brokerage + spread + impact) is realistic for South Africa and
  materially erodes the crossover's edge.
- **Correlation is dynamic.** The rand-hedge relationship isn't always
  "on" — it emerges during acute rand moves, which is what makes it
  tactical rather than structural.
- **Data can't be trusted blindly.** Initial results showed an impossible
  -99% one-day move in the Satrix 40 — a provider glitch on 2025-04-25 —
  which corrupted every drawdown figure. I added an outlier guard that
  flags and interpolates single-day moves beyond a 50% threshold before
  any calculation runs. The 04 Apr 2025 (-4.83%) entry in the worst-days
  table is the *real* data point that survived cleaning.

## Tech stack

Python, pandas, NumPy, yfinance, Streamlit, Plotly

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
