"""Run reproducible cache and routing experiments in a disposable project copy."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

from scripts.cache_build import build
from scripts.select_tests import select


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',default='reports/experiments')
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='smartci-demo-') as directory:
        project=Path(directory)/'project';project.mkdir()
        for folder in ('src','tests','scripts'):
            shutil.copytree(root/folder,project/folder,ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('requirements.txt','requirements.lock'):
            if (root/name).exists(): shutil.copy2(root/name,project/name)
        cache=Path(directory)/'cache'
        experiments={'cold':build(project,cache),'warm':build(project,cache)}
        with (project/'src/pricing.py').open('a',encoding='utf-8') as stream: stream.write('\n# Dependency invalidation experiment\n')
        experiments['pricing_changed']=build(project,cache)
        with (project/'requirements.txt').open('a',encoding='utf-8') as stream: stream.write('\n# Dependency manifest changed\n')
        experiments['requirements_changed']=build(project,cache)
        routing={name:select(project,changes) for name,changes in {
            'pricing':['src/pricing.py'],'inventory':['src/inventory.py'],
            'test_only':['tests/test_cart.py'],'docs_only':['docs/notes.md'],
            'dependencies':['requirements.txt'],'deleted_source':['src/deleted.py'],
            'unknown_base':None}.items()}
        for name,value in [('cache-experiments',experiments),('routing-experiments',routing)]:
            (out/f'{name}.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'cache':{k:{'hits':v['hits'],'misses':v['misses']} for k,v in experiments.items()},
                          'routing':routing},indent=2))


if __name__=='__main__':
    main()
