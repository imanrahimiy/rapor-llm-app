# Robust Resilient ETF Portfolio Optimizer v4 + LLM

This version adds an optional LLM Portfolio Copilot to the v3 no-zero resilient optimizer.

## New
- Optional OpenAI LLM explanation panel
- Local fallback explanation when no API key is provided
- Sends only summary metrics/tables to the LLM
- LLM critiques resilience, practical buy constraints, CVaR/drawdown, gaps, fees, and scenario results

## Run
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## API key
Recommended local method:
```bash
set OPENAI_API_KEY=your_key_here
streamlit run app.py
```

Or paste the key into the sidebar field during a local run. Do not hard-code your key into the source code.

Educational decision-support only. Not financial advice.
