"""Content-addressed Python compilation cache; every artifact is integrity checked."""
import argparse
import hashlib
import json
import platform
import py_compile
import sys
from pathlib import Path

from scripts.dependencies import closure, import_graph


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(root, cache_dir):
    root, cache_dir = Path(root).resolve(), Path(cache_dir).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    graph = import_graph(root)
    environment = {'schema': 1, 'python': sys.version, 'cache_tag': sys.implementation.cache_tag,
                   'platform': platform.system(), 'machine': platform.machine()}
    common = {name: digest((root/name).read_bytes()) for name in
              ('requirements.txt', 'requirements.lock', 'scripts/cache_build.py', 'scripts/dependencies.py')
              if (root/name).exists()}
    entries = []
    for rel in sorted(p for p in graph if p.startswith('src/')):
        dependencies = {p: digest((root/p).read_bytes()) for p in sorted(closure(graph, rel))}
        key = digest(json.dumps({'environment': environment, 'common': common,
                                 'dependencies': dependencies}, sort_keys=True).encode())
        artifact, receipt = cache_dir/f'{key}.pyc', cache_dir/f'{key}.json'
        hit = False
        try:
            saved = json.loads(receipt.read_text(encoding='utf-8'))
            hit = artifact.is_file() and saved.get('artifact_sha256') == digest(artifact.read_bytes())
        except (OSError, ValueError):
            pass
        if not hit:
            py_compile.compile(str(root/rel), cfile=str(artifact), dfile=rel, doraise=True,
                               invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH)
            receipt.write_text(json.dumps({'artifact_sha256': digest(artifact.read_bytes())}), encoding='utf-8')
        entries.append({'module': rel, 'key': key, 'status': 'hit' if hit else 'miss',
                        'dependencies': sorted(dependencies)})
    return {'environment': environment, 'hits': sum(e['status']=='hit' for e in entries),
            'misses': sum(e['status']=='miss' for e in entries), 'entries': entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.')
    parser.add_argument('--cache-dir', default='.smartci/build-cache')
    parser.add_argument('--output', default='reports/cache.json')
    args = parser.parse_args()
    result = build(args.root, args.cache_dir)
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
