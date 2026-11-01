import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.cache_build import build
from scripts.dependencies import closure, import_graph
from scripts.select_tests import git_changes, select
from scripts.summarize_log import extract, redact, summarize
from ml.predict_failure import FEATURES, generate_rows, predict, train, validate


@pytest.fixture
def project(tmp_path):
    files={'src/__init__.py':'', 'src/pricing.py':'def price(): return 10\n',
           'src/cart.py':'from .pricing import price\ndef total(): return price()\n',
           'src/inventory.py':'stock = 5\n',
           'tests/test_pricing.py':'from src.pricing import price\ndef test_price(): assert price()==10\n',
           'tests/test_cart.py':'from src.cart import total\ndef test_total(): assert total()==10\n',
           'tests/test_inventory.py':'from src.inventory import stock\ndef test_stock(): assert stock==5\n',
           'requirements.txt':'pytest==8.4.2\n'}
    for name,text in files.items():
        file=tmp_path/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text,encoding='utf-8')
    return tmp_path


def test_cache_cold_then_warm(project):
    assert build(project,project/'.cache')['misses']==4
    assert build(project,project/'.cache')['hits']==4


def test_transitive_cache_invalidation(project):
    build(project,project/'.cache')
    (project/'src/pricing.py').write_text('def price(): return 11\n')
    result=build(project,project/'.cache')
    assert {e['module'] for e in result['entries'] if e['status']=='miss'}=={'src/pricing.py','src/cart.py'}


def test_dependencies_invalidate_every_artifact(project):
    build(project,project/'.cache')
    (project/'requirements.txt').write_text('pytest==8.4.1\n')
    assert build(project,project/'.cache')['misses']==4


def test_corrupted_cache_is_rebuilt(project):
    result=build(project,project/'.cache');key=result['entries'][0]['key']
    (project/'.cache'/f'{key}.pyc').write_bytes(b'corrupted')
    assert build(project,project/'.cache')['misses']==1


def test_cache_artifact_is_valid_bytecode(project):
    result=build(project,project/'.cache')
    import importlib.util
    for entry in result['entries']:
        assert (project/'.cache'/f"{entry['key']}.pyc").read_bytes().startswith(importlib.util.MAGIC_NUMBER)


def test_relative_import_and_cycle(project):
    (project/'src/pricing.py').write_text('from .cart import total\ndef price(): return 10\n')
    graph=import_graph(project)
    assert 'src/cart.py' in closure(graph,'src/pricing.py')
    assert len(closure(graph,'src/pricing.py'))==3


def test_pricing_routes_to_cart_and_pricing(project):
    result=select(project,['src/pricing.py'])
    assert result['tests']==['tests/test_cart.py','tests/test_pricing.py']


def test_inventory_routes_only_inventory(project):
    assert select(project,['src/inventory.py'])['tests']==['tests/test_inventory.py']


def test_test_only_routes_to_changed_test(project):
    assert select(project,['tests/test_cart.py'])['tests']==['tests/test_cart.py']


@pytest.mark.parametrize('path',['requirements.txt','.github/workflows/ci.yml','scripts/cache_build.py',
                                 'src/__init__.py','tests/conftest.py','src/deleted.py','assets/config.json',
                                 '../outside.py','C:/outside.py'])
def test_uncertain_changes_run_full_suite(project,path):
    assert select(project,[path])['mode']=='full'


def test_docs_only_can_skip_subset(project):
    assert select(project,['docs/notes.md','README.md'])['mode']=='none'
    assert select(project,['README.md'],force_full=True)['mode']=='full'


def test_missing_diff_runs_full(project):
    assert select(project,None)['mode']=='full'
    assert git_changes(project,'0'*40,'HEAD') is None
    assert git_changes(project,'--help','HEAD') is None


def test_syntax_error_does_not_silently_skip(project):
    (project/'src/pricing.py').write_text('def broken(')
    assert select(project,['src/pricing.py'])['mode']=='full'


def test_dynamic_import_runs_full(project):
    (project/'src/cart.py').write_text("import importlib\nx=importlib.import_module('src.pricing')\n")
    assert select(project,['src/pricing.py'])['mode']=='full'


def test_unmapped_new_module_runs_full(project):
    (project/'src/new.py').write_text('value=1\n')
    assert select(project,['src/new.py'])['mode']=='full'


def test_git_diff_detects_deleted_and_renamed_files(project):
    def git(*args):
        return subprocess.check_output(['git','-C',str(project),*args],stderr=subprocess.DEVNULL).decode().strip()
    git('init');git('add','.');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-m','initial')
    before=git('rev-parse','HEAD')
    (project/'src/inventory.py').rename(project/'src/stock.py')
    git('add','-A');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-m','rename')
    changed=git_changes(project,before,'HEAD')
    assert {'src/inventory.py','src/stock.py'}<=set(changed)
    assert select(project,changed)['mode']=='full'


def test_log_redaction():
    cleaned=redact('Authorization: Bearer abc123\npassword=verysecret\nfoo@example.com\nghp_abcdef123\nhttps://user:pass@host/path')
    for secret in ['abc123','verysecret','foo@example.com','ghp_abcdef123','user:pass']:
        assert secret not in cleaned


def test_extract_failure_facts():
    text='E       assert 100.0 == 101.0\ntests/test_pricing.py:11: AssertionError\nFAILED tests/test_pricing.py::test_discount_boundaries\n1 failed, 27 passed\nProcess completed with exit code 1.'
    result=extract(text)
    assert result['status']=='failure'
    assert result['locations']==['tests/test_pricing.py:11']
    assert result['assertions']==['100.0 == 101.0']


def test_clean_and_unknown_logs():
    assert extract('28 passed in 0.04s')['status']=='success'
    assert extract('starting build')['status']=='unknown'


def test_fallback_is_not_presented_as_llm():
    result=summarize('28 passed in 0.04s')
    assert result['llm_used'] is False
    assert result['provider']=='extractive'


def test_llm_adapter_receives_only_redacted_text():
    def fake(prompt,model,revision):
        assert 'mysecret' not in prompt
        return 'Test assertion failed.', 'test-revision'
    result=summarize('ERROR token=mysecret\n1 failed, 27 passed',provider='local-llm',generator=fake)
    assert result['llm_used'] and result['model_revision']=='test-revision'


def test_model_errors_are_not_silently_replaced():
    def broken(*args): raise RuntimeError('model unavailable')
    with pytest.raises(RuntimeError,match='model unavailable'):
        summarize('ERROR',provider='local-llm',generator=broken)


def test_synthetic_history_is_reproducible_and_temporal():
    rows=generate_rows();assert rows==generate_rows()
    assert rows[0]['previous_failure']==0
    assert all(a['failed']==b['previous_failure'] for a,b in zip(rows,rows[1:]))
    assert all(r['provenance']=='synthetic_seed_42' for r in rows)


def test_prediction_training_and_json_roundtrip():
    model,metrics=train(generate_rows())
    assert (metrics['train_count'],metrics['test_count'])==(480,120)
    assert sum(map(sum,metrics['confusion_matrix']))==120
    assert set(model['features'])==set(FEATURES)
    assert 'failed' not in model['features']
    values=dict(zip(FEATURES,[12,650,1,0,1]))
    result=predict(json.loads(json.dumps(model)),values)
    assert 0<=result['failure_probability']<=1
    assert result['advisory_only']


def test_model_standardization_uses_training_rows_only():
    rows=generate_rows();model,_=train(rows)
    assert model['mean'][0]==pytest.approx(sum(r['files_changed'] for r in rows[:480])/480)


def test_rejects_invalid_training_data():
    with pytest.raises(ValueError): validate(generate_rows(10))
    rows=generate_rows();rows[2]['build_id']=1
    with pytest.raises(ValueError): validate(rows)
    rows=generate_rows();rows[0]['lines_changed']=math.nan
    with pytest.raises(ValueError): validate(rows)
