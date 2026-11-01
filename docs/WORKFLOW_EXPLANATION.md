> Update — 2026-11-01: Copilot Chat is now working. The requested prompt was submitted and the actual response is saved in [COPILOT_RESPONSE.md](COPILOT_RESPONSE.md). Earlier setup-blocker notes below are historical. The lab2 tag is now published.

# Line-by-line CI workflow explanation

Historical Lab 2 file: [ci.yml at the corrected checkpoint](https://github.com/Aryan-17159/smartci/blob/1fe7eb508b173511bed9f502c5fdbb534918ac31/.github/workflows/ci.yml). The current assignment workflow has additional steps.

This is an independently written explanation, not a response attributed to
Copilot. Copilot Chat was opened, but GitHub displayed "Setting up your Copilot
license" and its welcome dialog failed to save. See the evidence in
[the lab report](LAB_REPORT.md).

## Explanation

YAML indentation defines which settings belong to each job, step, and action.
Blank lines only separate sections and have no execution effect.

- **Line 1: `name: CI`** — Sets the workflow name shown in the Actions tab to CI.

- **Line 3: `on: [push, pull_request]`** — Triggers CI for pushes and pull-request events such as opening or updating a pull request.

- **Line 5: `permissions:`** — Starts the permissions configuration for the temporary GITHUB_TOKEN.

- **Line 6: `contents: read`** — Allows reading repository contents. Other configurable token permissions are not granted.

- **Line 8: `jobs:`** — Starts the collection of jobs in this workflow.

- **Line 9: `build:`** — Defines the job identifier build. This is the job opened to inspect the test failure.

- **Line 10: `runs-on: ubuntu-latest`** — Uses a fresh GitHub-hosted Ubuntu runner. The exact image behind ubuntu-latest can change over time.

- **Line 11: `timeout-minutes: 10`** — Stops this job if it exceeds 10 minutes, bounding accidental hangs.

- **Line 12: `steps:`** — Starts the ordered sequence of actions and shell commands in the job.

- **Line 13: `- name: Check out repository`** — Names the first step Check out repository in the job log.

- **Line 14: `uses: actions/checkout@v4`** — Runs version 4 of the checkout action to download repository files.

- **Line 15: `with:`** — Introduces inputs for the checkout action.

- **Line 16: `fetch-depth: 0`** — Fetches full Git history, including branches and tags, instead of a shallow checkout.

- **Line 18: `- name: Set up Python 3.12`** — Names the step that selects Python.

- **Line 19: `uses: actions/setup-python@v5`** — Runs version 5 of the setup-python action. This version is separate from the Python version.

- **Line 20: `with:`** — Introduces inputs for setup-python.

- **Line 21: `python-version: '3.12'`** — Selects a Python 3.12 interpreter and makes it available to later steps.

- **Line 23: `- name: Install dependencies`** — Names the dependency-installation step; its displayed baseline duration was 5 seconds.

- **Line 24: `run: python -m pip install -r requirements.txt`** — Uses the selected Python interpreter to run pip and install requirements.txt.

- **Line 26: `- name: Run tests`** — Names the test step. This is the step that becomes red during the intentional failure.

- **Line 27: `shell: bash`** — Explicitly selects Bash for the following shell commands.

- **Line 28: `run: |`** — The vertical bar starts a YAML multiline literal containing shell commands.

- **Line 29: `set -o pipefail`** — Makes a pipeline fail if an earlier command fails; a successful tee cannot hide a failing pytest process.

- **Line 30: `python -m pytest -v --junitxml=test-results.xml 2>&1 | tee build.log`** — Runs pytest verbosely; writes JUnit XML; merges stderr into stdout with 2>&1; pipes output to tee, which displays it and saves build.log.

- **Line 32: `- name: Upload test logs`** — Names the step that preserves test evidence as an Actions artifact.

- **Line 33: `if: always()`** — Evaluates the always() expression so log upload is attempted even after an earlier step fails. It does not erase or ignore the test failure.

- **Line 34: `uses: actions/upload-artifact@v4`** — Runs version 4 of the upload-artifact action.

- **Line 35: `with:`** — Introduces inputs for the artifact upload action.

- **Line 36: `name: test-results-${{ github.run_id }}-${{ github.run_attempt }}`** — Builds a distinct artifact name from the workflow run ID and retry attempt number.

- **Line 37: `path: |`** — Starts a multiline list of files to upload.

- **Line 38: `build.log`** — Includes the human-readable combined test output.

- **Line 39: `test-results.xml`** — Includes the machine-readable JUnit XML results.

- **Line 40: `if-no-files-found: ignore`** — Does not fail the upload step when no matching files exist, for example if installation failed before tests could run.

- **Line 41: `retention-days: 14`** — Requests that the artifact be retained for 14 days, subject to repository and organization policy.

## Why the red run happened

The test expected 101.0 after a 0% discount on 100. The correct result is 100.0.
Pytest raised AssertionError at tests/test_pricing.py:11 and exited with code 1.
Because pipefail is enabled, the Run tests step and build job failed despite tee
and the later artifact upload succeeding. Restoring the assertion to 100.0 made
all 28 tests pass. The red run demonstrates that the CI pipeline detects failed
assertions; the restored green run demonstrates recovery after a fix.

## Ready-to-send Copilot Chat prompt

Once your GitHub Copilot account setup is complete, submit the following prompt
with this workflow as context. The account-side blocker is the only reason a
Copilot-generated answer is not included.

> Explain each line of this workflow file. Explain YAML indentation, push and
> pull_request triggers, jobs and steps, the Ubuntu runner, checkout history,
> Python setup, dependencies, pipefail, stderr redirection, tee, JUnit XML,
> always(), artifact naming, and retention. Explain why changing the expected
> result of apply_discount(100, 0) from 100.0 to 101.0 causes a red run.

```yaml
name: CI

on: [push, pull_request]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: python -m pip install -r requirements.txt

      - name: Run tests
        shell: bash
        run: |
          set -o pipefail
          python -m pytest -v --junitxml=test-results.xml 2>&1 | tee build.log

      - name: Upload test logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ github.run_id }}-${{ github.run_attempt }}
          path: |
            build.log
            test-results.xml
          if-no-files-found: ignore
          retention-days: 14
```
