# Testing Plan — Harish

## Week 1: workflow and requirements
- Confirm repository layout, data grain and owners.
- Record expected input columns and outputs for each module.
- Create initial checklist and list unknowns.

## Week 2: data and model checks
- Test missing file, missing required columns, invalid dates and duplicate market-product-date keys.
- Check binary treatment/group flags and negative numeric values.
- Confirm data issues are reported, not silently discarded.
- Track each issue with steps to reproduce, expected vs actual result, owner and status.

## Week 3: integration and dashboard
- Test filters for dates, markets and products.
- Test empty filter selection and missing/invalid CSV path.
- Verify displayed units and simulated-data warning.
- Verify dashboard does not imply that descriptive charts are causal effects.
- Coordinate model output schemas with Aniket and Shrusti.

## Week 4: reproducibility and final handover
- Run setup instructions from a fresh environment if feasible and record the result.
- Run unit tests and record exact passed/failed/not-run status.
- Check README, architecture, known limitations and run commands against current code.
- Review every chart/table for source traceability and clear labels.
- Prepare a demo checklist and unresolved issue list.

## Evidence table

| Test | Expected | Actual result | Status | Evidence / issue ID |
|---|---|---|---|---|
| Load valid CSV | DataFrame loads | Fill after run | Not run | |
| Missing file | Clear error | Fill after run | Not run | |
| Missing required columns | Clear schema error | Fill after run | Not run | |
| Invalid dates | Validation fails | Fill after run | Not run | |
| Duplicate panel key | Duplicate check fails | Fill after run | Not run | |
| Empty dashboard filter | Helpful message | Fill after run | Not run | |
| Filtered CSV download | File downloads | Fill after run | Not run | |
