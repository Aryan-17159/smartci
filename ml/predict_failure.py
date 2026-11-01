"""Train and evaluate a pre-build failure classifier on explicitly synthetic history."""
import argparse
import csv
import json
import math
import random
from pathlib import Path

FEATURES = ['files_changed', 'lines_changed', 'dependency_changed', 'tests_changed', 'previous_failure']


def generate_rows(count=600, seed=42):
    rng=random.Random(seed); rows=[]; previous=0
    for i in range(count):
        files=rng.randint(1,25); lines=rng.randint(1,1000)
        dependency=int(rng.random()<0.2); tests=int(rng.random()<0.4)
        logit=-3.5+0.07*files+0.002*lines+1.0*dependency-0.7*tests+0.8*previous
        failed=int(rng.random() < 1/(1+math.exp(-logit)))
        rows.append(dict(build_id=i+1, files_changed=files, lines_changed=lines,
                         dependency_changed=dependency, tests_changed=tests,
                         previous_failure=previous, failed=failed, provenance='synthetic_seed_42' if seed==42 else f'synthetic_seed_{seed}'))
        previous=failed
    return rows


def validate(rows):
    if len(rows)<50:
        raise ValueError('At least 50 ordered builds are required for this demonstration')
    ids=[int(r['build_id']) for r in rows]
    if ids != sorted(set(ids)):
        raise ValueError('Rows must be ordered by unique increasing build_id')
    for row in rows:
        for name in FEATURES+['failed']:
            value=float(row[name])
            if not math.isfinite(value) or value<0:
                raise ValueError(f'Invalid {name}')
        for name in FEATURES[2:]+['failed']:
            if float(row[name]) not in (0,1):
                raise ValueError(f'{name} must be binary')


def train(rows):
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.dummy import DummyClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, brier_score_loss
    validate(rows)
    x=np.array([[float(r[f]) for f in FEATURES] for r in rows]); y=np.array([int(r['failed']) for r in rows])
    split=int(len(rows)*0.8)
    if len(set(y[:split]))<2 or len(set(y[split:]))<2:
        raise ValueError('Both outcomes must appear in training and held-out data')
    model=make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42))
    model.fit(x[:split], y[:split])
    probability=model.predict_proba(x[split:])[:,1]; predicted=(probability>=0.5).astype(int)
    baseline=DummyClassifier(strategy='most_frequent').fit(x[:split], y[:split])
    scaler, estimator=model.steps[0][1], model.steps[1][1]
    exported={'schema':1,'features':FEATURES,'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),
              'coefficients':estimator.coef_[0].tolist(),'intercept':float(estimator.intercept_[0]),
              'threshold':0.5,'training_provenance':sorted(set(r['provenance'] for r in rows[:split]))}
    metrics={'data_provenance':sorted(set(r['provenance'] for r in rows)),
             'warning':'Educational evaluation; synthetic-data metrics do not establish real CI reliability.',
             'split':'Chronological first 80% train, final 20% test; no shuffled future data',
             'train_count':split,'test_count':len(rows)-split,'threshold':0.5,
             'accuracy':accuracy_score(y[split:],predicted),'precision':precision_score(y[split:],predicted,zero_division=0),
             'recall':recall_score(y[split:],predicted,zero_division=0),'f1':f1_score(y[split:],predicted,zero_division=0),
             'roc_auc':roc_auc_score(y[split:], probability),'brier_score':brier_score_loss(y[split:],probability),
             'baseline_accuracy':accuracy_score(y[split:],baseline.predict(x[split:])),
             'confusion_matrix_labels':[0,1],'confusion_matrix':confusion_matrix(y[split:],predicted,labels=[0,1]).tolist()}
    return exported, metrics


def predict(model, features):
    if model.get('schema')!=1 or model.get('features')!=FEATURES:
        raise ValueError('Unsupported model schema or features')
    values=[float(features[f]) for f in FEATURES]
    if any(not math.isfinite(v) or v<0 for v in values) or any(v not in (0,1) for v in values[2:]):
        raise ValueError('Features must be finite nonnegative counts and binary flags')
    z=model['intercept']+sum(c*(v-m)/s for c,v,m,s in zip(model['coefficients'],values,model['mean'],model['scale'],strict=True))
    probability=1/(1+math.exp(-max(-700,min(700,z))))
    return {'failure_probability':probability,'prediction':'failure' if probability>=model['threshold'] else 'success',
            'features':features,'advisory_only':True,'training_provenance':model['training_provenance']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    gen=sub.add_parser('generate');gen.add_argument('--output',default='ml/data/synthetic_builds.csv')
    fit=sub.add_parser('train');fit.add_argument('--data',default='ml/data/synthetic_builds.csv');fit.add_argument('--output-dir',default='reports/prediction')
    infer=sub.add_parser('predict');infer.add_argument('--model',default='reports/prediction/model.json');infer.add_argument('--features',required=True);infer.add_argument('--output',default='reports/prediction/prediction.json')
    args=parser.parse_args()
    if args.command=='generate':
        rows=generate_rows();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
        with out.open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        print(f'Wrote {len(rows)} explicitly synthetic records')
    elif args.command=='train':
        with Path(args.data).open(encoding='utf-8') as stream: rows=list(csv.DictReader(stream))
        model,metrics=train(rows);out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
        for name,value in [('model',model),('metrics',metrics)]:
            (out/f'{name}.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(metrics,indent=2))
    else:
        result=predict(json.loads(Path(args.model).read_text()),json.loads(Path(args.features).read_text()))
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
