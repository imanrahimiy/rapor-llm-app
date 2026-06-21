
import os
import json
import requests
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.optimize import minimize
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# RAPOR-LLM public deployment build
# ============================================================

st.set_page_config(
    page_title="RAPOR-LLM | Adaptive ETF Portfolio Copilot",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 4rem;
    max-width: 1500px;
}
.card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 16px 18px;
    margin: 10px 0 16px 0;
    box-shadow: 0 2px 12px rgba(15, 23, 42, 0.06);
}
.card-blue {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-left: 6px solid #2563eb;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 10px 0 16px 0;
}
.card-green {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 6px solid #22c55e;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 10px 0 16px 0;
}
.card-orange {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-left: 6px solid #f97316;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 10px 0 16px 0;
}
.small-note {font-size: 0.88rem; color: #475569;}
.kpi-title {font-size:0.82rem; color:#64748b; margin-bottom:4px;}
.kpi-value {font-size:1.55rem; font-weight:700; color:#0f172a;}
hr.soft {border:0; border-top:1px solid #e5e7eb; margin:18px 0;}

.hero-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 45%, #312e81 100%);
    color: white;
    border-radius: 24px;
    padding: 26px 30px;
    margin: 12px 0 22px 0;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.22);
}
.hero-box h1 {margin:0; font-size:2.25rem;}
.hero-box p {margin:8px 0 0 0; font-size:1.02rem; opacity:0.92;}


.app-subtitle {
    color: #475569;
    font-size: 1.02rem;
    margin-top: -0.3rem;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 6px 20px rgba(15,23,42,0.06);
}
.section-title {
    font-weight: 750;
    color: #0f172a;
    margin-top: 0.8rem;
}
div[data-testid="stTabs"] button p {
    font-weight: 650;
}
.stButton > button {
    border-radius: 12px;
    font-weight: 650;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

</style>
""",
    unsafe_allow_html=True,
)

st.markdown("""
# RAPOR-LLM
### AI-Powered ETF Portfolio Optimizer and Financial Copilot

**Build resilient ETF portfolios · Stress-test market scenarios · Compare strategies · Review practical trade plans**
""")

st.caption(
    "RAPOR-LLM helps you explore diversified ETF allocations using historical market data, scenario stress tests, trading constraints, benchmark comparisons, and AI-assisted portfolio explanations. Outputs are decision-support estimates, not personal financial advice or predictions of future returns."
)

# ============================================================
# Asset universe
# ============================================================

ASSETS = pd.DataFrame([
    ["VAS.AX", "Australia Equity", "Equity Australia", "Australia", False, True],
    ["A200.AX", "Australia Equity", "Equity Australia", "Australia", False, False],
    ["IOZ.AX", "Australia Equity", "Equity Australia", "Australia", False, False],
    ["STW.AX", "Australia Equity", "Equity Australia", "Australia", False, False],
    ["MVW.AX", "Australia Equal Weight", "Equity Australia", "Australia", False, False],
    ["EX20.AX", "Australia ex Top 20", "Equity Australia", "Australia", False, False],
    ["VGS.AX", "Global Equity", "Equity Global", "Global Developed", False, True],
    ["IWLD.AX", "Global Equity", "Equity Global", "Global Developed", False, False],
    ["WXOZ.AX", "Global ex Australia", "Equity Global", "Global Developed", False, False],
    ["QUAL.AX", "Global Quality", "Equity Quality", "Global Developed", False, False],
    ["MOAT.AX", "Global Moat", "Equity Quality", "Global Developed", False, False],
    ["IVV.AX", "US S&P 500", "Equity US", "United States", False, True],
    ["NDQ.AX", "Nasdaq / Technology", "Technology", "United States", False, False],
    ["TECH.AX", "Global Technology", "Technology", "Global", False, False],
    ["FANG.AX", "Mega-cap Tech", "Technology", "United States", False, False],
    ["HACK.AX", "Cybersecurity", "Technology", "Global", False, False],
    ["ROBO.AX", "Robotics / Automation", "Technology", "Global", False, False],
    ["RBTZ.AX", "Robotics / AI", "Technology", "Global", False, False],
    ["VGE.AX", "Emerging Markets", "Emerging Markets", "Emerging Markets", False, False],
    ["IEM.AX", "Emerging Markets", "Emerging Markets", "Emerging Markets", False, False],
    ["IAA.AX", "Asia ex Japan", "Asia Equity", "Asia", False, False],
    ["IZZ.AX", "China Equity", "China Equity", "China", False, False],
    ["ESTX.AX", "Europe Equity", "Europe Equity", "Europe", False, False],
    ["VEQ.AX", "Europe Equity", "Europe Equity", "Europe", False, False],
    ["VAF.AX", "Australian Bonds", "Bonds", "Australia", True, True],
    ["VBND.AX", "Global Bonds", "Bonds", "Global", True, True],
    ["IAF.AX", "Australian Bonds", "Bonds", "Australia", True, False],
    ["BOND.AX", "Australian Bonds", "Bonds", "Australia", True, False],
    ["AGVT.AX", "Australian Government Bonds", "Government Bonds", "Australia", True, False],
    ["VGB.AX", "Australian Government Bonds", "Government Bonds", "Australia", True, False],
    ["IHCB.AX", "Corporate Bonds", "Corporate Bonds", "Global", True, False],
    ["HBRD.AX", "Hybrid Income", "Hybrid Income", "Australia", True, False],
    ["AAA.AX", "Cash / Money Market", "Cash", "Australia", True, False],
    ["BILL.AX", "Cash / Bills", "Cash", "Australia", True, False],
    ["QPON.AX", "Floating Rate Notes", "Floating Rate", "Australia", True, False],
    ["GOLD.AX", "Gold", "Gold", "Global", True, True],
    ["PMGOLD.AX", "Gold", "Gold", "Global", True, False],
    ["QAU.AX", "Gold Hedged", "Gold", "Global", True, False],
    ["FUEL.AX", "Global Energy", "Energy", "Global", False, True],
    ["OOO.AX", "Oil", "Energy", "Global", False, False],
    ["QRE.AX", "Australian Resources", "Resources", "Australia", False, False],
    ["MVR.AX", "Australian Resources", "Resources", "Australia", False, False],
    ["MNRS.AX", "Gold Miners", "Gold Miners", "Global", False, False],
    ["VAP.AX", "Property / REIT", "Property", "Australia", False, True],
    ["SLF.AX", "Property / REIT", "Property", "Australia", False, False],
    ["DJRE.AX", "Global REIT", "Property", "Global", False, False],
    ["VBLD.AX", "Global Infrastructure", "Infrastructure", "Global", False, False],
    ["IFRA.AX", "Infrastructure", "Infrastructure", "Global", False, False],
    ["DRUG.AX", "Healthcare", "Healthcare", "Global", False, False],
    ["IXJ.AX", "Healthcare", "Healthcare", "Global", False, False],
    ["BANK.AX", "Banks", "Banks", "Australia", False, False],
    ["MVB.AX", "Banks", "Banks", "Australia", False, False],
    ["FOOD.AX", "Food / Staples", "Consumer Staples", "Global", False, False],
    ["FAIR.AX", "Australian Sustainability", "Sustainable Equity", "Australia", False, False],
    ["ETHI.AX", "Global Sustainability", "Sustainable Equity", "Global", False, False],
    ["VHY.AX", "High Dividend", "Dividend Equity", "Australia", False, False],
    ["IHD.AX", "High Dividend", "Dividend Equity", "Australia", False, False],
    ["SYI.AX", "High Dividend", "Dividend Equity", "Australia", False, False],
    ["MVOL.AX", "Minimum Volatility", "Low Volatility", "Australia", False, False],
    ["AUMF.AX", "Multifactor", "Factor Equity", "Australia", False, False],
    ["SPY", "US S&P 500", "US-listed Equity", "United States", False, False],
    ["VOO", "US S&P 500", "US-listed Equity", "United States", False, False],
    ["QQQ", "Nasdaq 100", "US-listed Technology", "United States", False, False],
    ["TLT", "US Long Treasury", "US Treasury Bonds", "United States", True, False],
    ["IEF", "US Intermediate Treasury", "US Treasury Bonds", "United States", True, False],
    ["GLD", "Gold", "US-listed Gold", "Global", True, False],
    ["USO", "Oil", "US-listed Energy", "United States", False, False],
], columns=["Ticker", "Class", "Group", "Region", "Defensive", "Include"])

# ============================================================
# Helpers
# ============================================================

@st.cache_data(show_spinner=True)
def get_prices(tickers, start):
    if not tickers:
        return pd.DataFrame()
    data = yf.download(tickers, start=start, auto_adjust=True, progress=False)
    if data.empty:
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        if "Close" not in data.columns.get_level_values(0):
            return pd.DataFrame()
        close = data["Close"]
    else:
        close = data[["Close"]]
        close.columns = tickers[:1]
    close = close.dropna(how="all").ffill().dropna().dropna(axis=1, how="all")
    return close

def ann_ret(r):
    """
    Geometric annualised return from daily simple returns.
    Works for both a Series and a DataFrame.
    """
    if len(r) == 0:
        return pd.Series(dtype=float)
    return (1 + r).prod() ** (252 / max(len(r), 1)) - 1

def ann_vol(r):
    if len(r) == 0:
        return pd.Series(dtype=float)
    return r.std() * np.sqrt(252)

def cvar(x, alpha=.95):
    losses = -pd.Series(x).dropna()
    if len(losses) == 0:
        return 0.0
    q = np.quantile(losses, alpha)
    tail = losses[losses >= q]
    return float(tail.mean()) if len(tail) else float(q)

def max_drawdown(x):
    r = pd.Series(x).dropna()
    if len(r) == 0:
        return 0.0
    wealth = (1 + r).cumprod()
    dd = wealth / wealth.cummax() - 1
    return float(abs(dd.min()))

def norm(w):
    w = np.clip(np.array(w, dtype=float), 0, None)
    if len(w) == 0:
        return w
    if w.sum() <= 0:
        return np.ones(len(w)) / len(w)
    return w / w.sum()

def risk_contribution(weights, cov):
    weights = np.array(weights, dtype=float)
    port_var = float(weights @ cov @ weights)
    if port_var <= 0:
        return np.ones(len(weights)) / len(weights)
    marginal = cov @ weights
    rc = weights * marginal / port_var
    return rc

def scenario_template(tickers, scenario_name):
    base = {t: 0.0 for t in tickers}
    templates = {
        "Middle East energy shock": {
            "FUEL.AX": .25, "OOO.AX": .30, "QRE.AX": .12,
            "GOLD.AX": .14, "PMGOLD.AX": .14, "QAU.AX": .12,
            "VAS.AX": -.10, "A200.AX": -.10, "IOZ.AX": -.10,
            "VGS.AX": -.12, "IWLD.AX": -.12, "IVV.AX": -.12,
            "NDQ.AX": -.18, "TECH.AX": -.18, "HACK.AX": -.15,
            "VAF.AX": .02, "VBND.AX": .03, "IAF.AX": .02, "AAA.AX": .01,
            "VAP.AX": -.10, "SLF.AX": -.10,
        },
        "Global recession": {
            "VAS.AX": -.22, "A200.AX": -.22, "IOZ.AX": -.22,
            "VGS.AX": -.28, "IWLD.AX": -.28, "IVV.AX": -.28,
            "NDQ.AX": -.38, "TECH.AX": -.38, "HACK.AX": -.32,
            "VGE.AX": -.34, "IEM.AX": -.34,
            "VAP.AX": -.28, "SLF.AX": -.28,
            "FUEL.AX": -.12, "OOO.AX": -.12,
            "GOLD.AX": .10, "PMGOLD.AX": .10, "QAU.AX": .08,
            "VAF.AX": .07, "VBND.AX": .06, "IAF.AX": .07, "AAA.AX": .01,
        },
        "High inflation": {
            "GOLD.AX": .16, "PMGOLD.AX": .16, "QAU.AX": .13,
            "FUEL.AX": .20, "OOO.AX": .25, "QRE.AX": .15,
            "VAF.AX": -.12, "VBND.AX": -.10, "IAF.AX": -.12,
            "VAS.AX": -.06, "A200.AX": -.06, "IOZ.AX": -.06,
            "VGS.AX": -.07, "IWLD.AX": -.07, "IVV.AX": -.07,
            "NDQ.AX": -.12, "TECH.AX": -.12,
            "VAP.AX": -.12, "SLF.AX": -.12,
        },
        "Technology selloff": {
            "NDQ.AX": -.35, "TECH.AX": -.35, "HACK.AX": -.30,
            "VGS.AX": -.14, "IWLD.AX": -.14, "IVV.AX": -.18,
            "VAS.AX": -.06, "A200.AX": -.06, "IOZ.AX": -.06,
            "GOLD.AX": .07, "PMGOLD.AX": .07,
            "VAF.AX": .04, "VBND.AX": .04, "IAF.AX": .04, "AAA.AX": .01,
        },
        "Strong bull market": {
            "VAS.AX": .16, "A200.AX": .16, "IOZ.AX": .16,
            "VGS.AX": .20, "IWLD.AX": .20, "IVV.AX": .22,
            "NDQ.AX": .28, "TECH.AX": .28, "HACK.AX": .25,
            "VGE.AX": .20, "IEM.AX": .20,
            "VAP.AX": .14, "SLF.AX": .14,
            "FUEL.AX": .10, "OOO.AX": .12,
            "GOLD.AX": -.03, "PMGOLD.AX": -.03,
            "VAF.AX": .01, "VBND.AX": .01, "AAA.AX": .005,
        },
        "Neutral / no stress": {t: 0.002 for t in tickers},
    }
    base.update(templates.get(scenario_name, {}))
    return np.array([base.get(t, 0.0) for t in tickers], dtype=float)

def scenario_group_overrides(scenario_name):
    """
    Scenario-specific guardrail shifts. This makes scenario changes visible in the optimiser,
    not only in the report.
    """
    if scenario_name == "High inflation":
        return {
            "Gold": (.12, .30),
            "Energy": (.06, .20),
            "Bonds": (.12, .38),
            "Property": (.03, .12),
        }
    if scenario_name == "Middle East energy shock":
        return {
            "Gold": (.12, .30),
            "Energy": (.07, .22),
            "Bonds": (.16, .42),
        }
    if scenario_name == "Global recession":
        return {
            "Gold": (.10, .28),
            "Bonds": (.28, .55),
            "Energy": (.02, .12),
            "Property": (.02, .10),
        }
    if scenario_name == "Technology selloff":
        return {
            "Gold": (.10, .28),
            "Bonds": (.25, .50),
            "Technology": (0.00, .10),
            "US-listed Technology": (0.00, .10),
            "Equity US": (.03, .16),
            "US-listed Equity": (.03, .16),
        }
    if scenario_name == "Strong bull market":
        return {
            "Gold": (.03, .18),
            "Bonds": (.12, .35),
            "Equity Global": (.08, .30),
            "US-listed Equity": (.06, .30),
            "Equity US": (.06, .25),
            "Technology": (.03, .25),
        }
    return {}

def build_group_bounds(base_bounds, scenario_name, scenario_guardrail_strength):
    bounds = dict(base_bounds)
    overrides = scenario_group_overrides(scenario_name)
    if scenario_guardrail_strength <= 0:
        return bounds

    for g, (lo_new, hi_new) in overrides.items():
        if g in bounds:
            lo_old, hi_old = bounds[g]
            lo = (1 - scenario_guardrail_strength) * lo_old + scenario_guardrail_strength * lo_new
            hi = (1 - scenario_guardrail_strength) * hi_old + scenario_guardrail_strength * hi_new
            bounds[g] = (lo, hi)
        else:
            bounds[g] = (lo_new, hi_new)
    return bounds

def build_live_input(valid, latest, existing=None):
    old = {}
    if isinstance(existing, pd.DataFrame) and "Ticker" in existing.columns:
        for _, row in existing.iterrows():
            old[str(row["Ticker"])] = float(row.get("Manual Market Move %", 0.0))
    return pd.DataFrame({
        "Ticker": valid,
        "Latest Price": latest,
        "Manual Market Move %": [old.get(t, 0.0) for t in valid],
    })

def add_adjusted_prices(live_df):
    df = live_df.copy()
    df["Manual Market Move %"] = pd.to_numeric(df["Manual Market Move %"], errors="coerce").fillna(0.0)
    df["Manual Market Move"] = df["Manual Market Move %"] / 100.0
    df["Adjusted Price"] = df["Latest Price"] * (1 + df["Manual Market Move"])
    return df

def combine_shocks(base_scenario, live_moves, scenario_importance, live_importance):
    return scenario_importance * np.array(base_scenario, dtype=float) + live_importance * np.array(live_moves, dtype=float)

def scenario_matrix_library(tickers, live_moves=None, scenario_importance=1.0, live_importance=1.0):
    """
    Build a scenario matrix for robust and comparative model analysis.
    Rows = scenarios, columns = ETFs.
    """
    names = [
        "Middle East energy shock",
        "Global recession",
        "High inflation",
        "Technology selloff",
        "Strong bull market",
        "Neutral / no stress",
    ]
    live_moves = np.zeros(len(tickers)) if live_moves is None else np.array(live_moves, dtype=float)
    rows = []
    for name in names:
        base = scenario_template(tickers, name)
        rows.append(combine_shocks(base, live_moves, scenario_importance, live_importance))
    return np.vstack(rows), names

def validate_weights(weights, group_bounds, groups):
    """
    Feasibility checks for optimiser outputs.
    """
    w = np.array(weights, dtype=float)
    checks = []
    checks.append({"Check": "Weights sum to 1", "Value": float(w.sum()), "Pass": abs(w.sum() - 1.0) < 1e-5})
    checks.append({"Check": "No negative weights", "Value": float(w.min()), "Pass": w.min() >= -1e-7})
    checks.append({"Check": "No NaN weights", "Value": int(np.isnan(w).sum()), "Pass": int(np.isnan(w).sum()) == 0})

    for group_name, (lo, hi) in group_bounds.items():
        idx = [i for i, g in enumerate(groups) if g == group_name]
        if not idx:
            continue
        group_weight = float(w[idx].sum())
        if lo is not None:
            checks.append({"Check": f"{group_name} >= lower guardrail", "Value": group_weight, "Pass": group_weight + 1e-6 >= lo})
        if hi is not None:
            checks.append({"Check": f"{group_name} <= upper guardrail", "Value": group_weight, "Pass": group_weight - 1e-6 <= hi})
    return pd.DataFrame(checks)

def optimisation_formula_description(model_type):
    descriptions = {
        "capital_protection": "Conservative weighted objective: low volatility, low CVaR, low drawdown, low concentration, and low scenario loss receive the highest priority.",
        "crisis_resilience": "Tail-risk objective: heavily penalises CVaR, drawdown, and scenario loss to improve behaviour in adverse markets.",
        "balanced_resilience": "Balanced multi-objective formulation: trades off return, volatility, CVaR, drawdown, concentration, scenario loss, turnover, and tax drag.",
        "growth_guardrails": "Growth-biased formulation: rewards expected return more strongly but retains volatility, CVaR, drawdown, and scenario-loss guardrails.",
        "broad_diversification": "Diversification-first formulation: applies a strong concentration penalty to avoid dominant positions.",
        "risk_parity": "Risk parity formulation: penalises unequal risk contributions so assets contribute more evenly to total portfolio risk.",
        "scenario_aware": "Selected-scenario formulation: directly rewards positive selected-scenario performance and heavily penalises selected-scenario loss.",
        "minimum_volatility": "Minimum-volatility formulation: minimises portfolio volatility subject to practical and asset-class guardrails.",
        "downside_cvar": "Downside-risk formulation: focuses on CVaR and drawdown rather than ordinary volatility.",
        "max_sharpe_guardrails": "Return-per-risk formulation: approximates maximum Sharpe while retaining downside and concentration guardrails.",
        "worst_case_robust": "Worst-case robust formulation: penalises the worst portfolio loss across the full scenario library.",
    }
    return descriptions.get(model_type, "Custom weighted multi-objective formulation.")

def asset_diagnostics(returns, allocation, weights, cov):
    tickers = list(allocation["Ticker"])
    mean_ret = ann_ret(returns[tickers]).reindex(tickers).fillna(0).values
    vol = ann_vol(returns[tickers]).reindex(tickers).fillna(0).values
    rc = risk_contribution(weights, cov)
    out = allocation.copy()
    out["Asset Expected Return"] = mean_ret
    out["Asset Volatility"] = vol
    out["Risk Contribution"] = rc
    out["Return Contribution"] = out["Target Weight"].values * mean_ret
    return out

def make_gauge(title, value, suffix="/100"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(value),
        number={"suffix": suffix},
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"thickness": 0.28},
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fef3c7"},
                {"range": [70, 100], "color": "#dcfce7"},
            ],
        },
    ))
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=45, b=10))
    return fig

def make_drawdown_series(port_ret):
    wealth = (1 + port_ret).cumprod()
    return wealth / wealth.cummax() - 1


def _normalise_series(series, higher_is_better=True):
    """
    Convert a metric into a 0-100 relative score across feasible models.
    This prevents the comparison charts from becoming blank when absolute scores are too harsh.
    """
    s = pd.to_numeric(series, errors="coerce")
    if s.notna().sum() == 0:
        return pd.Series(np.zeros(len(s)), index=s.index)

    lo = float(s.min())
    hi = float(s.max())

    if abs(hi - lo) < 1e-12:
        return pd.Series(np.ones(len(s)) * 50.0, index=s.index)

    if higher_is_better:
        out = 100 * (s - lo) / (hi - lo)
    else:
        out = 100 * (hi - s) / (hi - lo)

    return out.fillna(0).clip(0, 100)

def score_model_comparison_table(comp, selected_business_objective):
    """
    Score all feasible models relative to each other.

    Why this is better than the previous formula:
    - The previous formula used absolute penalties and could clip all scores to zero.
    - If all scores are zero, Plotly bars and scatter sizes look blank.
    - This function ranks models relatively under the same data, scenario, budget, and constraints.
    """
    comp = comp.copy()
    if comp.empty:
        comp["Strategy score"] = []
        return comp

    feasible_mask = comp.get("Feasible", True) == True
    if feasible_mask.sum() == 0:
        comp["Strategy score"] = 0.0
        return comp

    f = comp.loc[feasible_mask].copy()

    # Relative metric scores
    ret_score = _normalise_series(f["Expected annual return"], higher_is_better=True)
    vol_score = _normalise_series(f["Annual volatility"], higher_is_better=False)
    cvar_score = _normalise_series(f["Daily CVaR 95%"], higher_is_better=False)
    dd_score = _normalise_series(f["Max drawdown"], higher_is_better=False)
    selected_scen_score = _normalise_series(f["Selected scenario return"], higher_is_better=True)
    worst_scen_score = _normalise_series(f["Worst scenario return"], higher_is_better=True)
    eff_score = _normalise_series(f["Effective holdings"], higher_is_better=True)
    fee_score = _normalise_series(f["Brokerage fee ratio"], higher_is_better=False)
    zero_score = _normalise_series(f["Zero-unit ETFs"], higher_is_better=False)

    # Objective-specific business weights.
    if selected_business_objective == "Protect my capital":
        score = (
            0.05 * ret_score +
            0.18 * vol_score +
            0.20 * cvar_score +
            0.22 * dd_score +
            0.10 * selected_scen_score +
            0.10 * worst_scen_score +
            0.05 * eff_score +
            0.05 * fee_score +
            0.05 * zero_score
        )
    elif selected_business_objective == "Prepare for market shocks":
        score = (
            0.03 * ret_score +
            0.10 * vol_score +
            0.20 * cvar_score +
            0.20 * dd_score +
            0.18 * selected_scen_score +
            0.17 * worst_scen_score +
            0.04 * eff_score +
            0.04 * fee_score +
            0.04 * zero_score
        )
    elif selected_business_objective == "Grow, but keep guardrails":
        score = (
            0.32 * ret_score +
            0.12 * vol_score +
            0.12 * cvar_score +
            0.12 * dd_score +
            0.10 * selected_scen_score +
            0.06 * worst_scen_score +
            0.04 * eff_score +
            0.06 * fee_score +
            0.06 * zero_score
        )
    elif selected_business_objective == "Spread risk widely":
        score = (
            0.08 * ret_score +
            0.11 * vol_score +
            0.11 * cvar_score +
            0.10 * dd_score +
            0.08 * selected_scen_score +
            0.08 * worst_scen_score +
            0.28 * eff_score +
            0.08 * fee_score +
            0.08 * zero_score
        )
    elif selected_business_objective == "Equalise risk contribution":
        score = (
            0.06 * ret_score +
            0.14 * vol_score +
            0.14 * cvar_score +
            0.12 * dd_score +
            0.08 * selected_scen_score +
            0.08 * worst_scen_score +
            0.28 * eff_score +
            0.05 * fee_score +
            0.05 * zero_score
        )
    elif selected_business_objective == "Optimise for my selected scenario":
        score = (
            0.05 * ret_score +
            0.08 * vol_score +
            0.12 * cvar_score +
            0.12 * dd_score +
            0.36 * selected_scen_score +
            0.13 * worst_scen_score +
            0.04 * eff_score +
            0.05 * fee_score +
            0.05 * zero_score
        )
    elif selected_business_objective == "Robust across all scenarios":
        score = (
            0.04 * ret_score +
            0.10 * vol_score +
            0.16 * cvar_score +
            0.16 * dd_score +
            0.12 * selected_scen_score +
            0.28 * worst_scen_score +
            0.04 * eff_score +
            0.05 * fee_score +
            0.05 * zero_score
        )
    elif selected_business_objective == "Minimum volatility":
        score = (
            0.03 * ret_score +
            0.35 * vol_score +
            0.14 * cvar_score +
            0.14 * dd_score +
            0.08 * selected_scen_score +
            0.08 * worst_scen_score +
            0.06 * eff_score +
            0.06 * fee_score +
            0.06 * zero_score
        )
    elif selected_business_objective == "Downside protection / CVaR":
        score = (
            0.03 * ret_score +
            0.10 * vol_score +
            0.32 * cvar_score +
            0.22 * dd_score +
            0.08 * selected_scen_score +
            0.13 * worst_scen_score +
            0.04 * eff_score +
            0.04 * fee_score +
            0.04 * zero_score
        )
    elif selected_business_objective == "Maximum return per unit risk":
        score = (
            0.26 * ret_score +
            0.22 * vol_score +
            0.12 * cvar_score +
            0.12 * dd_score +
            0.08 * selected_scen_score +
            0.06 * worst_scen_score +
            0.04 * eff_score +
            0.05 * fee_score +
            0.05 * zero_score
        )
    else:
        score = (
            0.14 * ret_score +
            0.14 * vol_score +
            0.14 * cvar_score +
            0.14 * dd_score +
            0.14 * selected_scen_score +
            0.12 * worst_scen_score +
            0.08 * eff_score +
            0.05 * fee_score +
            0.05 * zero_score
        )

    # Put scores back into full table.
    comp["Strategy score"] = 0.0
    comp.loc[feasible_mask, "Strategy score"] = score.astype(float).clip(0, 100)

    # Give infeasible models a visible but very low score, not NaN.
    comp.loc[~feasible_mask, "Strategy score"] = 0.0

    return comp


def portfolio_metrics(ret, w):
    pr = pd.Series(ret.values @ w, index=ret.index)
    return {
        "Expected annual return": float(ann_ret(pr)),
        "Annual volatility": float(ann_vol(pr)),
        "Daily CVaR 95%": float(cvar(pr)),
        "Max drawdown": float(max_drawdown(pr)),
    }, pr

def compute_scores(metrics, scenario_return, effective_n, fee_ratio, zero_units_count, n_assets):
    vol = float(metrics["Annual volatility"])
    dd = float(metrics["Max drawdown"])
    cvar95 = float(metrics["Daily CVaR 95%"])

    risk_score = 100 - 350 * vol - 180 * dd - 900 * cvar95
    risk_score = float(np.clip(risk_score, 0, 100))

    resilience_score = 70 + 250 * scenario_return - 100 * max(-scenario_return, 0) - 80 * dd
    resilience_score = float(np.clip(resilience_score, 0, 100))

    diversification_score = min(effective_n / max(n_assets, 1), 1.0) * 100
    diversification_score = float(np.clip(diversification_score, 0, 100))

    execution_score = 100 - 1800 * fee_ratio - 8 * zero_units_count
    execution_score = float(np.clip(execution_score, 0, 100))

    return {
        "Risk control score": risk_score,
        "Stress-test resilience score": resilience_score,
        "Diversification score": diversification_score,
        "Trade feasibility score": execution_score,
    }


def compute_raptor_score(scores):
    """
    Public-facing composite score combining risk control, scenario resilience,
    diversification, and execution quality.
    """
    return float(np.clip(
        0.30 * scores.get("Risk control score", 0) +
        0.30 * scores.get("Stress-test resilience score", 0) +
        0.20 * scores.get("Diversification score", 0) +
        0.20 * scores.get("Trade feasibility score", 0),
        0, 100
    ))

def risk_label(volatility, drawdown):
    if volatility < 0.07 and drawdown < 0.12:
        return "Low"
    if volatility < 0.13 and drawdown < 0.22:
        return "Moderate"
    return "High"


def compute_ai_confidence_score(scores, model_comparison=None, benchmark_comparison=None, validation_report=None):
    """
    Transparent internal confidence score. This is not a forecast.
    It measures coherence across risk, resilience, execution, model agreement,
    benchmark comparison, and feasibility checks.
    """
    base = compute_raptor_score(scores)

    model_gap_bonus = 0.0
    if isinstance(model_comparison, pd.DataFrame) and len(model_comparison) >= 2 and "Strategy score" in model_comparison.columns:
        vals = model_comparison["Strategy score"].dropna().sort_values(ascending=False).values
        if len(vals) >= 2:
            model_gap_bonus = min((vals[0] - vals[1]) * 0.15, 5.0)

    benchmark_bonus = 0.0
    if isinstance(benchmark_comparison, pd.DataFrame) and len(benchmark_comparison):
        leader = str(benchmark_comparison.iloc[0].get("Portfolio", ""))
        if "Selected" in leader or "RAPOR" in leader or "RAPTOR" in leader:
            benchmark_bonus = 5.0

    validation_penalty = 0.0
    if isinstance(validation_report, pd.DataFrame) and "Pass" in validation_report.columns:
        validation_penalty = int((validation_report["Pass"] == False).sum()) * 12.0

    return float(np.clip(base + model_gap_bonus + benchmark_bonus - validation_penalty, 0, 100))

# ============================================================
# Optimisation
# ============================================================


def make_feasible_weight_bounds(n, min_weight, max_weight, no_zero):
    """
    Build numerically feasible long-only box bounds.
    If the user's max weight is too tight for the selected number of ETFs, relax it just enough to allow sum(w)=1.
    If the requested minimum weight is too high, cap it safely.
    """
    if n <= 0:
        return [], 0.0, 0.0
    min_w = min(float(min_weight), 0.95 / n) if no_zero else 0.0
    max_w = max(float(max_weight), 1.0 / n + 1e-6)
    max_w = min(max_w, 1.0)
    if min_w * n > 1.0:
        min_w = 0.0
    return [(min_w, max_w) for _ in range(n)], min_w, max_w

def optimise(ret, groups, current_w, params, group_bounds, combined_shock, scenario_matrix=None):
    n = ret.shape[1]
    mu_hist = ann_ret(ret).values
    cov = ret.cov().values * 252

    # Scenario-adjusted expected-return vector.
    # A one-off shock is not annual return. We use it as a forward-looking tilt, with capped influence.
    shock = np.array(combined_shock, dtype=float)
    scenario_matrix = np.atleast_2d(shock) if scenario_matrix is None else np.array(scenario_matrix, dtype=float)
    shock_tilt = np.clip(shock, -0.35, 0.35)
    mu_eff = (1 - params["scenario_mu_blend"]) * mu_hist + params["scenario_mu_blend"] * shock_tilt

    bounds, min_w, effective_max_w = make_feasible_weight_bounds(
        n, params["min_weight"], params["max_weight"], params["no_zero"]
    )

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    for g, (lo, hi) in group_bounds.items():
        idx = [i for i, group in enumerate(groups) if group == g]
        if not idx:
            continue
        lo_eff = None if lo is None else float(np.clip(lo, 0.0, 1.0))
        hi_eff = None if hi is None else float(np.clip(hi, 0.0, 1.0))
        if lo_eff is not None and hi_eff is not None and lo_eff > hi_eff:
            lo_eff, hi_eff = hi_eff, lo_eff
        if lo_eff is not None:
            constraints.append({"type": "ineq", "fun": lambda w, idx=idx, lo=lo_eff: np.sum(w[idx]) - lo})
        if hi_eff is not None:
            constraints.append({"type": "ineq", "fun": lambda w, idx=idx, hi=hi_eff: hi - np.sum(w[idx])})

    current_w = norm(current_w)
    tax = np.ones(n) * params["tax_drag"]
    model_type = params["model_type"]

    def parts(w):
        pr = ret.values @ w
        expected = float(w @ mu_eff)
        hist_expected = float(w @ mu_hist)
        volatility = float(np.sqrt(max(w @ cov @ w, 0)))
        tail = cvar(pr)
        dd = max_drawdown(pr)
        concentration = float(np.sum(w * w))
        turnover = float(np.sum(np.abs(w - current_w)))
        tax_drag = float(np.sum(w * tax))
        scenario_result = float(w @ shock)
        scenario_loss = max(-scenario_result, 0.0)
        scenario_results = scenario_matrix @ w
        worst_case_loss = float(max(-np.min(scenario_results), 0.0))
        rc = risk_contribution(w, cov)
        risk_parity_penalty = float(np.sum((rc - 1.0 / n) ** 2))
        return expected, hist_expected, volatility, tail, dd, concentration, turnover, tax_drag, scenario_result, scenario_loss, risk_parity_penalty, worst_case_loss

    def objective(w):
        expected, hist_expected, vol, tail, dd, conc, turnover, tax_drag, scen, scen_loss, rp, worst_loss = parts(w)

        if model_type == "capital_protection":
            return (
                -0.15 * expected
                + 2.40 * params["risk"] * vol
                + 2.10 * params["cvar"] * tail
                + 2.20 * params["drawdown"] * dd
                + 1.20 * params["concentration"] * conc
                + 1.50 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "crisis_resilience":
            return (
                -0.20 * expected
                + 1.20 * params["risk"] * vol
                + 2.70 * params["cvar"] * tail
                + 2.70 * params["drawdown"] * dd
                + 1.00 * params["concentration"] * conc
                + 3.20 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "growth_guardrails":
            return (
                -1.60 * expected
                + 0.70 * params["risk"] * vol
                + 0.90 * params["cvar"] * tail
                + 0.85 * params["drawdown"] * dd
                + 0.70 * params["concentration"] * conc
                + 0.90 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "broad_diversification":
            return (
                -0.25 * expected
                + 0.80 * params["risk"] * vol
                + 0.80 * params["cvar"] * tail
                + 0.80 * params["drawdown"] * dd
                + 3.50 * params["concentration"] * conc
                + 1.10 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "risk_parity":
            return (
                -0.10 * expected
                + 0.55 * params["risk"] * vol
                + 0.70 * params["cvar"] * tail
                + 0.70 * params["drawdown"] * dd
                + 22.0 * rp
                + 0.60 * params["concentration"] * conc
                + 1.00 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "minimum_volatility":
            return (
                3.20 * vol
                + 0.65 * params["cvar"] * tail
                + 0.65 * params["drawdown"] * dd
                + 0.80 * params["concentration"] * conc
                + 0.80 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "downside_cvar":
            return (
                -0.10 * expected
                + 0.70 * params["risk"] * vol
                + 3.40 * params["cvar"] * tail
                + 2.60 * params["drawdown"] * dd
                + 1.00 * params["concentration"] * conc
                + 2.00 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "max_sharpe_guardrails":
            sharpe_proxy = expected / max(vol, 1e-6)
            return (
                -1.40 * sharpe_proxy
                + 0.70 * params["cvar"] * tail
                + 0.70 * params["drawdown"] * dd
                + 0.70 * params["concentration"] * conc
                + 0.80 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "worst_case_robust":
            return (
                -0.15 * hist_expected
                + 1.00 * params["risk"] * vol
                + 1.40 * params["cvar"] * tail
                + 1.40 * params["drawdown"] * dd
                + 1.00 * params["concentration"] * conc
                + 5.00 * params["scenario_loss_penalty"] * worst_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        if model_type == "scenario_aware":
            return (
                -0.25 * hist_expected
                -2.20 * max(scen, -1.0)   # reward positive scenario survival
                + 1.00 * params["risk"] * vol
                + 1.80 * params["cvar"] * tail
                + 1.80 * params["drawdown"] * dd
                + 1.00 * params["concentration"] * conc
                + 5.50 * params["scenario_loss_penalty"] * scen_loss
                + params["turnover"] * turnover
                + params["tax_penalty"] * tax_drag
            )

        # balanced_resilience
        return (
            -1.00 * expected
            + 1.00 * params["risk"] * vol
            + 1.10 * params["cvar"] * tail
            + 1.10 * params["drawdown"] * dd
            + 1.00 * params["concentration"] * conc
            + 1.40 * params["scenario_loss_penalty"] * scen_loss
            + params["turnover"] * turnover
            + params["tax_penalty"] * tax_drag
        )

    x0 = norm(np.ones(n) / n)
    res = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 4000, "ftol": 1e-10},
    )
    if not res.success:
        st.warning("Optimisation warning: " + str(res.message) + ". RAPOR-LLM will use the best numerical solution returned by SLSQP.")
    w_out = norm(res.x if res.x is not None else x0)
    # Final numerical clean-up: respect non-negativity and normalisation.
    w_out = norm(w_out)
    return w_out, min_w

def buy_plan(tickers, latest, w, budget, brokerage_fee, min_order, fractional):
    latest = np.array(latest, dtype=float)
    w = np.array(w, dtype=float)
    target = w * budget
    n = len(w)

    if fractional:
        gross = target.copy()
        fees = np.where(gross > 0, brokerage_fee, 0.0)
        scale = max((budget - fees.sum()) / max(gross.sum(), 1e-9), 0)
        values = gross * scale
        units = values / latest
        reasons = ["Fractional purchase" if values[i] > 0 else "No target" for i in range(n)]
    else:
        units = np.floor(target / latest).astype(int)
        units = np.maximum(units, 0)

        def cost(u):
            vals = u * latest
            return vals.sum() + brokerage_fee * np.sum(vals > 0)

        def clean_min_order(u):
            vals = u * latest
            u = u.copy()
            u[(vals > 0) & (vals < min_order)] = 0
            return u

        units = clean_min_order(units)

        while cost(units) > budget and units.sum() > 0:
            vals = units * latest
            actual = vals / max(vals.sum(), 1e-9)
            candidates = np.where(units > 0)[0]
            remove_i = candidates[np.argmax(actual[candidates] - w[candidates])]
            units[remove_i] -= 1
            units = clean_min_order(units)

        improved = True
        while improved:
            improved = False
            vals = units * latest
            cash = budget - cost(units)
            actual = vals / max(vals.sum(), 1e-9)
            current_error = np.sum((actual - w) ** 2)
            best_i = None
            best_gain = 0.0
            for i in range(n):
                extra_fee = brokerage_fee if units[i] == 0 else 0.0
                if latest[i] + extra_fee <= cash:
                    trial = units.copy()
                    trial[i] += 1
                    trial_vals = trial * latest
                    if 0 < trial_vals[i] < min_order:
                        continue
                    trial_w = trial_vals / max(trial_vals.sum(), 1e-9)
                    gain = current_error - np.sum((trial_w - w) ** 2)
                    if gain > best_gain:
                        best_i = i
                        best_gain = gain
            if best_i is not None:
                units[best_i] += 1
                improved = True

        values = units * latest
        reasons = []
        for i in range(n):
            if units[i] > 0:
                reasons.append("Purchased")
            elif target[i] < latest[i]:
                reasons.append("Target below one unit price")
            elif target[i] < min_order:
                reasons.append("Target below minimum order")
            else:
                reasons.append("Not selected / insufficient cash")

    values = units * latest
    fees = np.where(values > 0, brokerage_fee, 0.0)
    actual_w = values / max(values.sum(), 1e-9)

    return pd.DataFrame({
        "Ticker": tickers,
        "Latest Price": latest,
        "Target Weight": w,
        "Target AUD": target,
        "Units to Buy": units,
        "Order Value": values,
        "Brokerage Fee": fees,
        "Actual Weight": actual_w,
        "Gap vs Target": actual_w - w,
        "Reason": reasons,
    }), budget - values.sum() - fees.sum()

def asset_diagnostics(returns, allocation, weights, cov):
    tickers = list(allocation["Ticker"])
    mean_ret = ann_ret(returns[tickers]).reindex(tickers).fillna(0).values
    vol = ann_vol(returns[tickers]).reindex(tickers).fillna(0).values
    rc = risk_contribution(weights, cov)
    out = allocation.copy()
    out["Asset Expected Return"] = mean_ret
    out["Asset Volatility"] = vol
    out["Risk Contribution"] = rc
    out["Return Contribution"] = out["Target Weight"].values * mean_ret
    return out

def make_gauge(title, value, suffix="/100"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(value),
        number={"suffix": suffix},
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"thickness": 0.28},
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fef3c7"},
                {"range": [70, 100], "color": "#dcfce7"},
            ],
        },
    ))
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=45, b=10))
    return fig

def make_drawdown_series(port_ret):
    wealth = (1 + port_ret).cumprod()
    return wealth / wealth.cummax() - 1

# ============================================================
# Analyst
# ============================================================

def rule_based_analysis(context):
    metrics = context["metrics"]
    alloc = context["allocation"]
    group_alloc = context["group_alloc"]
    bp = context["buy_plan"]
    scenario_contrib = context["scenario_contrib"]
    live_df = context["live_df"]

    ret = metrics["Expected annual return"]
    vol = metrics["Annual volatility"]
    tail = metrics["Daily CVaR 95%"]
    dd = metrics["Max drawdown"]

    fees = bp["Brokerage Fee"].sum()
    order_value = bp["Order Value"].sum()
    capital = context["capital"]
    cash_left = context["cash_left"]
    fee_ratio = fees / max(capital, 1e-9)
    zero_units = bp[bp["Units to Buy"] == 0]

    hhi = float(np.sum(np.square(alloc["Target Weight"].values)))
    effective_n = 1 / max(hhi, 1e-9)

    defensive = group_alloc[group_alloc["Group"].isin(["Bonds", "Gold", "Cash"])]["Target Weight"].sum()
    equity = group_alloc[group_alloc["Group"].str.contains("Equity", case=False, na=False)]["Target Weight"].sum()
    shock_assets = group_alloc[group_alloc["Group"].isin(["Gold", "Energy", "Resources", "Property"])]["Target Weight"].sum()

    nonzero_live = live_df[np.abs(live_df["Manual Market Move %"]) > 1e-9]
    if len(nonzero_live):
        live_text = nonzero_live[["Ticker", "Manual Market Move %", "Adjusted Price"]].to_string(index=False)
    else:
        live_text = "No manual live-market moves were entered."

    worst = scenario_contrib.sort_values("Contribution").head(5)
    best = scenario_contrib.sort_values("Contribution", ascending=False).head(5)

    recommendations = []
    if context["scenario_return"] < -0.05:
        recommendations.append("The current scenario produces a meaningful loss. Test 'Optimise for my selected scenario' or raise scenario importance.")
    if dd > 0.18:
        recommendations.append("Maximum drawdown is high for a low-risk mandate. Test 'Protect my capital' or increase bond/gold guardrails.")
    if vol > 0.10:
        recommendations.append("Annual volatility is not low. Increase risk sensitivity or reduce growth/sector exposure.")
    if fee_ratio > 0.02:
        recommendations.append("Brokerage drag is too high. Reduce ETF count or increase budget.")
    if len(zero_units) > 0:
        recommendations.append("Some target allocations cannot be bought with whole units. Use fewer ETFs for the starter portfolio.")
    if effective_n < 4:
        recommendations.append("Effective diversification is weak. Test 'Spread risk widely' or lower maximum ETF weight.")
    if not recommendations:
        recommendations.append("The result is internally consistent. Still verify fees, tax, liquidity, product suitability, and broker rules.")

    model_comp = context.get("model_comparison", pd.DataFrame())
    if isinstance(model_comp, pd.DataFrame) and len(model_comp):
        top_models_text = model_comp.head(5)[[
            "Business option", "Strategy score", "Expected annual return",
            "Annual volatility", "Daily CVaR 95%", "Max drawdown",
            "Selected scenario return", "Worst scenario return"
        ]].to_string(index=False)
    else:
        top_models_text = "Model comparison is not available."

    bench_comp = context.get("benchmark_comparison", pd.DataFrame())
    if isinstance(bench_comp, pd.DataFrame) and len(bench_comp):
        benchmark_text = bench_comp[[
            "Portfolio", "Strategy score", "Expected annual return",
            "Annual volatility", "Daily CVaR 95%", "Max drawdown",
            "Selected scenario return", "Worst scenario return"
        ]].to_string(index=False)
    else:
        benchmark_text = "Benchmark comparison is not available."

    analyst_mode = context.get("analyst_mode", "Integrated decision-support system analyst")

    return f"""
## Financial Copilot Portfolio Review

### 1. Executive summary

Business objective: **{context["investment_style"]}**  
Optimisation approach: **{context["optimisation_approach"]}**  
Scenario: **{context["scenario_name"]}**  \nScenario type: **{context.get("scenario_source", "Not specified")}**

This report combines five layers of evidence: historical behaviour, scenario stress testing, manual live-market moves, executable trade sizing, and asset-class concentration. The recommendation should be read as decision support, not as an instruction to trade.

Historical profile:

- Expected annual return: **{ret:.2%}**
- Annual volatility: **{vol:.2%}**
- Daily CVaR 95%: **{tail:.2%}**
- Maximum drawdown: **{dd:.2%}**
- Scenario/live-market portfolio result: **{context["scenario_return"]:.2%}**  
Confidence level score: **{context.get("ai_confidence_score", 0):.0f}/100**

This result updates when you change the scenario, scenario importance, live-market inputs, or selected strategy objective.

### 2. Why scenario changes now matter

The selected scenario is not only reported after the fact. It enters the optimisation in three ways:

1. It tilts the expected-return vector used by the optimiser.
2. It adds a penalty for scenario losses.
3. It can adjust asset-class guardrails, for example increasing gold/energy requirements during inflation or energy-shock scenarios.

Therefore, changing the scenario and clicking **Run RAPOR optimisation** should change the target allocation, especially for the scenario-aware and crisis-resilience approaches.

### 3. Live-market inputs

Manual market moves entered by the user:

{live_text}

These moves are combined with the selected stress scenario. For example, if a market website shows gold up and equities down, those inputs will affect the scenario impact and analyst report.

### 4. Allocation structure

Top allocations:

{alloc.sort_values("Target Weight", ascending=False).head(6)[["Ticker", "Class", "Group", "Target Weight", "Target AUD from New Budget"]].to_string(index=False)}

Group allocation:

{group_alloc.to_string(index=False)}

Structural indicators:

- Defensive allocation: **{defensive:.2%}**
- Equity allocation: **{equity:.2%}**
- Gold/energy/property shock-hedge allocation: **{shock_assets:.2%}**
- Effective number of holdings: **{effective_n:.2f}**

### 5. Scenario impact

{context["scenario_summary"]}

Worst contributors:

{worst[["Ticker", "Scenario Return", "Live Market Move", "Combined Shock", "Contribution"]].to_string(index=False)}

Best contributors:

{best[["Ticker", "Scenario Return", "Live Market Move", "Combined Shock", "Contribution"]].to_string(index=False)}

### 6. Practical execution

- Investment budget: **${capital:,.2f}**
- Order value: **${order_value:,.2f}**
- Brokerage fees: **${fees:,.2f}**
- Brokerage as budget share: **{fee_ratio:.2%}**
- Cash left: **${cash_left:,.2f}**
- ETFs with zero practical units: **{len(zero_units)}**

If many ETFs cannot be bought, the mathematical portfolio is too complex for the current capital level. A starter allocation should use fewer ETFs.

### 7. Strategy recommendation

The model-comparison engine recommends: **{context.get("recommended_model", "Not available")}**.

This recommendation is based on a business-alignment score that combines the selected business objective, selected scenario return, worst-scenario return, volatility, CVaR, drawdown, diversification, brokerage drag, and executable-unit constraints.

### 8. Strategy comparison

Analyst mode: **{analyst_mode}**

Recommended optimisation model: **{context.get("recommended_model", "Not available")}**

Top model-comparison results:

{top_models_text}

Interpretation: the recommended optimisation model should be viewed as the model most aligned with the selected business objective under the current scenario and live-market inputs, not as an objectively best model for all market regimes.

### 9. Benchmark comparison

Benchmark leader: **{context.get("recommended_benchmark", "Not available")}**

Benchmark-comparison results:

{benchmark_text}

This benchmark view shows whether the selected RAPOR allocation is meaningfully different from simple alternatives such as equal weight, defensive, growth, and shock-hedge portfolios.

### 10. Portfolio auditor

The auditor checks whether the recommendation is mathematically and practically credible:

- Feasibility: review the Portfolio Quality Review tab; failed checks invalidate the allocation.
- Scenario stability: if the selected scenario is acceptable but the worst scenario is poor, robustness is incomplete.
- Execution realism: if many ETFs have zero units, the target allocation is not practically implementable at the current budget.
- Cost drag: if brokerage is high relative to capital, the model is over-fragmented.
- Data risk: historical ETF behaviour may not represent future crisis dynamics.

### 11. Critical challenger

The strongest challenge to this optimiser is that it can look scientific while still being driven by assumptions:

- Scenario returns are user-defined and should not be treated as forecasts.
- Penalty weights influence the allocation strongly.
- Small budgets can make mathematically optimal allocations impossible to execute.
- A strong backtest does not prove forward resilience.
- LLM explanations can improve interpretability, but they do not validate the financial truth of the model.

### 12. Investor coach

Practical next steps:

1. Compare the selected RAPOR portfolio against the benchmark tab.
2. Check whether the selected model is also strong under the worst scenario.
3. Reduce ETF count if execution quality is weak.
4. Re-run after entering live market moves from an external website.
5. Treat LLM output as explanation and critique, not as financial advice.

### 13. Advanced system note

RAPOR AI is designed to do more than summarise results. It reviews feasibility, challenges the optimisation output, explains benchmark comparisons, and translates technical risk measures into practical decision-support language.

### 14. Detailed recommendations

{chr(10).join([f"{i+1}. {r}" for i, r in enumerate(recommendations)])}

### 15. Business and implementation implications

- If the execution score is weak, the practical buy plan matters more than the mathematical target weights.
- If the scenario resilience score is weak, the selected scenario is exposing a structural vulnerability.
- If diversification is weak, the portfolio may look broad by ticker count but still behave like a concentrated exposure.
- If brokerage drag is high, the portfolio should be simplified until capital increases.
- If live-market moves are large, use them as a short-term stress overlay rather than as a long-term expected-return forecast.

### 16. Suggested next actions

1. Compare the current result with **Protect my capital**.
2. Compare it with **Optimise for my selected scenario**.
3. Increase and decrease scenario importance to check sensitivity.
4. Enter current live moves from your broker or market website.
5. Re-run the optimiser and check whether allocation changes are stable or unstable.
6. If small changes create large allocation shifts, the model is sensitive and should be used cautiously.

### 17. Final interpretation

RAPOR-LLM links business objective, scenario assumptions, live market inputs, optimisation, execution feasibility, benchmark comparison, and AI interpretation. If market conditions change, update the live inputs, re-optimise, and regenerate the report.
"""

def make_prompt(context, question):
    payload = {
        "question": question,
        "investment_style": context["investment_style"],
        "optimisation_approach": context["optimisation_approach"],
        "scenario_name": context["scenario_name"],
        "predefined_scenario_name": context.get("predefined_scenario_name", ""),
        "scenario_source": context.get("scenario_source", ""),
        "scenario_return": context["scenario_return"],
        "scenario_summary": context["scenario_summary"],
        "metrics": context["metrics"],
        "capital": context["capital"],
        "cash_left": context["cash_left"],
        "allocation": context["allocation"][["Ticker", "Class", "Group", "Target Weight", "Target AUD from New Budget"]].to_dict(orient="records"),
        "group_allocation": context["group_alloc"].to_dict(orient="records"),
        "buy_plan": context["buy_plan"][["Ticker", "Target Weight", "Target AUD", "Units to Buy", "Order Value", "Brokerage Fee", "Reason"]].to_dict(orient="records"),
        "live_market_inputs": context["live_df"][["Ticker", "Manual Market Move %", "Adjusted Price"]].to_dict(orient="records"),
        "scenario_contributions": context["scenario_contrib"][["Ticker", "Scenario Return", "Live Market Move", "Combined Shock", "Contribution"]].to_dict(orient="records"),
        "validation_report": context.get("validation_report", pd.DataFrame()).to_dict(orient="records") if isinstance(context.get("validation_report"), pd.DataFrame) else [],
        "scenario_library_results": context.get("scenario_library_results", pd.DataFrame()).to_dict(orient="records") if isinstance(context.get("scenario_library_results"), pd.DataFrame) else [],
        "model_comparison": context.get("model_comparison", pd.DataFrame()).to_dict(orient="records") if isinstance(context.get("model_comparison"), pd.DataFrame) else [],
        "benchmark_comparison": context.get("benchmark_comparison", pd.DataFrame()).to_dict(orient="records") if isinstance(context.get("benchmark_comparison"), pd.DataFrame) else [],
        "recommended_model": context.get("recommended_model", "Not available"),
        "recommended_benchmark": context.get("recommended_benchmark", "Not available"),
        "model_formula_description": context.get("model_formula_description", ""),
        "analyst_mode": context.get("analyst_mode", "Integrated decision-support system analyst"),
    }
    return f"""You are a cautious portfolio decision-support analyst. This is not financial advice.
Always respond in English.
Be critical, technical, and business-oriented.
Explain how the selected scenario and manual live-market inputs changed the portfolio.

Input JSON:
{json.dumps(payload, indent=2)}

Use the requested analyst_mode from the JSON. Produce a strong technical decision-support system report.

Mandatory roles:
1. Executive summary
2. Strategy comparison: explain which model is most consistent with the user's business objective and why
3. Benchmark comparison: explain whether the selected RAPOR portfolio beats naive/policy benchmarks
4. Portfolio auditor: identify feasibility, guardrail, concentration, scenario, execution, and data-quality issues
5. Critical challenger: challenge the optimiser's recommendation and explain where it may be misleading
6. Investor coach: translate the result into practical next steps without giving personal financial advice
8. Suggested model-setting changes
9. What to test next
10. Final interpretation
"""

def call_openai(key, model, prompt):
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a cautious portfolio decision-support analyst. You do not provide personal financial advice."},
                {"role": "user", "content": prompt},
            ],
            "temperature": .2,
            "max_tokens": 2500,
        },
        timeout=90,
    )
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI HTTP {r.status_code}: {r.text}")
    return r.json()["choices"][0]["message"]["content"]



def call_gemini(api_key, model, prompt):
    """
    Gemini Developer API using REST generateContent.
    Recommended free/low-cost option for RAPOR-LLM.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 3000},
    }
    r = requests.post(url, json=payload, timeout=90)
    if r.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {r.status_code}: {r.text}")
    data = r.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise RuntimeError(f"Unexpected Gemini response: {data}")

def call_groq(api_key, model, prompt):
    """
    Groq uses an OpenAI-compatible chat completions endpoint.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are RAPOR AI, a cautious portfolio decision-support copilot. You do not provide personal financial advice."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 3000,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=payload, timeout=90)
    if r.status_code != 200:
        raise RuntimeError(f"Groq HTTP {r.status_code}: {r.text}")
    return r.json()["choices"][0]["message"]["content"]

def call_openrouter(api_key, model, prompt):
    """
    OpenRouter OpenAI-compatible endpoint.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are RAPOR AI, a cautious portfolio decision-support copilot. You do not provide personal financial advice."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 3000,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "RAPOR-LLM",
    }
    r = requests.post(url, headers=headers, json=payload, timeout=90)
    if r.status_code != 200:
        raise RuntimeError(f"OpenRouter HTTP {r.status_code}: {r.text}")
    return r.json()["choices"][0]["message"]["content"]

def run_ai_provider(provider, prompt, openai_key="", openai_model="", gemini_key="", gemini_model="", groq_key="", groq_model="", openrouter_key="", openrouter_model=""):
    if provider == "OpenAI":
        if not openai_key:
            raise RuntimeError("OpenAI API key is empty.")
        return call_openai(openai_key, openai_model, prompt), "OpenAI"
    if provider == "Gemini":
        if not gemini_key:
            raise RuntimeError("Gemini API key is empty.")
        return call_gemini(gemini_key, gemini_model, prompt), "Gemini"
    if provider == "Groq":
        if not groq_key:
            raise RuntimeError("Groq API key is empty.")
        return call_groq(groq_key, groq_model, prompt), "Groq"
    if provider == "OpenRouter":
        if not openrouter_key:
            raise RuntimeError("OpenRouter API key is empty.")
        return call_openrouter(openrouter_key, openrouter_model, prompt), "OpenRouter"
    raise RuntimeError("External AI provider is not selected.")

def make_ai_scenario_prompt(user_scenario, tickers, allocation, group_alloc):
    return f"""
You are RAPOR AI. Generate a plausible stress scenario for ETF portfolio testing.

User scenario description:
{user_scenario}

Available ETF tickers:
{tickers}

Current allocation:
{allocation[["Ticker", "Group", "Target Weight"]].to_dict(orient="records")}

Group allocation:
{group_alloc.to_dict(orient="records")}

Return ONLY valid JSON with this exact structure:
{{
  "scenario_name": "short scenario name",
  "scenario_logic": "brief explanation",
  "ticker_shocks": {{
    "TICKER": decimal_return
  }}
}}

Rules:
- decimal_return must be numeric, e.g. -0.12 for -12%, 0.08 for +8%.
- Include every ticker exactly once.
- No markdown.
- No personal financial advice.
"""

def parse_ai_scenario_json(text, tickers):
    try:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json", "", 1).strip()
        data = json.loads(raw)
        shocks = data.get("ticker_shocks", {})
        out = [float(shocks.get(t, 0.0)) for t in tickers]
        return data.get("scenario_name", "AI scenario"), data.get("scenario_logic", ""), np.array(out, dtype=float), data
    except Exception as e:
        neutral = np.zeros(len(tickers), dtype=float)
        return "AI scenario parse failed", f"Could not parse AI JSON. Error: {e}", neutral, {}


def clean_scenario_label_for_ai(label):
    """
    Prevent recursive AI scenario names such as:
    AI-generated: Strong Bull Market - AI enhanced - AI enhanced
    """
    text = str(label).replace("AI-generated: ", "").strip()
    for suffix in [" - AI enhanced", " - AI Enhanced"]:
        while text.endswith(suffix):
            text = text[: -len(suffix)].strip()
    return text

def get_active_scenario_vector(valid, selected_scenario_option):
    """
    Single source of truth for scenario shocks.

    The sidebar has only one Scenario selector.
    If it is a predefined scenario, use predefined shocks.
    If it is AI-generated, use the stored AI scenario vector.
    """
    if selected_scenario_option.startswith("AI-generated:"):
        ai_vector = st.session_state.get("ai_scenario_vector")
        ai_name = st.session_state.get("ai_scenario_name", "AI-generated scenario")
        if ai_vector is not None:
            return np.array(ai_vector, dtype=float), ai_name, "AI-generated scenario"
        # fallback if session state was cleared
        return scenario_template(valid, "Neutral / no stress"), "Neutral / no stress", "Fallback: AI scenario missing"

    return scenario_template(valid, selected_scenario_option), selected_scenario_option, "Predefined scenario"


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.header("1. Capital and trading")
    capital = st.number_input("Investment budget (AUD)", min_value=100.0, value=900.0, step=100.0)
    start = st.date_input("Historical data start date", pd.to_datetime("2018-01-01"))
    brokerage_fee = st.number_input("Brokerage fee per order", min_value=0.0, value=3.0, step=.5)
    min_order = st.number_input("Minimum order value", min_value=0.0, value=100.0, step=50.0)
    fractional = st.checkbox("Broker supports fractional ETF units", False)

    st.header("2. Business objective")

    MODEL_PRESETS = {
        "Protect my capital": {
            "model_type": "capital_protection",
            "plain": "Most conservative. Prioritises smaller losses, lower volatility, and lower drawdown.",
            "risk": 14.0, "cvar": 14.0, "drawdown": 14.0, "concentration": 6.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.04, "max_weight": 0.22,
            "no_zero": True, "scenario_loss_penalty": 1.2, "scenario_mu_blend": 0.25,
        },
        "Prepare for market shocks": {
            "model_type": "crisis_resilience",
            "plain": "Designed for recession, geopolitical shocks, inflation stress, and market sell-offs.",
            "risk": 11.0, "cvar": 16.0, "drawdown": 15.0, "concentration": 6.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.04, "max_weight": 0.24,
            "no_zero": True, "scenario_loss_penalty": 1.8, "scenario_mu_blend": 0.35,
        },
        "Balanced resilient portfolio": {
            "model_type": "balanced_resilience",
            "plain": "Balanced compromise between return, risk control, diversification, and practical implementation.",
            "risk": 10.0, "cvar": 10.0, "drawdown": 8.0, "concentration": 5.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.05, "max_weight": 0.25,
            "no_zero": True, "scenario_loss_penalty": 1.0, "scenario_mu_blend": 0.25,
        },
        "Grow, but keep guardrails": {
            "model_type": "growth_guardrails",
            "plain": "Accepts more risk to pursue higher historical return, while still limiting drawdown and concentration.",
            "risk": 6.0, "cvar": 7.0, "drawdown": 6.0, "concentration": 4.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.03, "max_weight": 0.30,
            "no_zero": True, "scenario_loss_penalty": 0.8, "scenario_mu_blend": 0.15,
        },
        "Spread risk widely": {
            "model_type": "broad_diversification",
            "plain": "Prioritises broad diversification and avoids a few dominant positions.",
            "risk": 8.0, "cvar": 8.0, "drawdown": 7.0, "concentration": 8.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.05, "max_weight": 0.20,
            "no_zero": True, "scenario_loss_penalty": 1.0, "scenario_mu_blend": 0.20,
        },
        "Equalise risk contribution": {
            "model_type": "risk_parity",
            "plain": "Attempts to make each ETF contribute more evenly to total portfolio risk.",
            "risk": 7.0, "cvar": 7.0, "drawdown": 7.0, "concentration": 5.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.03, "max_weight": 0.25,
            "no_zero": True, "scenario_loss_penalty": 0.9, "scenario_mu_blend": 0.20,
        },
        "Minimum volatility": {
            "model_type": "minimum_volatility",
            "plain": "Finds the lowest-volatility portfolio that still respects practical and asset-class guardrails.",
            "risk": 12.0, "cvar": 8.0, "drawdown": 8.0, "concentration": 5.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.03, "max_weight": 0.25,
            "no_zero": True, "scenario_loss_penalty": 0.8, "scenario_mu_blend": 0.10,
        },
        "Downside protection / CVaR": {
            "model_type": "downside_cvar",
            "plain": "Focuses on severe loss days and drawdown rather than average volatility.",
            "risk": 8.0, "cvar": 16.0, "drawdown": 13.0, "concentration": 5.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.04, "max_weight": 0.24,
            "no_zero": True, "scenario_loss_penalty": 1.4, "scenario_mu_blend": 0.25,
        },
        "Maximum return per unit risk": {
            "model_type": "max_sharpe_guardrails",
            "plain": "Approximates a Sharpe-style portfolio: more return per unit of risk, with downside guardrails.",
            "risk": 7.0, "cvar": 7.0, "drawdown": 7.0, "concentration": 4.5,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.03, "max_weight": 0.30,
            "no_zero": True, "scenario_loss_penalty": 0.9, "scenario_mu_blend": 0.20,
        },
        "Robust across all scenarios": {
            "model_type": "worst_case_robust",
            "plain": "Minimises the worst loss across the full scenario library, not only the selected scenario.",
            "risk": 9.0, "cvar": 12.0, "drawdown": 12.0, "concentration": 5.5,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.04, "max_weight": 0.24,
            "no_zero": True, "scenario_loss_penalty": 1.8, "scenario_mu_blend": 0.30,
        },
        "Optimise for my selected scenario": {
            "model_type": "scenario_aware",
            "plain": "Gives the selected scenario the strongest influence on the target allocation.",
            "risk": 9.0, "cvar": 12.0, "drawdown": 12.0, "concentration": 5.0,
            "turnover": 2.0, "tax_penalty": 1.0, "min_weight": 0.04, "max_weight": 0.25,
            "no_zero": True, "scenario_loss_penalty": 2.2, "scenario_mu_blend": 0.55,
        },
    }

    investment_style = st.selectbox("Business objective", list(MODEL_PRESETS.keys()), index=2)
    preset = MODEL_PRESETS[investment_style]
    st.info(preset["plain"])

    st.header("3. Scenario")
    predefined_scenarios = [
        "Middle East energy shock",
        "Global recession",
        "High inflation",
        "Technology selloff",
        "Strong bull market",
        "Neutral / no stress",
    ]

    scenario_options = predefined_scenarios.copy()
    if "ai_scenario_name" in st.session_state and "ai_scenario_vector" in st.session_state:
        scenario_options.append("AI-generated: " + st.session_state["ai_scenario_name"])

    # 
    # 
    pending_ai_option = st.session_state.pop("pending_ai_scenario_option", None)
    if pending_ai_option is not None and pending_ai_option in scenario_options:
        st.session_state["scenario_select"] = pending_ai_option

    if "scenario_select" not in st.session_state or st.session_state["scenario_select"] not in scenario_options:
        st.session_state["scenario_select"] = scenario_options[0]

    scenario_name = st.selectbox(
        "Scenario",
        scenario_options,
        key="scenario_select",
        help="This is the single active scenario used by optimisation, scenario charts, comparison tables, and RAPOR AI."
    )

    scenario_importance = st.slider("Scenario importance", 0.0, 3.0, 1.6, 0.1)
    scenario_guardrail_strength = st.slider("Scenario guardrail strength", 0.0, 1.0, 0.8, 0.1)
    live_importance = st.slider("Manual live-move importance", 0.0, 2.0, 1.0, 0.1)

    st.info(f"Active scenario selected: {scenario_name}")

    show_advanced = st.checkbox("Show advanced controls", value=False)
    if show_advanced:
        params = {
            "model_type": preset["model_type"],
            "no_zero": st.checkbox("Keep every selected ETF represented", preset["no_zero"]),
            "min_weight": st.slider("Minimum allocation per selected ETF", 0.0, .15, float(preset["min_weight"]), .01),
            "max_weight": st.slider("Maximum allocation per ETF", .05, .60, float(preset["max_weight"]), .05),
            "risk": st.slider("Sensitivity to normal volatility", 0.0, 30.0, float(preset["risk"]), .5),
            "cvar": st.slider("Sensitivity to severe-loss days", 0.0, 30.0, float(preset["cvar"]), .5),
            "drawdown": st.slider("Sensitivity to large falls", 0.0, 30.0, float(preset["drawdown"]), .5),
            "concentration": st.slider("Preference for diversification", 0.0, 20.0, float(preset["concentration"]), .5),
            "turnover": st.slider("Preference to avoid unnecessary rebalancing", 0.0, 20.0, float(preset["turnover"]), .5),
            "tax_drag": st.slider("Estimated annual tax drag", 0.0, .05, .005, .001),
            "tax_penalty": st.slider("Sensitivity to tax drag", 0.0, 20.0, float(preset["tax_penalty"]), .5),
            "scenario_loss_penalty": st.slider("Scenario-loss penalty", 0.0, 5.0, float(preset["scenario_loss_penalty"]), .1),
            "scenario_mu_blend": st.slider("Scenario influence on expected returns", 0.0, .80, float(preset["scenario_mu_blend"]), .05),
        }
    else:
        params = {
            "model_type": preset["model_type"],
            "no_zero": preset["no_zero"],
            "min_weight": preset["min_weight"],
            "max_weight": preset["max_weight"],
            "risk": preset["risk"],
            "cvar": preset["cvar"],
            "drawdown": preset["drawdown"],
            "concentration": preset["concentration"],
            "turnover": preset["turnover"],
            "tax_drag": .005,
            "tax_penalty": preset["tax_penalty"],
            "scenario_loss_penalty": preset["scenario_loss_penalty"],
            "scenario_mu_blend": preset["scenario_mu_blend"],
        }

    st.header("4. Resilience rules")
    use_groups = st.checkbox("Apply asset-class guardrails", True)
    base_group_bounds = {
        "Gold": (.08, .25),
        "Bonds": (.20, .45),
        "Energy": (.03, .15),
        "Property": (.03, .15),
        "Equity Australia": (.08, .25),
        "Equity Global": (.08, .25),
        "Equity US": (.05, .20),
    } if use_groups else {}

    st.header("5. Asset universe")
    with st.expander("Edit ETF universe: ASX and optional US-listed ETFs", False):
        assets = st.data_editor(ASSETS, num_rows="dynamic", use_container_width=True, height=520)
    included = assets[assets["Include"] == True].copy()
    tickers = included["Ticker"].astype(str).tolist()

    st.header("6. RAPOR AI")
    provider = st.selectbox("Copilot engine", ["Rule-Based Analyst", "Gemini", "Groq", "OpenRouter", "OpenAI"])
    api_key = ""
    model = ""
    gemini_api_key = ""
    gemini_model = "gemini-2.5-flash-lite"
    groq_api_key = ""
    groq_model = "llama-3.3-70b-versatile"
    openrouter_api_key = ""
    openrouter_model = "deepseek/deepseek-chat"

    if provider == "Gemini":
        st.caption("Recommended free/low-cost option. Get a key from Google AI Studio.")
        gemini_api_key = st.text_input("Gemini API key", os.getenv("GEMINI_API_KEY", ""), type="password")
        gemini_model = st.text_input("Gemini model", "gemini-2.5-flash-lite")
    elif provider == "Groq":
        st.caption("Fast hosted option from Groq Cloud.")
        groq_api_key = st.text_input("Groq API key", os.getenv("GROQ_API_KEY", ""), type="password")
        groq_model = st.text_input("Groq model", "llama-3.3-70b-versatile")
    elif provider == "OpenRouter":
        st.caption("Use OpenRouter free/low-cost models if available in your account.")
        openrouter_api_key = st.text_input("OpenRouter API key", os.getenv("OPENROUTER_API_KEY", ""), type="password")
        openrouter_model = st.text_input("OpenRouter model", "deepseek/deepseek-chat")
    elif provider == "OpenAI":
        st.caption("Requires active OpenAI API billing/quota. ChatGPT Plus/Pro is separate from API billing.")
        api_key = st.text_input("OpenAI API key", os.getenv("OPENAI_API_KEY", ""), type="password")
        model = st.text_input("OpenAI model", "gpt-4.1-mini")
    else:
        st.caption("No API required. Uses connected deterministic English analyst.")

    analyst_mode = st.selectbox(
        "Analyst mode",
        [
            "Quick Summary",
            "Risk Review",
            "Portfolio Critique",
            "Investment Coach",
            "Advanced Analysis",
        ],
        index=0,
        help="Choose the style of RAPOR AI output."
    )

    question = st.text_area(
        "Ask the Financial Copilot",
        "Explain my portfolio clearly. What are the main risks, how does it compare with benchmarks, and what should I test next?",
        height=130,
    )

    run_button = st.button("Run RAPOR optimisation", type="primary")

# ============================================================
# Main
# ============================================================

def make_config_signature():
    """
    Capture the user-controlled inputs that materially affect optimisation outputs.
    If this signature changes after results are shown, the app automatically re-optimises
    so charts, tables, buy plan, benchmarks and copilot context cannot become stale.
    """
    return json.dumps({
        "tickers": tickers,
        "start": str(start),
        "capital": float(capital),
        "brokerage_fee": float(brokerage_fee),
        "min_order": float(min_order),
        "fractional": bool(fractional),
        "investment_style": investment_style,
        "scenario_name": scenario_name,
        "scenario_importance": float(scenario_importance),
        "scenario_guardrail_strength": float(scenario_guardrail_strength),
        "live_importance": float(live_importance),
        "use_groups": bool(use_groups),
        "base_group_bounds": base_group_bounds,
        "params": params,
    }, sort_keys=True, default=str)

current_config_signature = make_config_signature()

if len(tickers) < 2:
    st.error("Please select at least two ETFs.")
    st.stop()

st.markdown(
    f"""
<div class="card-blue">
<b>Business objective:</b> {investment_style}<br>
<b>Scenario:</b> {scenario_name}<br>
<span class="small-note">{preset["plain"]}</span>
</div>
""",
    unsafe_allow_html=True,
)

with st.expander("Selected ETF universe", expanded=False):
    st.dataframe(included, use_container_width=True, height=280)



def make_group_target_weights(valid, groups, group_targets):
    """
    Build a benchmark weight vector from group-level targets.
    If a group has multiple ETFs, its target is equally distributed within that group.
    Missing groups are ignored and remaining weights are renormalised.
    """
    w = np.zeros(len(valid), dtype=float)
    groups_arr = np.array(groups)
    for g, target in group_targets.items():
        idx = np.where(groups_arr == g)[0]
        if len(idx) > 0 and target > 0:
            w[idx] = target / len(idx)
    if w.sum() <= 0:
        return np.ones(len(valid)) / len(valid)
    return w / w.sum()

def evaluate_weight_vector(label, model_code, weights, returns, valid, latest, combined, scen_matrix):
    weights = norm(weights)
    metrics, port_ret = portfolio_metrics(returns, weights)
    execution, cash_left = buy_plan(valid, latest, weights, capital, brokerage_fee, min_order, fractional)
    scen_returns = scen_matrix @ weights
    hhi = float(np.sum(np.square(weights)))
    effective_n = 1 / max(hhi, 1e-9)
    fee_ratio = float(execution["Brokerage Fee"].sum()) / max(capital, 1e-9)
    zero_units = int((execution["Units to Buy"] == 0).sum())
    return {
        "Portfolio": label,
        "Model code": model_code,
        "Expected annual return": metrics["Expected annual return"],
        "Annual volatility": metrics["Annual volatility"],
        "Daily CVaR 95%": metrics["Daily CVaR 95%"],
        "Max drawdown": metrics["Max drawdown"],
        "Selected scenario return": float(weights @ combined),
        "Worst scenario return": float(np.min(scen_returns)),
        "Effective holdings": effective_n,
        "Brokerage fee ratio": fee_ratio,
        "Zero-unit ETFs": zero_units,
        "Cash left": cash_left,
    }

def compare_against_benchmarks(selected_weights, returns, valid, latest, groups, combined, scen_matrix):
    """
    Public-style benchmark comparison.
    These benchmarks are intentionally simple and interpretable.
    They help show whether the RAPOR-LLM portfolio engine adds value beyond naive allocation rules.
    """
    benchmarks = []

    # 1) Selected RAPOR portfolio
    benchmarks.append(evaluate_weight_vector(
        "Selected RAPOR portfolio",
        "selected_dss",
        selected_weights,
        returns,
        valid,
        latest,
        combined,
        scen_matrix,
    ))

    # 2) Equal weight benchmark
    benchmarks.append(evaluate_weight_vector(
        "Equal weight",
        "equal_weight",
        np.ones(len(valid)) / len(valid),
        returns,
        valid,
        latest,
        combined,
        scen_matrix,
    ))

    # 3) Defensive 40/40/20-style benchmark, adapted to available groups
    defensive_targets = {
        "Bonds": 0.40,
        "Government Bonds": 0.10,
        "Gold": 0.15,
        "Cash": 0.05,
        "Equity Australia": 0.12,
        "Equity Global": 0.12,
        "Equity US": 0.06,
    }
    benchmarks.append(evaluate_weight_vector(
        "Defensive policy benchmark",
        "defensive_policy",
        make_group_target_weights(valid, groups, defensive_targets),
        returns,
        valid,
        latest,
        combined,
        scen_matrix,
    ))

    # 4) Growth policy benchmark
    growth_targets = {
        "Equity Australia": 0.20,
        "Equity Global": 0.30,
        "Equity US": 0.25,
        "Technology": 0.10,
        "Bonds": 0.10,
        "Gold": 0.05,
    }
    benchmarks.append(evaluate_weight_vector(
        "Growth policy benchmark",
        "growth_policy",
        make_group_target_weights(valid, groups, growth_targets),
        returns,
        valid,
        latest,
        combined,
        scen_matrix,
    ))

    # 5) Shock-hedge benchmark
    shock_targets = {
        "Gold": 0.25,
        "Energy": 0.15,
        "Resources": 0.10,
        "Bonds": 0.25,
        "Equity Australia": 0.10,
        "Equity Global": 0.10,
        "Equity US": 0.05,
    }
    benchmarks.append(evaluate_weight_vector(
        "Shock-hedge benchmark",
        "shock_hedge_policy",
        make_group_target_weights(valid, groups, shock_targets),
        returns,
        valid,
        latest,
        combined,
        scen_matrix,
    ))

    out = pd.DataFrame(benchmarks)

    # Relative score for benchmark comparison.
    score_table = out.rename(columns={"Portfolio": "Business option"}).copy()
    score_table["Feasible"] = True
    score_table = score_model_comparison_table(score_table, investment_style)
    out["Strategy score"] = score_table["Strategy score"].values

    return out.sort_values("Strategy score", ascending=False)


def compare_all_models(returns, valid, latest, included_valid, live_df, combined, scen_matrix, scen_names, active_bounds, groups):
    """
    Run every available optimisation model using the same data and constraints.
    Returns model-level comparison table.
    """
    group_map = included_valid.set_index("Ticker")["Group"].to_dict()
    class_map = included_valid.set_index("Ticker")["Class"].to_dict()

    rows = []
    current_w = np.ones(len(valid)) / len(valid)

    for objective_name, preset_model in MODEL_PRESETS.items():
        test_params = {
            "model_type": preset_model["model_type"],
            "no_zero": preset_model["no_zero"],
            "min_weight": preset_model["min_weight"],
            "max_weight": preset_model["max_weight"],
            "risk": preset_model["risk"],
            "cvar": preset_model["cvar"],
            "drawdown": preset_model["drawdown"],
            "concentration": preset_model["concentration"],
            "turnover": preset_model["turnover"],
            "tax_drag": params.get("tax_drag", .005),
            "tax_penalty": preset_model["tax_penalty"],
            "scenario_loss_penalty": preset_model["scenario_loss_penalty"],
            "scenario_mu_blend": preset_model["scenario_mu_blend"],
        }

        try:
            w_cmp, _ = optimise(returns, groups, current_w, test_params, active_bounds, combined, scen_matrix)
            m_cmp, pr_cmp = portfolio_metrics(returns, w_cmp)
            exec_cmp, cash_cmp = buy_plan(valid, latest, w_cmp, capital, brokerage_fee, min_order, fractional)
            scenario_selected = float(w_cmp @ combined)
            scen_returns = scen_matrix @ w_cmp
            worst_scenario = float(np.min(scen_returns))
            hhi = float(np.sum(np.square(w_cmp)))
            effective_n = 1 / max(hhi, 1e-9)
            fees = float(exec_cmp["Brokerage Fee"].sum())
            fee_ratio = fees / max(capital, 1e-9)
            zero_units = int((exec_cmp["Units to Buy"] == 0).sum())
            row = {
                "Business option": objective_name,
                "Model code": preset_model["model_type"],
                "Expected annual return": m_cmp["Expected annual return"],
                "Annual volatility": m_cmp["Annual volatility"],
                "Daily CVaR 95%": m_cmp["Daily CVaR 95%"],
                "Max drawdown": m_cmp["Max drawdown"],
                "Selected scenario return": scenario_selected,
                "Worst scenario return": worst_scenario,
                "Effective holdings": effective_n,
                "Brokerage fee ratio": fee_ratio,
                "Zero-unit ETFs": zero_units,
                "Cash left": cash_cmp,
                "Feasible": True,
            }
            rows.append(row)
        except Exception as e:
            rows.append({
                "Business option": objective_name,
                "Model code": preset_model["model_type"],
                "Expected annual return": np.nan,
                "Annual volatility": np.nan,
                "Daily CVaR 95%": np.nan,
                "Max drawdown": np.nan,
                "Selected scenario return": np.nan,
                "Worst scenario return": np.nan,
                "Effective holdings": np.nan,
                "Brokerage fee ratio": np.nan,
                "Zero-unit ETFs": np.nan,
                "Cash left": np.nan,
                "Strategy score": 0,
                "Feasible": False,
                "Error": str(e),
            })

    comp = pd.DataFrame(rows)
    comp = score_model_comparison_table(comp, investment_style)
    comp = comp.sort_values("Strategy score", ascending=False)
    return comp


def compute_and_store(live_existing=None):
    prices = get_prices(tickers, str(start))
    if prices.empty:
        st.error("No price data downloaded. Check ticker symbols or internet connection.")
        st.stop()

    returns = prices.pct_change().dropna()
    if returns.empty or returns.shape[1] < 2:
        st.error("Not enough valid price history. Select at least two ETFs with data.")
        st.stop()

    valid = list(returns.columns)
    latest = prices[valid].iloc[-1].dropna()
    valid = list(latest.index)
    returns = returns[valid]
    included_valid = included[included["Ticker"].isin(valid)].copy()

    group_map = included_valid.set_index("Ticker")["Group"].to_dict()
    class_map = included_valid.set_index("Ticker")["Class"].to_dict()
    region_map = included_valid.set_index("Ticker")["Region"].to_dict()

    groups = [group_map.get(t, "Other") for t in valid]
    live_df = add_adjusted_prices(build_live_input(valid, latest.values, live_existing))
    active_scenario, active_scenario_name, active_scenario_source = get_active_scenario_vector(
        valid, scenario_name
    )
    live_moves = live_df["Manual Market Move"].values
    combined = combine_shocks(active_scenario, live_moves, scenario_importance, live_importance)
    scen_matrix, scen_names = scenario_matrix_library(valid, live_moves, scenario_importance, live_importance)
    scen_matrix = np.vstack([scen_matrix, combined])
    scen_names = scen_names + [f"Scenario: {active_scenario_name}"]

    # For AI-generated scenarios, use the original base scenario for guardrail logic.
    guardrail_scenario_name = st.session_state.get("ai_base_scenario", scenario_name) if str(scenario_name).startswith("AI-generated:") else scenario_name
    group_bounds = build_group_bounds(base_group_bounds, guardrail_scenario_name, scenario_guardrail_strength)
    active_bounds = {g: b for g, b in group_bounds.items() if g in set(groups)}

    current_w = np.ones(len(valid)) / len(valid)
    w, min_w = optimise(returns, groups, current_w, params, active_bounds, combined, scen_matrix)
    m, port_ret = portfolio_metrics(returns, w)

    trade_prices = live_df["Adjusted Price"].values
    allocation = pd.DataFrame({
        "Ticker": valid,
        "Class": [class_map.get(t, "") for t in valid],
        "Group": [group_map.get(t, "") for t in valid],
        "Region": [region_map.get(t, "") for t in valid],
        "Latest Price": trade_prices,
        "Target Weight": w,
        "Target AUD from New Budget": w * capital,
    }).sort_values("Target Weight", ascending=False)

    group_alloc = allocation.groupby("Group", as_index=False)["Target Weight"].sum().sort_values("Target Weight", ascending=False)
    execution, cash_left = buy_plan(valid, trade_prices, w, capital, brokerage_fee, min_order, fractional)
    wealth = (1 + port_ret).cumprod()

    scenario_return = float(w @ combined)
    scenario_value = capital * (1 + scenario_return)
    scenario_contrib = pd.DataFrame({
        "Ticker": valid,
        "Target Weight": w,
        "Scenario Return": active_scenario,
        "Live Market Move": live_moves,
        "Combined Shock": combined,
        "Contribution": w * combined,
    }).sort_values("Contribution")

    hhi = float(np.sum(np.square(w)))
    effective_n = 1 / max(hhi, 1e-9)
    fee_ratio = execution["Brokerage Fee"].sum() / max(capital, 1e-9)
    zero_count = int((execution["Units to Buy"] == 0).sum())
    scores = compute_scores(m, scenario_return, effective_n, fee_ratio, zero_count, len(w))
    validation_report = validate_weights(w, active_bounds, groups)
    scenario_library_results = pd.DataFrame({
        "Scenario": scen_names,
        "Portfolio Return": scen_matrix @ w,
    })
    model_comparison = compare_all_models(returns, valid, trade_prices, included_valid, live_df, combined, scen_matrix, scen_names, active_bounds, groups)
    benchmark_comparison = compare_against_benchmarks(w, returns, valid, trade_prices, groups, combined, scen_matrix)
    cov = returns.cov().values * 252
    diagnostics = asset_diagnostics(returns, allocation, w, cov)
    drawdown_series = make_drawdown_series(port_ret)

    st.session_state["has_results"] = True
    st.session_state["valid"] = valid
    st.session_state["returns"] = returns
    st.session_state["metrics"] = m
    st.session_state["weights"] = w
    st.session_state["allocation"] = allocation
    st.session_state["group_alloc"] = group_alloc
    st.session_state["execution"] = execution
    st.session_state["cash_left"] = cash_left
    st.session_state["wealth"] = wealth
    st.session_state["corr"] = returns.corr()
    st.session_state["live_df"] = live_df
    st.session_state["scenario_contrib"] = scenario_contrib
    st.session_state["scenario_return"] = scenario_return
    st.session_state["scenario_value"] = scenario_value
    st.session_state["scenario_summary"] = (
        f"{active_scenario_name} [{active_scenario_source}]: combined scenario/live portfolio return {scenario_return:.2%}; "
        f"estimated value after shock ${scenario_value:,.2f}."
    )
    st.session_state["investment_style"] = investment_style
    st.session_state["optimisation_approach"] = params["model_type"]
    st.session_state["scores"] = scores
    st.session_state["raptor_score"] = compute_raptor_score(scores)
    st.session_state["risk_label"] = risk_label(m["Annual volatility"], m["Max drawdown"])
    st.session_state["validation_report"] = validation_report
    st.session_state["scenario_library_results"] = scenario_library_results
    st.session_state["model_comparison"] = model_comparison
    st.session_state["benchmark_comparison"] = benchmark_comparison
    st.session_state["ai_confidence_score"] = compute_ai_confidence_score(scores, model_comparison, benchmark_comparison, validation_report)
    st.session_state["recommended_model"] = model_comparison.iloc[0]["Business option"] if len(model_comparison) else "Not available"
    st.session_state["recommended_benchmark"] = benchmark_comparison.iloc[0]["Portfolio"] if len(benchmark_comparison) else "Not available"
    st.session_state["model_formula_description"] = optimisation_formula_description(params["model_type"])
    st.session_state["analyst_mode"] = analyst_mode
    st.session_state["asset_diagnostics"] = diagnostics
    st.session_state["drawdown_series"] = drawdown_series
    st.session_state["port_ret"] = port_ret
    st.session_state["scenario_name"] = active_scenario_name
    st.session_state["predefined_scenario_name"] = scenario_name
    st.session_state["scenario_source"] = active_scenario_source
    st.session_state["active_scenario_vector"] = active_scenario
    st.session_state["params_snapshot"] = params.copy()
    st.session_state["group_bounds_used"] = active_bounds
    st.session_state["config_signature"] = current_config_signature

if run_button:
    existing_live = st.session_state.get("live_df")
    compute_and_store(existing_live)
elif st.session_state.get("has_results", False) and st.session_state.get("config_signature") != current_config_signature:
    st.info("Inputs changed. RAPOR-LLM is re-optimising so all outputs remain linked to the current sidebar settings.")
    existing_live = st.session_state.get("live_df")
    compute_and_store(existing_live)
    st.rerun()

if not st.session_state.get("has_results", False):
    st.markdown(
        """
<div class="card-blue">
<b>Start here:</b> configure your budget, objective, scenario, ETF universe, and copilot settings in the sidebar, then click <b>Run RAPOR optimisation</b>.
After results appear, you can enter live market moves, compare strategies, review benchmarks, and ask the financial copilot for an interpretation.
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()

# ============================================================
# Results
# ============================================================

m = st.session_state["metrics"]
allocation = st.session_state["allocation"]
group_alloc = st.session_state["group_alloc"]
execution = st.session_state["execution"]
cash_left = st.session_state["cash_left"]
wealth = st.session_state["wealth"]
corr = st.session_state["corr"]
valid = st.session_state["valid"]
weights = st.session_state["weights"]
live_df = st.session_state["live_df"]
scenario_contrib = st.session_state["scenario_contrib"]
scores = st.session_state["scores"]
raptor_score = st.session_state.get("raptor_score", 0)
risk_level = st.session_state.get("risk_label", "Not available")
ai_confidence_score = st.session_state.get("ai_confidence_score", 0)
asset_diag = st.session_state["asset_diagnostics"]
drawdown_series = st.session_state["drawdown_series"]
port_ret = st.session_state["port_ret"]
validation_report = st.session_state["validation_report"]
scenario_library_results = st.session_state["scenario_library_results"]
model_comparison = st.session_state["model_comparison"]
benchmark_comparison = st.session_state["benchmark_comparison"]
recommended_model = st.session_state["recommended_model"]
recommended_benchmark = st.session_state["recommended_benchmark"]
model_formula_description = st.session_state["model_formula_description"]
analyst_mode_current = st.session_state.get("analyst_mode", "Integrated decision-support system analyst")

st.markdown(
    f"""
<div class="card-green">
<b>Optimisation completed.</b><br>
Objective: <b>{st.session_state["investment_style"]}</b> |
Approach: <b>{st.session_state["optimisation_approach"]}</b> |
Scenario: <b>{st.session_state["scenario_name"]}</b>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="card-blue">
<b>Recommended strategy:</b> {recommended_model}<br>
<b>Best benchmark reference:</b> {recommended_benchmark}<br>
<span class="small-note">The recommendation reflects your selected objective, market scenario, live inputs, risk metrics, trade feasibility, strategy comparison, and benchmark review.</span>
</div>
""",
    unsafe_allow_html=True,
)


st.markdown(
    f"""
<div class="hero-box">
  <h1>RAPOR Resilience Score: {raptor_score:.0f}/100</h1>
  <p>Risk level: <b>{risk_level}</b> · Confidence level: <b>{ai_confidence_score:.0f}/100</b> · Recommended model: <b>{recommended_model}</b> · Benchmark leader: <b>{recommended_benchmark}</b></p>
</div>
""",
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Expected return", f"{m['Expected annual return']:.2%}")
k2.metric("Volatility", f"{m['Annual volatility']:.2%}")
k3.metric("CVaR 95%", f"{m['Daily CVaR 95%']:.2%}")
k4.metric("Max drawdown", f"{m['Max drawdown']:.2%}")
k5.metric("Scenario result", f"{st.session_state['scenario_return']:.2%}")
k6.metric("Confidence level", f"{ai_confidence_score:.0f}/100")

g1, g2, g3, g4 = st.columns(4)
with g1:
    st.plotly_chart(make_gauge("Risk control", scores["Risk control score"]), use_container_width=True)
with g2:
    st.plotly_chart(make_gauge("Stress-test resilience", scores["Stress-test resilience score"]), use_container_width=True)
with g3:
    st.plotly_chart(make_gauge("Diversification", scores["Diversification score"]), use_container_width=True)
with g4:
    st.plotly_chart(make_gauge("Trade feasibility", scores["Trade feasibility score"]), use_container_width=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Portfolio",
    "Scenarios",
    "Scenario Details",
    "Trading Plan",
    "Portfolio Quality Review",
    "Strategy Comparison",
    "Benchmarks",
    "Financial Copilot",
])

with tab1:
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Target allocation")
        st.dataframe(
            allocation.style.format({
                "Latest Price": "${:,.2f}",
                "Target Weight": "{:.2%}",
                "Target AUD from New Budget": "${:,.2f}",
            }),
            use_container_width=True,
            height=360,
        )
    with right:
        st.plotly_chart(px.pie(allocation, names="Ticker", values="Target Weight", title="Target ETF weights"), use_container_width=True)

    st.subheader("Asset-class allocation")
    st.dataframe(group_alloc.style.format({"Target Weight": "{:.2%}"}), use_container_width=True, height=260)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        fig_group = px.bar(group_alloc, x="Group", y="Target Weight", title="Allocation by asset class", text_auto=".1%")
        fig_group.update_layout(height=420)
        st.plotly_chart(fig_group, use_container_width=True)
    with col_b:
        fig_tree = px.treemap(allocation, path=["Group", "Ticker"], values="Target Weight", title="Portfolio exposure map")
        fig_tree.update_layout(height=420)
        st.plotly_chart(fig_tree, use_container_width=True)

    st.subheader("Asset risk-return diagnostics")
    st.dataframe(
        asset_diag[["Ticker", "Group", "Target Weight", "Asset Expected Return", "Asset Volatility", "Risk Contribution", "Return Contribution"]].style.format({
            "Target Weight": "{:.2%}",
            "Asset Expected Return": "{:.2%}",
            "Asset Volatility": "{:.2%}",
            "Risk Contribution": "{:.2%}",
            "Return Contribution": "{:.2%}",
        }),
        use_container_width=True,
        height=360,
    )
    fig_scatter = px.scatter(
        asset_diag,
        x="Asset Volatility",
        y="Asset Expected Return",
        size="Target Weight",
        color="Group",
        hover_name="Ticker",
        title="Risk-return map sized by target allocation",
    )
    fig_scatter.update_layout(height=520)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Backtest, drawdown and correlation")
    st.plotly_chart(px.line(wealth, title="Backtested growth of $1"), use_container_width=True)
    fig_dd = px.area(drawdown_series, title="Historical portfolio drawdown")
    fig_dd.update_layout(height=360)
    st.plotly_chart(fig_dd, use_container_width=True)
    st.plotly_chart(px.imshow(corr, text_auto=".2f", aspect="auto", title="Historical return correlation"), use_container_width=True)

with tab2:
    st.subheader("Scenario and live-market inputs")
    st.markdown(
        """
<div class="card-blue">
Enter current moves from your broker or market website. Example: GOLD up 1.2% → enter <b>1.2</b>. VGS down 0.8% → enter <b>-0.8</b>.
After editing, click the button below to re-run the optimiser using these live inputs.
</div>
""",
        unsafe_allow_html=True,
    )

    edited_live = st.data_editor(
        live_df[["Ticker", "Latest Price", "Manual Market Move %"]],
        use_container_width=True,
        height=360,
        num_rows="fixed",
        key="live_editor_v15",
    )
    edited_live = add_adjusted_prices(edited_live)

    st.dataframe(
        edited_live[["Ticker", "Latest Price", "Manual Market Move %", "Adjusted Price"]].style.format({
            "Latest Price": "${:,.2f}",
            "Manual Market Move %": "{:.2f}%",
            "Adjusted Price": "${:,.2f}",
        }),
        use_container_width=True,
        height=300,
    )

    st.plotly_chart(px.bar(edited_live, x="Ticker", y="Manual Market Move %", title="Manual live-market moves"), use_container_width=True)

    if st.button("Re-run optimisation using edited live inputs", type="primary"):
        compute_and_store(edited_live)
        st.success("Re-optimised using edited live-market moves. Open the Scenario impact or Analyst tab to see updated results.")
        st.rerun()

with tab3:
    st.subheader("Scenario and live-market impact")
    c1, c2, c3 = st.columns(3)
    c1.metric("Combined scenario/live result", f"{st.session_state['scenario_return']:.2%}")
    c2.metric("Estimated value after shock", f"${st.session_state['scenario_value']:,.2f}")
    c3.metric("Scenario selected", st.session_state["scenario_name"])

    st.markdown(f"<div class='card-blue'>{st.session_state['scenario_summary']}</div>", unsafe_allow_html=True)

    st.dataframe(
        scenario_contrib.style.format({
            "Target Weight": "{:.2%}",
            "Scenario Return": "{:.2%}",
            "Live Market Move": "{:.2%}",
            "Combined Shock": "{:.2%}",
            "Contribution": "{:.2%}",
        }),
        use_container_width=True,
        height=360,
    )
    fig_contrib = px.bar(scenario_contrib, x="Ticker", y="Contribution", title="Contribution to scenario/live result", text_auto=".2%")
    fig_contrib.update_layout(height=460)
    st.plotly_chart(fig_contrib, use_container_width=True)

    sorted_contrib = scenario_contrib.sort_values("Contribution")
    fig_waterfall = go.Figure(go.Waterfall(
        x=sorted_contrib["Ticker"],
        y=sorted_contrib["Contribution"],
        measure=["relative"] * len(sorted_contrib),
        text=[f"{v:.2%}" for v in sorted_contrib["Contribution"]],
        textposition="outside",
    ))
    fig_waterfall.update_layout(title="Waterfall view of scenario contribution", height=460)
    st.plotly_chart(fig_waterfall, use_container_width=True)

with tab4:
    st.subheader("Trading plan")
    st.dataframe(
        execution.style.format({
            "Latest Price": "${:,.2f}",
            "Target Weight": "{:.2%}",
            "Target AUD": "${:,.2f}",
            "Order Value": "${:,.2f}",
            "Brokerage Fee": "${:,.2f}",
            "Actual Weight": "{:.2%}",
            "Gap vs Target": "{:.2%}",
        }),
        use_container_width=True,
        height=420,
    )

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Order value", f"${execution['Order Value'].sum():,.2f}")
    e2.metric("Brokerage fees", f"${execution['Brokerage Fee'].sum():,.2f}")
    e3.metric("Cash left", f"${cash_left:,.2f}")
    e4.metric("Assets purchased", f"{int((execution['Units to Buy'] > 0).sum())}/{len(execution)}")

    if execution["Brokerage Fee"].sum() / max(capital, 1e-9) > 0.02:
        st.markdown(
            "<div class='card-orange'>Brokerage fees exceed 2% of the budget. This allocation may be too fragmented for the current capital.</div>",
            unsafe_allow_html=True,
        )


with tab5:
    st.subheader("Portfolio Quality Review and formulation check")
    st.markdown(
        f"""
<div class="card-blue">
<b>Selected formulation:</b> {st.session_state["optimisation_approach"]}<br>
<span class="small-note">{model_formula_description}</span>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Mathematical feasibility checks")
    st.dataframe(validation_report, use_container_width=True, height=280)

    st.markdown("#### Portfolio performance across full scenario library")
    st.dataframe(
        scenario_library_results.style.format({"Portfolio Return": "{:.2%}"}),
        use_container_width=True,
        height=280,
    )
    fig_scen_lib = px.bar(
        scenario_library_results.sort_values("Portfolio Return"),
        x="Scenario",
        y="Portfolio Return",
        title="Portfolio return across all stress scenarios",
        text_auto=".2%",
    )
    fig_scen_lib.update_layout(height=440)
    st.plotly_chart(fig_scen_lib, use_container_width=True)

    st.markdown("""
#### Audit interpretation

- If any feasibility check fails, do not trust the allocation.
- If the selected scenario is acceptable but the worst scenario is poor, the portfolio is not robust across regimes.
- If guardrails are too strict, the optimiser may produce similar allocations across models.
- If scenario importance is too weak, scenario changes will not materially affect the result.
""")

with tab6:
    st.subheader("Strategy comparison")
    st.markdown(
        f"""
<div class="card-blue">
This section runs every optimisation approach using the same ETF universe, scenario, live-market inputs, constraints, fees, and budget.
The recommended model for the current business objective is: <b>{recommended_model}</b>.<br>
<span class="small-note">Scores are relative to the feasible models in this run, so charts remain meaningful even when absolute risk penalties are large.</span>
</div>
""",
        unsafe_allow_html=True,
    )

    st.dataframe(
        model_comparison.style.format({
            "Expected annual return": "{:.2%}",
            "Annual volatility": "{:.2%}",
            "Daily CVaR 95%": "{:.2%}",
            "Max drawdown": "{:.2%}",
            "Selected scenario return": "{:.2%}",
            "Worst scenario return": "{:.2%}",
            "Effective holdings": "{:.2f}",
            "Brokerage fee ratio": "{:.2%}",
            "Cash left": "${:,.2f}",
            "Strategy score": "{:.1f}",
        }),
        use_container_width=True,
        height=520,
    )

    feasible_models = model_comparison[model_comparison["Feasible"] == True].copy()

    if feasible_models.empty:
        st.error("No feasible comparison models were produced. Relax guardrails, reduce minimum allocation, or reduce the number of selected ETFs.")
        if "Error" in model_comparison.columns:
            st.dataframe(model_comparison[["Business option", "Model code", "Feasible", "Error"]], use_container_width=True)
    else:
        feasible_models["Plot size"] = feasible_models["Strategy score"].clip(lower=8)

        fig_rank = px.bar(
            feasible_models.sort_values("Strategy score"),
            x="Strategy score",
            y="Business option",
            orientation="h",
            title="Model ranking by business-alignment score",
            text="Strategy score",
        )
        fig_rank.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_rank.update_layout(height=560, xaxis_range=[0, 105], margin=dict(l=20, r=80, t=60, b=40))
        st.plotly_chart(fig_rank, use_container_width=True)

        scatter = px.scatter(
            feasible_models,
            x="Annual volatility",
            y="Expected annual return",
            size="Plot size",
            color="Business option",
            hover_name="Business option",
            hover_data={
                "Strategy score": ":.1f",
                "Selected scenario return": ":.2%",
                "Worst scenario return": ":.2%",
                "Max drawdown": ":.2%",
                "Daily CVaR 95%": ":.2%",
                "Plot size": False,
            },
            title="Return-risk map of all feasible optimisation models",
        )
        scatter.update_traces(marker=dict(opacity=0.82, line=dict(width=1)))
        scatter.update_layout(height=560, margin=dict(l=20, r=20, t=60, b=40))
        st.plotly_chart(scatter, use_container_width=True)

        fig_worst = px.bar(
            feasible_models.sort_values("Worst scenario return"),
            x="Business option",
            y="Worst scenario return",
            title="Worst-scenario performance by feasible model",
            text="Worst scenario return",
        )
        fig_worst.update_traces(texttemplate="%{text:.2%}", textposition="outside")
        fig_worst.update_layout(height=500, margin=dict(l=20, r=20, t=60, b=120), xaxis_tickangle=-30)
        st.plotly_chart(fig_worst, use_container_width=True)

        if "Error" in model_comparison.columns and (~model_comparison["Feasible"]).any():
            with st.expander("Show infeasible model errors"):
                st.dataframe(
                    model_comparison.loc[~model_comparison["Feasible"], ["Business option", "Model code", "Error"]],
                    use_container_width=True,
                )



with tab7:
    st.subheader("Benchmark comparison")
    st.markdown(
        f"""
<div class="card-blue">
This section compares the selected RAPOR portfolio against simple, interpretable benchmark strategies.
The current benchmark leader is: <b>{recommended_benchmark}</b>.
</div>
""",
        unsafe_allow_html=True,
    )

    st.dataframe(
        benchmark_comparison.style.format({
            "Expected annual return": "{:.2%}",
            "Annual volatility": "{:.2%}",
            "Daily CVaR 95%": "{:.2%}",
            "Max drawdown": "{:.2%}",
            "Selected scenario return": "{:.2%}",
            "Worst scenario return": "{:.2%}",
            "Effective holdings": "{:.2f}",
            "Brokerage fee ratio": "{:.2%}",
            "Cash left": "${:,.2f}",
            "Strategy score": "{:.1f}",
        }),
        use_container_width=True,
        height=420,
    )

    fig_bench_score = px.bar(
        benchmark_comparison.sort_values("Strategy score"),
        x="Strategy score",
        y="Portfolio",
        orientation="h",
        title="Benchmark ranking by business-alignment score",
        text="Strategy score",
    )
    fig_bench_score.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_bench_score.update_layout(height=420, xaxis_range=[0, 105], margin=dict(l=20, r=80, t=60, b=40))
    st.plotly_chart(fig_bench_score, use_container_width=True)

    fig_bench_scatter = px.scatter(
        benchmark_comparison,
        x="Annual volatility",
        y="Expected annual return",
        size=benchmark_comparison["Strategy score"].clip(lower=8),
        color="Portfolio",
        hover_name="Portfolio",
        title="Benchmark return-risk map",
    )
    fig_bench_scatter.update_layout(height=500)
    st.plotly_chart(fig_bench_scatter, use_container_width=True)


with tab8:
    st.subheader("RAPOR Financial Copilot")
    context = {
        "metrics": m,
        "allocation": allocation,
        "group_alloc": group_alloc,
        "buy_plan": execution,
        "capital": capital,
        "cash_left": cash_left,
        "scenario_summary": st.session_state["scenario_summary"],
        "scenario_return": st.session_state["scenario_return"],
        "scenario_contrib": scenario_contrib,
        "investment_style": st.session_state["investment_style"],
        "optimisation_approach": st.session_state["optimisation_approach"],
        "scenario_name": st.session_state["scenario_name"],
        "predefined_scenario_name": st.session_state.get("predefined_scenario_name", ""),
        "scenario_source": st.session_state.get("scenario_source", ""),
        "live_df": st.session_state["live_df"],
        "validation_report": validation_report,
        "scenario_library_results": scenario_library_results,
        "model_comparison": model_comparison,
        "benchmark_comparison": benchmark_comparison,
        "recommended_model": recommended_model,
        "recommended_benchmark": recommended_benchmark,
        "model_formula_description": model_formula_description,
        "analyst_mode": analyst_mode_current,
        "ai_confidence_score": ai_confidence_score,
        "ai_provider": provider,
    }

    st.markdown(
        """
<div class="card-blue">
The analyst uses the selected scenario, manual market inputs, optimisation result, group allocation, buy plan, fees, and cash left.
If you change the scenario, objective, budget or ETF universe, RAPOR-LLM automatically refreshes the optimisation. If you edit live-market moves in the Scenarios tab, click the live-input re-run button.
</div>
""",
        unsafe_allow_html=True,
    )


    last_used = st.session_state.get("scenario_name", "Run RAPOR optimisation to initialise scenario")

    if last_used != scenario_name:
        status_note = (
            "The selected Scenario has changed. Click Run RAPOR optimisation before trusting "
            "the charts, model comparison, benchmark comparison, or copilot interpretation."
        )
    else:
        status_note = "The financial copilot will interpret this same selected Scenario."

    st.markdown(
        f"""
<div class="card-blue">
<b>Active Scenario:</b> {scenario_name}<br>
<span class="small-note">{status_note}</span>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.session_state.get("scenario_name") != scenario_name:
        st.warning(
            "The Scenario selected on the left has not yet been applied to the optimiser. "
            "Click Run RAPOR optimisation first; otherwise the copilot may interpret old results."
        )

    st.markdown("### AI tools")

    tool_col1, tool_col2 = st.columns(2)

    with tool_col1:
        st.markdown("#### Optional: enhance the selected Scenario with AI")
        st.caption(
            "This tool uses only the Scenario selected on the left. "
            "It does not use a separate scenario text box, so the copilot and optimiser remain consistent."
        )

        selected_scenario_for_ai = clean_scenario_label_for_ai(
            st.session_state.get("ai_base_scenario", scenario_name) if scenario_name.startswith("AI-generated:") else scenario_name
        )
        st.info(f"AI will generate shocks for the selected Scenario: {selected_scenario_for_ai}")

        if st.button("Generate / refresh AI scenario for selected Scenario", key="generate_ai_scenario"):
            if provider == "Rule-Based Analyst":
                st.warning("Select Gemini, Groq, OpenRouter, or OpenAI to generate AI scenarios. Rule-Based Analyst cannot invent new scenario shocks.")
            else:
                try:
                    scenario_instruction = (
                        f"The user selected this active scenario from the left dropdown: {selected_scenario_for_ai}. "
                        f"Generate ETF shocks that are strictly consistent with this selected scenario. "
                        f"Do not switch to a different geopolitical or macroeconomic event unless it is explicitly part of the selected scenario."
                    )
                    scen_prompt = make_ai_scenario_prompt(scenario_instruction, valid, allocation, group_alloc)
                    scen_text, scen_used = run_ai_provider(
                        provider,
                        scen_prompt,
                        openai_key=api_key,
                        openai_model=model,
                        gemini_key=gemini_api_key,
                        gemini_model=gemini_model,
                        groq_key=groq_api_key,
                        groq_model=groq_model,
                        openrouter_key=openrouter_api_key,
                        openrouter_model=openrouter_model,
                    )
                    scen_name, scen_logic, shocks, raw_json = parse_ai_scenario_json(scen_text, valid)

                    if selected_scenario_for_ai.lower() not in scen_name.lower():
                        scen_name = selected_scenario_for_ai + " - AI enhanced"

                    ai_scenario_df = pd.DataFrame({
                        "Ticker": valid,
                        "AI Scenario Shock": shocks,
                        "Contribution using current weights": weights * shocks,
                    })
                    st.session_state["ai_scenario_df"] = ai_scenario_df
                    st.session_state["ai_scenario_name"] = scen_name
                    st.session_state["ai_scenario_logic"] = scen_logic
                    st.session_state["ai_scenario_vector"] = shocks
                    st.session_state["ai_base_scenario"] = selected_scenario_for_ai
                    ai_option = "AI-generated: " + scen_name
                    st.session_state["pending_ai_scenario_option"] = ai_option
                    st.success(f"Generated scenario using {scen_used}: {scen_name}")
                    st.info("The AI-enhanced version of the selected Scenario will be added to the left Scenario dropdown and selected after refresh.")
                    st.rerun()
                except Exception as e:
                    st.error(f"AI scenario generation failed: {e}")

        # Display active AI scenario details only when the left Scenario dropdown selects an AI-generated scenario.
        if scenario_name.startswith("AI-generated:") and "ai_scenario_df" in st.session_state:
            st.markdown(f"**Active AI scenario:** {st.session_state.get('ai_scenario_name', clean_scenario_label_for_ai(scenario_name))}")
            st.caption(st.session_state.get("ai_scenario_logic", ""))
            st.dataframe(
                st.session_state["ai_scenario_df"].style.format({
                    "AI Scenario Shock": "{:.2%}",
                    "Contribution using current weights": "{:.2%}",
                }),
                use_container_width=True,
                height=280,
            )
            fig_ai_scen = px.bar(
                st.session_state["ai_scenario_df"].sort_values("Contribution using current weights"),
                x="Ticker",
                y="Contribution using current weights",
                title="Active AI scenario contribution",
                text_auto=".2%",
            )
            st.plotly_chart(fig_ai_scen, use_container_width=True)

    with tool_col2:
        st.markdown("#### Rebalancing Advisor")
        st.caption("Uses target weights, execution gaps, benchmark comparison, and scenario results.")
        if st.button("Generate rebalancing guidance", key="rebalance_guidance"):
            rebalance_prompt = make_prompt(
                context,
                "Focus only on rebalancing guidance. Explain overweight/underweight exposures, execution problems, scenario vulnerabilities, and practical next tests for a small-budget ETF portfolio. Do not give personal financial advice."
            )
            try:
                if provider == "Rule-Based Analyst":
                    guidance = rule_based_analysis(context)
                    used = "Rule-Based Analyst"
                else:
                    guidance, used = run_ai_provider(
                        provider,
                        rebalance_prompt,
                        openai_key=api_key,
                        openai_model=model,
                        gemini_key=gemini_api_key,
                        gemini_model=gemini_model,
                        groq_key=groq_api_key,
                        groq_model=groq_model,
                        openrouter_key=openrouter_api_key,
                        openrouter_model=openrouter_model,
                    )
                st.session_state["rebalance_guidance"] = str(guidance)
                st.session_state["rebalance_used"] = str(used)
            except Exception as e:
                st.error(f"Rebalancing guidance failed: {e}")

        if isinstance(st.session_state.get("rebalance_guidance"), str) and st.session_state.get("rebalance_guidance").strip():
            st.success("Generated by: " + str(st.session_state.get("rebalance_used", "Rule-Based Analyst")))
            st.markdown(st.session_state["rebalance_guidance"])

    st.markdown("---")

    if st.button("Ask the Financial Copilot", type="primary"):
        with st.spinner(f"Generating RAPOR AI analysis using {provider}..."):
            try:
                if provider == "Rule-Based Analyst":
                    answer = rule_based_analysis(context)
                    used = "Rule-Based Analyst"
                else:
                    answer, used = run_ai_provider(
                        provider,
                        make_prompt(context, question),
                        openai_key=api_key,
                        openai_model=model,
                        gemini_key=gemini_api_key,
                        gemini_model=gemini_model,
                        groq_key=groq_api_key,
                        groq_model=groq_model,
                        openrouter_key=openrouter_api_key,
                        openrouter_model=openrouter_model,
                    )
            except Exception as e:
                st.error(f"{provider} failed. Using Rule-Based Analyst. Error: {e}")
                answer = rule_based_analysis(context)
                used = "Rule-Based Analyst fallback"

            st.session_state["analysis_answer"] = answer
            st.session_state["analysis_used"] = used

    if "analysis_answer" in st.session_state:
        st.success("Generated by: " + st.session_state.get("analysis_used", "Unknown"))
        st.markdown(st.session_state["analysis_answer"])

with st.expander("How RAPOR-LLM calculates your portfolio"):
    st.markdown("""
RAPOR-LLM uses historical daily ETF returns to estimate geometric annualised return, annualised volatility, daily CVaR at 95%, maximum drawdown, correlations, and portfolio backtest paths.

The optimiser is long-only and normalises weights to 100%. Depending on the selected objective, it penalises volatility, CVaR, drawdown, concentration, turnover, tax drag, selected-scenario loss, and worst-case scenario loss. Scenario shocks enter both the expected-return tilt and the downside penalty. Practical trading plans then convert continuous target weights into executable whole-unit or fractional orders using latest adjusted prices, brokerage, and minimum-order constraints.

These calculations are intended for decision support and education. Historical prices, scenario shocks and LLM-generated interpretations are not forecasts. The app can keep calculations internally consistent, but it cannot guarantee future investment outcomes or personal suitability.
""")

with st.expander("Optional AI provider setup"):
    st.markdown("""
### Recommended provider: Gemini

For low-cost AI-assisted explanations, start with **Gemini** from Google AI Studio.

Suggested settings:
- Copilot engine: `Gemini`
- Model: `gemini-2.5-flash-lite`
- Environment variable option: `GEMINI_API_KEY`

Other optional providers:
- **Groq** for very fast hosted responses.
- **OpenRouter** for access to many hosted free/low-cost models.
- **Rule-Based Analyst** when no API key is available.

If an external provider fails, RAPOR-LLM falls back to the rule-based analyst.
""")


with st.expander("About RAPOR-LLM"):
    st.markdown("""
**RAPOR-LLM** is an AI-powered ETF portfolio decision-support tool.

It combines ETF market data, scenario stress testing, portfolio optimisation, practical trading constraints, benchmark comparison, and AI-assisted explanations in one dashboard.

Use it to explore possible portfolio allocations and understand trade-offs between risk, diversification, resilience, and implementation practicality. It is not personal financial advice and does not guarantee future performance.
""")


st.markdown("---")
st.caption(
    "RAPOR-LLM is provided for educational and decision-support purposes only. "
    "ETF prices and historical returns may be delayed, incomplete, or affected by external data-provider availability. "
    "Always verify product details, fees, tax implications, and suitability before making any investment decision."
)
