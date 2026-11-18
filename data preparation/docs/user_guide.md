# Dashboard User Guide

## Start
1. Install the dependencies listed in `requirements.txt`.
2. Run `streamlit run app/streamlit_app.py` from the repository's `data preparation/` directory.
3. Confirm the transaction CSV path in the sidebar.
4. Review the data-validation summary before interpreting any charts.

## Controls
- **Date range:** limits rows to the selected dates.
- **Markets / Products:** select the units included in the descriptive analysis.
- **Outcome:** switches the time-series chart between revenue, gross profit, units sold and price.
- **Download:** exports the filtered rows to CSV.

## Interpret carefully
- The dataset currently supplied is simulated and currency units are unspecified.
- Charts are descriptive associations, not proof of causality.
- A successful schema validation does not establish overlap, identification, model correctness, or causal validity.
- If the dashboard reports missing columns, invalid dates, or no matching rows, stop and investigate the data/path rather than bypassing the check.
