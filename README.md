# RAPOR-LLM

# A Robust Adaptive Portfolio Optimization Framework with an LLM-Based Financial Copilot for Resilient ETF Portfolio Construction

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Overview

RAPOR-LLM is an AI-powered Decision Support System (DSS) for resilient ETF portfolio construction under market uncertainty.

The framework integrates:

- Portfolio optimization
- Risk and resilience analysis
- Scenario stress testing
- Benchmark comparison
- Live-market adjustments
- AI-assisted financial interpretation
- Interactive decision dashboards

Unlike traditional portfolio optimizers, RAPOR-LLM combines mathematical optimization with an LLM-based Financial Copilot to assist users in understanding, validating, and interpreting portfolio recommendations.

---

## Key Features

### Portfolio Optimization

- Multiple optimization strategies
- Business-objective-driven portfolio construction
- Budget and trading constraint handling
- Asset-class diversification rules
- Practical execution feasibility analysis

---

### Risk Analytics

- Expected annual return
- Annual volatility
- Conditional Value-at-Risk (CVaR)
- Maximum drawdown
- Portfolio resilience score
- Diversification assessment
- Execution quality assessment

---

### AI-Assisted Decision Support

- LLM Financial Copilot
- AI-generated scenario enhancement
- Portfolio auditing
- Benchmark comparison
- Investment committee review
- Risk interpretation
- Practical trading recommendations

Supported AI engines

- Rule-Based Financial Analyst
- Google Gemini
- OpenAI-compatible APIs (optional)

---

### Scenario Analysis

Stress-test portfolios under different market conditions including:

- Global recession
- High inflation
- Interest-rate shock
- Energy crisis
- Technology sell-off
- Commodity boom
- Financial crisis
- Bull market
- Custom AI-enhanced scenarios

---

### Interactive Dashboard

The Streamlit interface includes:

- Portfolio allocation
- ETF allocation charts
- Scenario analysis
- Trading plan
- Benchmark comparison
- Optimization model comparison
- Financial Copilot
- Portfolio audit

---

# System Architecture

```
                User
                  │
                  ▼
      Business Objective Selection
                  │
                  ▼
          Scenario Engine
                  │
                  ▼
      Portfolio Optimisation Engine
                  │
                  ▼
      Risk & Resilience Analytics
                  │
                  ▼
        Benchmark Comparison
                  │
                  ▼
         Trading Plan Generator
                  │
                  ▼
        LLM Financial Copilot
                  │
                  ▼
     Interactive Decision Dashboard
```

---

# Optimization Strategies

RAPOR-LLM supports multiple optimization objectives:

- Protect my capital
- Balanced resilient portfolio
- Maximum return per unit risk
- Equalise risk contribution
- Minimum volatility
- Downside protection (CVaR)
- Spread risk widely
- Growth with guardrails
- Robust across scenarios
- Scenario-focused optimization

Users can compare all optimization strategies simultaneously using the integrated model comparison module.

---

# Technologies

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- yFinance
- SciPy
- Google Gemini API (optional)
- OpenAI-compatible APIs (optional)

---

# Installation

Clone the repository

```bash
git clone https://github.com/imanrahimiy/rapor-llm-app.git
cd rapor-llm-app
```

Create a virtual environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run RAPOR-LLM

```bash
streamlit run app.py
```

---

# AI Configuration

The application works immediately using the built-in Rule-Based Financial Analyst.

No API key is required.

For AI-assisted explanations:

1. Obtain a Google Gemini API key

https://aistudio.google.com/

2. Select **Gemini** as the Copilot Engine

3. Enter your API key in the application sidebar

OpenAI-compatible APIs can also be configured.

---

# Live Demo

**Streamlit Application**

https://rapor-llm-app-9yt3r7nmjlzzeyuhxvzw7.streamlit.app

**Opt-Mining Website**

https://opt-mining.com.au/rapor-llm

---

# Repository

https://github.com/imanrahimiy/rapor-llm-app

---

# Example Workflow

1. Set investment budget
2. Select business objective
3. Choose a stress scenario
4. Select ETF universe
5. Run optimization
6. Review portfolio metrics
7. Compare optimization strategies
8. Evaluate benchmark performance
9. Generate AI-assisted interpretation
10. Export investment recommendations

---

# Research Contribution

RAPOR-LLM contributes an integrated AI-powered Decision Support System that combines:

- Portfolio optimization
- Risk management
- Scenario analysis
- Explainable AI
- LLM-assisted financial interpretation
- Interactive decision support

The framework demonstrates how mathematical optimization and Large Language Models can be integrated into a unified financial decision-support environment.

---

# Citation

If RAPOR-LLM contributes to your research, please cite:

> Rahimi, I. RAPOR-LLM: A Robust Adaptive Portfolio Optimization Framework with an LLM-Based Financial Copilot for Resilient ETF Portfolio Construction. GitHub Repository.

---


---

# Disclaimer

RAPOR-LLM is intended for research, educational, and decision-support purposes only.

The software provides optimization results based on historical market information, user-defined assumptions, and optimization models. Results should not be interpreted as financial advice or guarantees of future investment performance.

---

# Author

**Dr. Iman Rahimi**

Founder, Opt-Mining

Artificial Intelligence • Decision Support Systems • Mathematical Optimization • Financial Analytics

Website

https://opt-mining.com.au

GitHub

https://github.com/imanrahimiy

---

© 2026 Opt-Mining. All rights reserved.