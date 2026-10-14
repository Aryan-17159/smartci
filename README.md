# SmartCI

Completed source code for Labs 0-2 from the supplied `m4_0.pdf`: a small Python
shopping-cart application, pytest coverage, and a baseline GitHub Actions pipeline.

**Local validation:** 28 tests pass on Python 3.12. The deliberate failure exercise
produces 1 failed and 27 passed; restoring the assertion returns all 28 to passing.
Captured output is in [docs/evidence](docs/evidence).

The project is ready to push. GitHub run URLs, timings, and screenshots must be
collected from your repository after pushing; they are not included as completed
GitHub evidence. See the [lab report](docs/LAB_REPORT.md).

## 1. Run locally

Install Python 3.12, Git, and VS Code. Extract the ZIP and open the **smartci**
folder, the folder containing this README, in VS Code.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v
```

Using the environment's executable directly also works when PowerShell does not
allow activation scripts. To display `(.venv)` in your terminal when activation
is allowed, run `.\.venv\Scripts\Activate.ps1`.

macOS / Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
```

In VS Code, install the Python and GitHub Copilot extensions, sign in to Copilot,
then use **Python: Select Interpreter** to select `.venv`. You can ask Copilot to
explain the code or a failing assertion as described in the assignment.

Example (run from the project folder with the environment's Python):

```python
from src.cart import Cart

cart = Cart()
cart.add("pen", 50, 2)
print(cart.total(discount=10))  # 106.2
```

## 2. Push to GitHub

Create a new empty repository named **smartci** on GitHub. Do not initialize it
with a README, license, or .gitignore. Run the following inside the extracted
**smartci** folder, replacing `YOUR-USER` with your GitHub username:

```bash
git init
git branch -M main
git add .
git commit -m "Complete SmartCI Labs 0-2"
git remote add origin https://github.com/YOUR-USER/smartci.git
git push -u origin main
```

If Git asks for an identity, set your own `git config user.name` and
`git config user.email` in this repository, then retry the commit. Authenticate
with your own GitHub account when Git prompts.

If your instructor requires separate Lab 0 / Lab 1 / Lab 2 commits and the
`lab1` tag, use [the checkpoint commit guide](docs/CHECKPOINT_COMMITS.md)
**instead of** the quick commands above.

Open the repository's **Actions** tab and wait for **CI** to finish. The **build**
job should pass its **Run tests** step. Record the run URL, total duration, and
**Install dependencies** duration in [the lab report](docs/LAB_REPORT.md).

## 3. Complete the red-run exercise

Start with a clean working tree and a successful CI run. Use a temporary branch
so the exercise has a clear beginning and end. The commands below work in
PowerShell with the virtual environment created above:

```powershell
git switch -c lab2-red-run
.\.venv\Scripts\python.exe scripts/failure_demo.py enable
.\.venv\Scripts\python.exe -m pytest -v
```

The last command is **expected to fail**. It changes the boundary assertion's
expected value from `100.0` to `101.0`, exactly as requested by the PDF.

```bash
git add tests/test_pricing.py
git commit -m "Lab 2: demonstrate a failing assertion"
git push -u origin lab2-red-run
```

**Wait for this GitHub run to finish red before continuing.** Open
**Actions > CI > the failed run > build > Run tests**. Find
`test_discount_boundaries`, `assert 100.0 == 101.0`, and the exit-code failure.
Take the screenshots described in [docs/screenshots](docs/screenshots/README.md).

Restore the expected value, verify locally, and push the fix:

```powershell
.\.venv\Scripts\python.exe scripts/failure_demo.py disable
.\.venv\Scripts\python.exe -m pytest -v
git add tests/test_pricing.py
git commit -m "Lab 2: fix the expected discount value"
git push
```

Wait for the corrected run to finish green and capture its screenshot. Keep this
branch available as evidence. Return to your unchanged, passing main branch and
tag the completed lab:

```bash
git switch main
git tag -a lab2 -m "Lab 2: baseline CI and red-run exercise complete"
git push origin lab2
```

On macOS / Linux, use `python` instead of `.\.venv\Scripts\python.exe` after
activating `.venv`. The Git commands are the same on both platforms.

## Project files

```text
smartci/
  .github/workflows/ci.yml   Push and pull-request CI; downloadable test logs
  src/
    __init__.py
    pricing.py               Discounts and tax
    cart.py                  Cart totals; imports pricing.py
    inventory.py             Stock additions and removals
  tests/                     Pricing, cart, and inventory tests
  scripts/failure_demo.py    Enable or disable the Lab 2 assertion error
  ml/                        Reserved by Lab 0
  infra/                     Reserved by Lab 0
  ansible/                   Reserved by Lab 0
  docs/                      Lab report, evidence, and submission instructions
  requirements.txt
  pytest.ini
```

The supplied PDF ends at Lab 2. The three reserved folders contain `.gitkeep`
files so Git preserves them; later ML and infrastructure labs are outside this
document's scope. `requests` is retained because the assignment lists it, even
though these three modules do not make network requests.

The application follows the teaching reference's numeric behavior, including
Python's `round(..., 2)` and default 18% tax. Inputs are assumed to be numeric,
with nonnegative prices and positive integer quantities. Broader input
validation and decimal currency accounting are outside this lab's contract.

## CI notes

CI uses Python 3.12 on `ubuntu-latest`, downloads full Git history, installs
requirements, and runs the complete test suite. `set -o pipefail` propagates
pytest's failure through `tee`, while `2>&1` puts error output in `build.log`.
Test logs and JUnit XML are uploaded even after a test failure. No dependency
cache is configured, matching the lab's baseline timing exercise.

The workflow retains the assignment's `checkout@v4` and `setup-python@v5` action
versions. The extra artifact step makes failed-run logs easier to inspect.
See the official [Python CI guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
and [workflow log guide](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs)
for GitHub's workflow and log interfaces.
