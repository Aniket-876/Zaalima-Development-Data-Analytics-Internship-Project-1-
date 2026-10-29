# Harish's Week 1–4 Plan

This plan maps Harish's proposed task-distribution responsibilities onto the project's four-week flow. Confirm dates and review milestones with the mentor; do not treat this plan as an official deadline.

## Week 1 — Understand the workflow and requirements
- Read the project objective, data dictionary, causal design and existing notebooks/scripts.
- Map data → causal design/Synthetic Control → DML → dashboard/report dependencies.
- Write an end-to-end checklist and capture expected input/output contracts.
- Deliver: workflow notes, owner/dependency list and open questions.

## Week 2 — Testing foundation and issue tracking
- Create a test plan for data loading, required columns, dates, duplicate keys and model output shape.
- Start a bug log with reproduction steps, expected/actual behavior, owner and status.
- Review existing scripts and note which checks have actually been run.
- Deliver: test checklist, bug-log template and initial verified test evidence.

## Week 3 — Dashboard support and module integration
- Build/run the Streamlit descriptive dashboard using the repository's cleaned transaction CSV.
- Add date/market/product filters, descriptive trend and scatter plots, market summary, data preview and CSV export.
- Clearly label simulated data and distinguish descriptive charts from causal estimates.
- Coordinate the expected Synthetic Control and DML output schemas with Shrusti and Aniket.
- Deliver: dashboard prototype, tests, integration contract and known limitations.

## Week 4 — Documentation, reproducibility and demo preparation
- Update setup/run instructions, architecture and user guide to match the actual repository.
- Attempt a fresh run; record environment, commands, pass/fail/not-run tests and errors.
- Prepare demo steps, final report outline, limitations and future improvements.
- Deliver: reproducibility evidence, updated documentation, test results and demo checklist.

## Definition of done
A deliverable is done only after it exists in the branch, the relevant command/test has actually been run where applicable, evidence is recorded, and the documentation matches the implementation. A planned feature is not a completed feature.
