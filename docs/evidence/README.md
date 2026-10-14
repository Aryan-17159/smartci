# Local verification evidence

These files record actual local runs on **14 October 2026**, using a fresh
environment with **Python 3.12.10**, **pytest 8.4.2**, and **requests 2.34.2**.
They do not represent runs on GitHub-hosted runners.

- [Normal run](local-green.txt): 28 passed, exit code 0.
- [Intentional error](local-red.txt): 1 failed and 27 passed, exit code 1.
- [Restored run](local-restored-green.txt): 28 passed, exit code 0.
- [Verification metadata](verification.json): environment versions and results.
- [Workflow validation](workflow-validation.txt): actionlint 1.7.12, exit code 0.

Tests ran on Windows through Git Bash with `set -o pipefail` and `tee`, verifying
that the test failure propagates through the same type of pipeline used by CI.
The GitHub workflow itself is configured for Ubuntu and still needs its first
remote run after pushing.

For portable, public evidence, absolute local paths in the pytest logs were
replaced with `<project>` or `<workspace>`. Assertion details, test statuses,
process exit codes, and pytest timings were preserved. These timings are local
measurements and must not be entered as GitHub Actions timing measurements.

The failure helper was enabled twice and disabled twice to check repeated use.
After restoration, `tests/test_pricing.py` was byte-for-byte identical to its
original passing version. The delivered project contains the correct assertion.

Actionlint checked workflow syntax, supported action inputs, expressions, and
step structure. Optional external ShellCheck and Pyflakes integrations were
disabled. Successful local checks do not substitute for GitHub execution or
screenshots; capture those using [the screenshot guide](../screenshots/README.md).
