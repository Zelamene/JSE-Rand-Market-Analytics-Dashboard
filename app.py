import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data import fetch_data, TICKERS
from analysis import compute_analytics
from backtest import backtest_sma

st.set_page_config(page_title="JSE + Rand Dashboard", layout="wide")


Forest = "#1B4332"
Green = "#2D6A4F"
MID_Green = "#52B788"
Lime = "#84CC16"
Lime_SOFT = "#B5E48C"
Grey = "#6B7280"
Grey_SOFT = "#9CA3AF"
INK = "#1F2937"
hairline = "#E3E8E3"
GRID = "#EAEFEA"

COLORWAY = [Forest, Lime, MID_Green, Grey, Green, Grey_SOFT, Lime_SOFT, "#374151"]
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', 'Source Sans Pro', sans-serif; }

    [data-testid="stAppViewContainer"] { background: #F6F8F6; }
    [data-testid="stHeader"]           { background: transparent; }

    [data-testid="stSidebar"] {
        background: #EDF2ED;
        border-right: 1px solid #DFE6DF;
    }

    h1, h2, h3 { color: #1B4332 !important; letter-spacing: -0.01em; }

    .hero { padding: 0.3rem 0 0.4rem 0; }
    .hero .eyebrow {
        color: #4D7C0F;
        font-size: 0.72rem; font-weight: 700;
        letter-spacing: 0.16em; text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .hero h1 { font-size: 2.05rem; font-weight: 800; margin: 0; color: #1B4332; }
    .hero h1 .accent { color: #65A30D; }
    .hero p  { color: #6B7280; margin: 0.45rem 0 0 0; font-size: 0.97rem; max-width: 46rem; }
    .hero .rule {
        height: 3px; width: 72px; background: #84CC16;
        border-radius: 99px; margin-top: 0.95rem;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E3E8E3;
        border-left: 4px solid #84CC16;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 1px 2px rgba(27, 67, 50, 0.06);
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {
        color: #6B7280; font-weight: 600;
    }
    [data-testid="stMetricValue"] { color: #1B4332; font-weight: 700; }

    .stTabs [data-baseweb="tab-list"] { gap: 0.25rem; border-bottom: 1px solid #DFE6DF; }
    .stTabs [data-baseweb="tab"] {
        color: #6B7280; font-weight: 600;
        padding: 0.55rem 1.1rem;
        border-radius: 10px 10px 0 0;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #1B4332; background: #EDF2ED; }
    .stTabs [aria-selected="true"]     { color: #1B4332 !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #84CC16; }
    .stTabs [data-baseweb="tab-border"]    { background-color: transparent; }

    [data-testid="stCaptionContainer"] { color: #8A9490; }
    hr { border-color: #E3E8E3; }
    </style>
    """,
    unsafe_allow_html=True,
)


def style_fig(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        colorway=COLORWAY,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, 'Source Sans Pro', sans-serif", size=13, color=Grey),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", bordercolor=hairline, font=dict(color=INK)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            title_text="",
        ),
        margin=dict(l=8, r=8, t=42, b=8),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=hairline,
        title_text="",
        tickfont=dict(color=Grey_SOFT),
    )
    fig.update_yaxes(
        gridcolor=GRID, zeroline=False, title_text="", tickfont=dict(color=Grey_SOFT)
    )
    return fig


def last_pct_change(series):
    s = series.dropna()
    return f"{s.iloc[-1] / s.iloc[-2] - 1:+.2%}" if len(s) > 1 else None


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Market-fluency demo</div>
      <h1>JSE <span class="accent">&amp;</span> Rand Dashboard</h1>
      <p>Rand hedges vs SA&nbsp;Inc - relative performance, volatility, currency
         correlation and a simple SMA crossover backtest on the Satrix&nbsp;40.</p>
      <div class="rule"></div>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Settings")
    start_date = st.date_input("Start date", value=pd.to_datetime("2019-01-01"))
    selected_stocks = st.multiselect(
        "JSE stocks to display",
        options=[k for k in TICKERS if k not in ("USDZAR", "Satrix40")],
        default=["Naspers", "StandardBank", "Anglo", "Shoprite"],
    )
    st.caption("Prices are cached per start date - change it to refetch.")


# Data pipeline
@st.cache_data
def load_all(start):
    prices = fetch_data(start=str(start))
    returns, vol, ma, corr_hedge, corr_sa = compute_analytics(prices)
    return prices, returns, vol, ma, corr_hedge, corr_sa


with st.spinner("Fetching prices…"):
    prices, returns, vol, ma, corr_hedge, corr_sa = load_all(start_date)


# KPI strip

satrix = prices["Satrix40"].dropna()
zar = prices["USDZAR"].dropna()
hedge_corr_now = corr_hedge.dropna()

k1, k2, k3, k4 = st.columns(4)
k1.metric(
    "Satrix 40 close (ZAR)",
    f"{satrix.iloc[-1]:,.2f}",
    last_pct_change(satrix),
)
k2.metric(
    "USD/ZAR",
    f"{zar.iloc[-1]:.2f}",
    last_pct_change(zar),
    delta_color="inverse",
)
k3.metric(
    "Satrix 40 · period return",
    f"{satrix.iloc[-1] / satrix.iloc[0] - 1:+.1%}",
    help="Total return since the selected start date.",
)
k4.metric(
    "Rand-hedge FX correlation (60d)",
    f"{hedge_corr_now.iloc[-1]:.2f}" if len(hedge_corr_now) else "–",
    help="Rolling 60-day correlation between the rand-hedge basket and USD/ZAR "
    "returns. Positive = these stocks tend to rise when the rand weakens.",
)

st.write("")

tab1, tab2, tab3 = st.tabs(["Price & Trends", "Volatility & Correlation", "Backtest"])

with tab1:
    st.subheader("Normalised prices")
    st.caption(
        "Each series rebased to 1.0 at the start date for a clean relative comparison."
    )
    if selected_stocks:
        norm = prices[selected_stocks].div(prices[selected_stocks].iloc[0])
        fig1 = px.line(norm)
        fig1.update_traces(line_width=2)
        st.plotly_chart(style_fig(fig1), use_container_width=True)
    else:
        st.info("Pick at least one stock in the sidebar to draw this chart.")

    st.divider()

    st.subheader("Satrix 40 - 50/200-day moving averages")
    fig_sma = go.Figure()
    fig_sma.add_trace(
        go.Scatter(
            x=ma.index,
            y=ma["Satrix40"],
            name="Satrix 40",
            line=dict(color=Forest, width=2.4),
        )
    )
    fig_sma.add_trace(
        go.Scatter(
            x=ma.index,
            y=ma["MA50"],
            name="MA50",
            line=dict(color=Lime, width=1.7),
        )
    )
    fig_sma.add_trace(
        go.Scatter(
            x=ma.index,
            y=ma["MA200"],
            name="MA200",
            line=dict(color=Grey, width=1.7, dash="dot"),
        )
    )
    st.plotly_chart(style_fig(fig_sma), use_container_width=True)
    st.caption(
        "A golden cross (MA50 above MA200) is the long signal used in the Backtest tab."
    )

# Volatility, Correlation
with tab2:
    st.subheader("30-day rolling volatility")
    st.caption("Annualised standard deviation of daily returns.")
    if selected_stocks:
        fig_vol = px.line(vol[selected_stocks])
        fig_vol.update_traces(line_width=2)
        st.plotly_chart(style_fig(fig_vol), use_container_width=True)
    else:
        st.info("Pick at least one stock in the sidebar to draw this chart.")

    st.divider()

    st.subheader("Rolling 60-day correlation with USD/ZAR returns")
    corr_df = pd.DataFrame(
        {
            "Rand Hedges (Naspers, Anglo)": corr_hedge,
            "SA Inc (Banks, Shoprite)": corr_sa,
        }
    ).dropna()
    fig_corr = go.Figure()
    fig_corr.add_trace(
        go.Scatter(
            x=corr_df.index,
            y=corr_df["Rand Hedges (Naspers, Anglo)"],
            name="Rand Hedges (Naspers, Anglo)",
            line=dict(color=MID_Green, width=2),
        )
    )
    fig_corr.add_trace(
        go.Scatter(
            x=corr_df.index,
            y=corr_df["SA Inc (Banks, Shoprite)"],
            name="SA Inc (Banks, Shoprite)",
            line=dict(color=Grey, width=2),
        )
    )
    fig_corr.add_hline(y=0, line_dash="dot", line_color=Grey_SOFT, line_width=1)
    st.plotly_chart(style_fig(fig_corr), use_container_width=True)
    st.caption(
        "Above zero = the stock rises when the rand weakens (a rand hedge). "
        "Naspers and Anglo tend to benefit from a weaker rand, while banks and "
        "Shoprite often show weaker or negative correlation."
    )

with tab3:
    st.subheader("50/200 SMA crossover backtest - Satrix 40")
    backtest_df, metrics = backtest_sma(ma)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Buy & Hold CAGR", f"{metrics['Buy & Hold']['CAGR']:.2%}")
    c2.metric(
        "Strategy CAGR",
        f"{metrics['Strategy']['CAGR']:.2%}",
        f"{metrics['Strategy']['CAGR'] - metrics['Buy & Hold']['CAGR']:+.2%} vs B&H",
    )
    c3.metric("Buy & Hold max drawdown", f"{metrics['Buy & Hold']['Max Drawdown']:.2%}")
    c4.metric("Strategy max drawdown", f"{metrics['Strategy']['Max Drawdown']:.2%}")

    st.divider()

    st.subheader("Equity curve")
    fig_eq = go.Figure()
    fig_eq.add_trace(
        go.Scatter(
            x=backtest_df.index,
            y=backtest_df["bh_equity"],
            name="Buy & Hold",
            line=dict(color=Grey_SOFT, width=1.8),
        )
    )
    fig_eq.add_trace(
        go.Scatter(
            x=backtest_df.index,
            y=backtest_df["strat_equity"],
            name="SMA Crossover",
            line=dict(color=Forest, width=2.4),
        )
    )
    st.plotly_chart(style_fig(fig_eq), use_container_width=True)
    st.caption(
        "Long when the 50-day SMA is above the 200-day; 0.3% transaction cost "
        "per trade with next-day execution."
    )
