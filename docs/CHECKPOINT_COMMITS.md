# Optional separate lab checkpoints

Use this guide only for a fresh extracted copy with no commits, **instead of**
the README's quick-push section. It creates distinct checkpoints from the
completed files, while keeping `lab1` on the app-and-tests commit.

Create an empty GitHub repository named `smartci`, then run these commands from
the local `smartci` folder. Replace `YOUR-USER` with your GitHub username.

## Lab 0

```bash
git init
git branch -M main
git add .gitignore .gitattributes src/__init__.py ml/.gitkeep infra/.gitkeep ansible/.gitkeep
git commit -m "Lab 0: project skeleton"
git remote add origin https://github.com/YOUR-USER/smartci.git
git push -u origin main
```

Git tracks files rather than empty directories; the other folders will appear
remotely when their files are committed in the following steps.

## Lab 1

First install dependencies and run the tests using the README's local setup
commands. After all 28 tests pass:

```bash
git add src tests requirements.txt pytest.ini
git commit -m "Lab 1: app and tests"
git tag -a lab1 -m "Lab 1: application and passing tests"
git push --follow-tags
```

This uses an **annotated** tag: `--follow-tags` pushes annotated tags, whereas a
lightweight `git tag lab1` needs an explicit `git push origin lab1`.

## Lab 2

```bash
git add .github scripts README.md docs
git commit -m "Lab 2: baseline CI and lab documentation"
git push
```

Wait for the green run, then follow the README's temporary-branch red-run exercise.
Create and push the annotated `lab2` tag after the red and corrected green runs
are complete. Add your screenshots and measured run details in a final commit:

```bash
git add docs
git commit -m "Document GitHub Actions run evidence"
git push
```
