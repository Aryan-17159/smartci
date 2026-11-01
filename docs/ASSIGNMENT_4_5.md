# Assignment 4.5 — Build-Failure Prediction
## Objective and dataset
[predict_failure.py](../ml/predict_failure.py) trains a standardized logistic regression to estimate failure risk before a build. Features are changed-file count, changed-line count, dependency-change flag, test-change flag and previous-build failure. Current build outcome is only the training label, never an input.

The repository has too few actual CI outcomes for a meaningful trained predictor. Therefore the committed 600-row dataset is explicitly **synthetic**, generated with seed 42. Its probabilities are educational and do not establish real repository risk.

## Steps
1. Complete [setup](ASSIGNMENTS.md).
2. Reproduce the dataset: `python -m ml.predict_failure generate`.
3. Train: `python -m ml.predict_failure train`. The first 480 chronological records train the scaler and model; the last 120 evaluate them.
4. Inspect reports/prediction/metrics.json and model.json. The model is exported as plain coefficients and scaling values, without pickle.
5. Run `python -m ml.predict_failure predict --features ml/example_features.json`.
6. Inspect reports/prediction/prediction.json. The supplied example gives approximately 0.609 failure probability and is marked advisory_only.
7. GitHub Actions repeats training and prediction and uploads the reports.

## Actual evaluation and interpretation
[Recorded metrics](evidence/assignments/prediction/metrics.json): accuracy 0.7833; majority-class baseline accuracy 0.7833; precision 0.5000; recall 0.1923; F1 0.2778; ROC-AUC 0.7741; Brier score 0.1395. Confusion counts: 89 true negatives, 5 false positives, 21 false negatives and 5 true positives.

The default threshold 0.5 misses 21 of 26 failures. Accuracy alone hides this weakness, and the model does not outperform the trivial baseline on accuracy. No threshold was tuned using held-out outcomes. These results do not justify blocking or skipping builds.

## Learning and next steps
Chronological evaluation reduces future-data leakage. Fit preprocessing only on the training split. A previous outcome is available before the next build; the current outcome is not. Class imbalance requires recall, precision and calibration alongside accuracy.

To deploy meaningfully, collect many real completed build records with pre-build diff features and timestamps; reserve a later time period for evaluation; tune on a separate validation period; compare against baselines and monitor drift. The example input is supplied manually, not represented as an automatically extracted live commit. Prediction never overrides the real test result.

