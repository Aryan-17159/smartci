# Assignment 4.3 — Dynamic Test-Subset Routing
## Objective and implementation
[select_tests.py](../scripts/select_tests.py) intersects changed source paths with each test's transitive static import dependencies. A changed test selects itself. Documentation-only changes select no subset tests. Unknown files, dependencies, configuration, package initializers, fixtures, deleted source, unavailable Git history and unsafe parsing trigger a full run.

## Steps and observed results
1. Complete [setup](ASSIGNMENTS.md).
2. Run `python -m scripts.select_tests --changed src/pricing.py --run`. Pricing and cart tests are selected.
3. Run `python -m scripts.select_tests --changed src/inventory.py --run`. Inventory tests are selected.
4. Run `python -m scripts.select_tests --changed tests/test_cart.py` to select only that changed test.
5. Run `python -m scripts.select_tests --changed docs/notes.md` to observe mode none.
6. Run `python -m scripts.select_tests --changed requirements.txt` to observe mode full.
7. For real commits, use `python -m scripts.select_tests --base HEAD~1 --head HEAD --merge-base --run`. Missing comparison history falls back to full.
8. Run `python -m scripts.demo_assignments` and inspect the [recorded routing results](evidence/assignments/routing-experiments.json).

## CI and learning
Actions checks out full history and supplies the event's comparison SHA as an environment variable. The script resolves commit objects, uses a NUL-separated Git diff, treats renames as deletion/addition and passes pytest arguments without a shell. Its JSON explains both selection and fallback reason.

Static import graphs cannot capture every runtime dependency. Dynamic imports and built-in eval/exec are rejected; external dependencies/configuration changes request all tests. The workflow always runs the full suite after subset selection as a correctness safety check, including when the selected test step fails. Thus this implementation demonstrates routing, not a measured reduction in total workflow time.

Tests exercise transitive selection, invalid paths, deleted modules, changed fixtures, documentation-only diffs and actual temporary Git histories. Learning: choose a smaller test set only with evidence; uncertainty should increase coverage.

