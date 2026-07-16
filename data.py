import yfinance as yf
import pandas as pd
from pathlib import Path

TICKERS = {
    "USDZAR": "ZAR=X",
    "Naspers": "NPN.JO",
    "StandardBank": "SBK.JO",
    "Anglo": "AGL.JO",
    "Shoprite": "SHP.JO",
    "Satrix40": "STX40.JO",
    "Nedbank": "NED.JO",
    "FirstRand": "FSR.JO",
}

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


# Replace unusually large daily jumps with interpolated values.
def _clean_outliers(series, threshold=0.5):
    daily_ret = series.pct_change()
    bad_days = daily_ret.abs() > threshold

    if bad_days.any():
        series = series.copy()
        series[bad_days] = None
        series = series.interpolate(method="linear")

    return series


# Download prices for each asset, use cached data when possible,
# and return one clean DataFrame of closing prices.
def fetch_data(start="2019-01-01"):
    prices = {}

    for name, ticker in TICKERS.items():
        filepath = CACHE_DIR / f"{name}.csv"

        if filepath.exists():
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        else:
            df = yf.download(ticker, start=start, progress=False)

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.to_csv(filepath)

        # Flatten multi-level columns if they exist.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Use the closing price if available.
        series = df["Close"] if "Close" in df.columns else df.iloc[:, 0]

        # Make sure the result is a Series.
        if isinstance(series, pd.DataFrame):
            series = series.squeeze()

        series = pd.to_numeric(series, errors="coerce")
        series = _clean_outliers(series)
        series.name = name

        prices[name] = series

    # Combine all assets into a single DataFrame.
    combined = pd.DataFrame(prices).dropna().astype("float64")

    return combined
