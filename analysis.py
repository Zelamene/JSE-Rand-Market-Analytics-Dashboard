import pandas as pd
import numpy as np


def compute_analytics(prices):
    """prices: DataFrame with all tickers (including USDZAR and Satrix40)."""
    returns = prices.pct_change().dropna()

    # Measure how much prices have been moving over the past month
    vol = returns.rolling(30).std() * np.sqrt(252)

    # Build the moving averages used for the trading strategy
    ma = pd.DataFrame(index=prices.index)
    ma["Satrix40"] = prices["Satrix40"]
    ma["MA50"] = prices["Satrix40"].rolling(50).mean()
    ma["MA200"] = prices["Satrix40"].rolling(200).mean()

    # Split stocks into rand hedges and SA-focused companies
    zar_ret = returns["USDZAR"]
    rand_hedges = ["Naspers", "Anglo"]
    sa_inc = ["StandardBank", "Shoprite", "Nedbank", "FirstRand"]

    # Track how each group moves with the rand over a rolling 60-day window
    corr_hedge_all = returns[rand_hedges].rolling(60).corr(zar_ret)
    corr_sa_all = returns[sa_inc].rolling(60).corr(zar_ret)

    # Average the correlations so it's easier to compare the two groups
    corr_hedge_avg = corr_hedge_all.groupby(level=0).mean().mean(axis=1)
    corr_sa_avg = corr_sa_all.groupby(level=0).mean().mean(axis=1)

    return returns, vol, ma, corr_hedge_avg, corr_sa_avg
