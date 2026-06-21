# Model audit notes

Checked and updated in v26:

1. Annualised return now uses geometric annualisation from daily returns.
2. Weight bounds are adjusted to avoid infeasible optimisation when the selected ETF count conflicts with max-weight constraints.
3. AI-generated scenarios use the original selected base scenario for guardrail logic.
4. Practical buy-plan and comparisons use adjusted prices after manual live-market moves.
5. The Scenario dropdown remains the single source of truth for optimiser, charts, comparison tables, and copilot interpretation.
6. All outputs remain decision-support estimates, not forecasts or financial advice.
