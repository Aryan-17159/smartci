"""Route changes to affected tests; uncertainty always selects the full suite."""
import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

from scripts.dependencies import UnsafeGraph, closure, import_graph


def select(root, changed, force_full=False):
    root = Path(root)
    tests = sorted(p.relative_to(root).as_posix() for p in (root/'tests').rglob('test_*.py'))
    def full(reason):
        return {'mode': 'full', 'reason': reason, 'changed': changed, 'tests': tests}
    if force_full or changed is None:
        return full('Full run requested or comparison base unavailable')
    if not tests:
        return full('No test files discovered; pytest will report a collection failure')
    normalized = []
    for path in changed:
        path = path.replace('\\', '/')
        pure = PurePosixPath(path)
        if pure.is_absolute() or '..' in pure.parts or ':' in path:
            return full('Unrecognized change path')
        normalized.append(path)
    changed = sorted(set(normalized))
    runnable = []
    for path in changed:
        if path.startswith('docs/') or path == 'README.md':
            continue
        if not path.startswith(('src/', 'tests/')) or not path.endswith('.py'):
            return full(f'Configuration, tooling, dependency, or unknown change: {path}')
        if not (root/path).is_file() or path.endswith(('__init__.py', 'conftest.py')):
            return full(f'Deletion, package initializer, or fixture change: {path}')
        runnable.append(path)
    if not runnable:
        return {'mode': 'none', 'reason': 'Documentation-only or empty diff', 'changed': changed, 'tests': []}
    try:
        graph = import_graph(root)
    except UnsafeGraph as exc:
        return full(str(exc))
    affected = [t for t in tests if set(runnable) & closure(graph, t)]
    # An unmapped production module could use conventions not represented by imports.
    if any(p.startswith('src/') and not any(p in closure(graph, t) for t in tests) for p in runnable):
        return full('Source change has no mapped test; conservative fallback')
    if not affected:
        return full('Changed Python file cannot be mapped safely')
    return {'mode': 'subset', 'reason': 'Transitive static import dependencies', 'changed': changed, 'tests': affected}


def git_changes(root, base, head, merge_base=False):
    if not base or not head or set(base)=={'0'} or base.startswith('-') or head.startswith('-'):
        return None
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL)
    try:
        base = git('rev-parse', '--verify', '--end-of-options', base+'^{commit}').decode().strip()
        head = git('rev-parse', '--verify', '--end-of-options', head+'^{commit}').decode().strip()
        if merge_base:
            base = git('merge-base', base, head).decode().strip()
        return [p.decode('utf-8') for p in git('diff', '--name-only', '-z', '--no-renames', base, head, '--').split(b'\0') if p]
    except (subprocess.CalledProcessError, UnicodeError, OSError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.')
    parser.add_argument('--base'); parser.add_argument('--head', default='HEAD')
    parser.add_argument('--merge-base', action='store_true')
    parser.add_argument('--changed', nargs='*', default=None)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--output', default='reports/selection.json')
    args = parser.parse_args()
    changed = args.changed if args.changed is not None else git_changes(args.root, args.base, args.head, args.merge_base)
    result = select(args.root, changed, args.full)
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)
    if args.run and result['mode'] != 'none':
        targets = result['tests'] if result['tests'] else ['tests']
        return subprocess.call([sys.executable, '-m', 'pytest', '-v', '--junitxml=reports/selected-tests.xml', *targets], cwd=args.root)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
