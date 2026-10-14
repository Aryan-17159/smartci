# GitHub screenshot checklist

Capture these from your actual GitHub repository after following the README.
This directory initially contains instructions only; no live GitHub execution
has been claimed or illustrated with simulated screenshots.

1. **01-repository.png**: the repository Code tab, showing the project files and
   the `.github/workflows` folder.
2. **02-green-run.png**: a successful CI run summary with the repository name,
   run status, and total duration visible.
3. **03-install-duration.png**: the successful `build` job showing the
   **Install dependencies** step and its duration.
4. **04-red-run-error.png**: the failed `build` job with **Run tests** expanded.
   Include the failing test name, `assert 100.0 == 101.0`, and failed-test summary.
5. **05-fixed-green-run.png**: the successful run after restoring the assertion,
   with the **Run tests** output showing all tests passed.
6. **06-actions-history.png**: the Actions run list with the red and green runs
   visible together. Clear the branch filter if necessary.

On Windows, use **Win+Shift+S** to capture the relevant browser region and save
each PNG in this folder. On macOS use **Shift+Command+4**. Then add links/images
in `docs/LAB_REPORT.md`, for example:

```markdown
![Failed assertion shown in GitHub Actions](screenshots/04-red-run-error.png)
```

Add only image links for files you have actually saved. Copy each run's browser
URL into the report and record measured durations. Commit and push the report
and screenshots when ready.
