# SmartCI lab report

Source: the user-supplied `m4_0.pdf`, three pages covering Labs 0, 1, and 2.
Prepared on 14 October 2026.

## Lab 0: Setup and project folder

The project includes `src`, `tests`, `scripts`, `ml`, `infra`, `ansible`, and
`.github/workflows`. `.gitignore` excludes virtual environments, Python caches,
pytest caches, and generated CI logs. Empty folders are preserved with `.gitkeep`.

A fresh Python 3.12 virtual environment was used for local verification.
Installation and GitHub push commands are in the README. VS Code extension
installation, Copilot sign-in, and GitHub authentication are user-account setup
steps. An interactive Copilot session has not been recorded as completed.

## Lab 1: Application and tests

`apply_discount` checks that the percentage is in the inclusive range 0-100,
applies it, and rounds to two decimal places. `add_tax` applies 18% by default.
`Cart.total` sums unit price times quantity, applies the discount, and adds tax.
`Inventory` supports accumulating stock and removing available stock, raising
`ValueError` when insufficient stock is requested.

For the required cart example, two pens at 50 give a subtotal of 100.
A 10% discount gives 90. Adding 18% tax gives **106.20**.

There are 28 collected test cases:

- Pricing: 12 cases covering normal discounts, both boundaries, four invalid
  percentages, rounding, zero price, default tax, a custom rate, and zero tax.
- Cart: 8 cases covering discount, empty cart, quantity, multiple products,
  complete discount, invalid discount propagation, independent carts, and
  repeated totals without mutation.
- Inventory: 8 cases covering new stock, accumulated stock, partial and complete
  removal, insufficient stock without mutation, missing products, separate
  products, and independent inventory instances.

Local test evidence is provided in [evidence](evidence/README.md). The delivered
test file contains the correct assertion and the normal suite passes.

## Lab 2: Baseline CI pipeline

The workflow is `.github/workflows/ci.yml`:

1. `name: CI` gives the workflow its Actions-tab name.
2. `on: [push, pull_request]` runs it when commits are pushed or pull requests
   are opened or updated.
3. `permissions: contents: read` limits the workflow token to reading repository
   contents.
4. `jobs: build` defines a job that runs on a fresh `ubuntu-latest` runner.
5. `timeout-minutes: 10` bounds the job duration.
6. `actions/checkout@v4` checks out repository files; `fetch-depth: 0` downloads
   full history for later Git-diff exercises.
7. `actions/setup-python@v5` selects Python 3.12.
8. `python -m pip install -r requirements.txt` installs the listed dependencies.
9. `shell: bash` selects Bash for the test step. `set -o pipefail` makes the
   pipeline fail when pytest fails, even though `tee` successfully writes output.
10. `python -m pytest -v --junitxml=test-results.xml` runs the tests and records
    machine-readable results. `2>&1 | tee build.log` displays and saves output.
11. `if: always()` on the upload step preserves logs even after a failing test.
    Artifacts include the run ID and attempt number and are retained for 14 days.

### What is the use of a red run?

A red run means a workflow or job did not complete successfully. In this lab,
the intentionally wrong assertion demonstrates that CI actually detects a test
failure and propagates its nonzero exit status through the log pipeline. It
helps locate the failing behavior before a change is accepted. A failing required
status check can prevent merging when branch protection is configured; a red run
by itself does not automatically configure or enforce branch protection.

The demonstration replaces:

```python
assert apply_discount(100, 0) == 100.0
```

with:

```python
assert apply_discount(100, 0) == 101.0
```

The function correctly returns 100.0 because a 0% discount leaves 100 unchanged.
The failure is in the expected test value. Restore `100.0`; changing the function
to return 101.0 would make the application incorrect.

### Where does GitHub Actions show the error?

Go to **repository > Actions > CI > failed run > build > Run tests**.
The test log identifies `tests/test_pricing.py::test_discount_boundaries`, shows
the assertion mismatch `assert 100.0 == 101.0`, and ends with a failed-test summary
and a nonzero exit-code message. The failed step and job have red status icons.
The run summary's artifacts also provide `build.log` and `test-results.xml`.

### Actual verification status

- Local normal run: **28 passed**, process exit code 0.
- Local intentional failure: **1 failed, 27 passed**, process exit code 1.
- Local restored run: **28 passed**, process exit code 0.
- GitHub-hosted green and red runs: **pending the user's repository push**.
- GitHub timings and screenshots: **pending those live runs**.

The saved local output is real test output. It is not GitHub-hosted execution
evidence, and no GitHub screenshots or timing measurements have been invented.

## Complete after pushing

Use the README's red-run exercise, then replace the following pending fields
with values from your own repository:

- Repository URL: pending
- First green run URL: pending
- First green run total duration: pending
- Install dependencies step duration: pending
- Intentional red run URL: pending
- Restored green run URL: pending
- Screenshot files: pending; see [capture instructions](screenshots/README.md)

No baseline timing is claimed until it has been measured in GitHub Actions.

## References

- Supplied assignment: `m4_0.pdf`, pages 1-3.
- [Building and testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
- [Using workflow run logs](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs)
- [Checkout action](https://github.com/actions/checkout)
- [Setup Python action](https://github.com/actions/setup-python)
