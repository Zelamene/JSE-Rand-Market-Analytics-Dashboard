import pandas as pd
import numpy as np


def backtest_sma(ma_df, cost=0.003):
    """
    ma_df: DataFrame with columns Satrix40, MA50, MA200 (from analysis).
    Returns: equity curves DataFrame, and a dict of metrics.
    """
    df = ma_df.dropna().copy()

    # Create buy/sell signals based on the moving average crossover
    df["signal"] = (df["MA50"] > df["MA200"]).astype(int)
    df["position"] = df["signal"].shift(1)  # enter the trade on the next trading day
    df["trade"] = df["signal"].diff().fillna(0)  # marks when a position changes

    # Calculate the ETF's daily returns
    df["ret"] = df["Satrix40"].pct_change()

    # Apply returns only while invested and subtract trading costs when positions change
    df["strat_ret_gross"] = df["position"] * df["ret"]
    df["cost"] = df["trade"].abs() * cost
    df["strat_ret_net"] = df["strat_ret_gross"] - df["cost"]

    # Grow both portfolios from an initial value of 1
    df["bh_equity"] = (1 + df["ret"]).cumprod()
    df["strat_equity"] = (1 + df["strat_ret_net"]).cumprod()

    # Work out annualised returns for each approach
    years = len(df) / 252
    cagr_bh = df["bh_equity"].iloc[-1] ** (1 / years) - 1
    cagr_strat = df["strat_equity"].iloc[-1] ** (1 / years) - 1

    # Find the largest peak-to-trough decline for each portfolio
    rolling_max_bh = df["bh_equity"].cummax()
    drawdown_bh = df["bh_equity"] / rolling_max_bh - 1
    max_dd_bh = drawdown_bh.min()

    rolling_max_strat = df["strat_equity"].cummax()
    drawdown_strat = df["strat_equity"] / rolling_max_strat - 1
    max_dd_strat = drawdown_strat.min()

    metrics = {
        "Buy & Hold": {"CAGR": cagr_bh, "Max Drawdown": max_dd_bh},
        "Strategy": {"CAGR": cagr_strat, "Max Drawdown": max_dd_strat},
    }

    return df, metrics
