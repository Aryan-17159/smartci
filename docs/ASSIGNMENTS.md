# Assignments 4.2–4.5: submission and learning record
Repository: https://github.com/Aryan-17159/smartci

The assignment screenshots specify four topics and request implementation plus a step-by-step learning document. This project implements each topic in Python 3.12. The records below separate actual execution from simulated data.

## Setup
1. Clone the repository and enter its directory.
2. Run `python -m venv .venv` and activate it.
3. Run `python -m pip install -r requirements.lock`.
4. Run `python -m pytest -q`. Local verification on 2026-11-01: **62 passed**.
5. Read the four reports:
   - [4.2 Smart Build-Cache Invalidation](ASSIGNMENT_4_2.md)
   - [4.3 Dynamic Test-Subset Routing](ASSIGNMENT_4_3.md)
   - [4.4 LLM-Based Build/Error-Log Summarization](ASSIGNMENT_4_4.md)
   - [4.5 Build-Failure Prediction](ASSIGNMENT_4_5.md)

## CI integration
The [workflow](../.github/workflows/ci.yml) runs on pushes, pull requests and manual dispatch. It installs locked packages, restores build artifacts, validates module keys, routes tests, runs the full suite as a safety check, reproduces experiments, trains the educational predictor and uploads reports. The full suite remains enabled: subset selection is demonstrated without claiming end-to-end CI speed savings.

Automatic runs use explicitly labeled deterministic log extraction. A manual **Actions → CI → Run workflow** additionally downloads and runs the actual local language model on the recorded failed log. Model execution requires no API key. Local actual inference evidence is committed.

## Previous Lab 2 checkpoint
[Lab report and screenshots](LAB_REPORT.md) records the intentional 100.0 → 101.0 assertion failure and its correction. A red run proves the pipeline detects a regression and exits unsuccessfully. It identifies the failing test, actual/expected values and source line so a developer can fix it before merging.

- [Red run and exact error step](https://github.com/Aryan-17159/smartci/actions/runs/38528095257/job/115733143363#step:5:64): tests/test_pricing.py:11, actual 100.0 versus expected 101.0.
- [Restored green run](https://github.com/Aryan-17159/smartci/actions/runs/38528235235).
- [Actions history](https://github.com/Aryan-17159/smartci/actions).
- [Screenshots](screenshots/README.md).

These historical runs had 28 tests; the extended project has 62. The original [line-by-line explanation](WORKFLOW_EXPLANATION.md) describes the historical Lab 2 workflow, not the expanded assignment workflow. Copilot licensing previously prevented an actual Copilot response; that limitation is documented rather than presenting an independently written explanation as Copilot output.

