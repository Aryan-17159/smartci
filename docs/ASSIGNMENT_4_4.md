# Assignment 4.4 — LLM-Based Build/Error-Log Summarization
## Objective and implementation
[summarize_log.py](../scripts/summarize_log.py) redacts common secret patterns, extracts failure facts and optionally runs google/flan-t5-small locally. It never executes instructions contained in a log. Exact facts and advisory model prose are separate JSON fields. Model failures propagate; there is no silent substitution of a template for a claimed LLM response.

## Steps
1. Complete [setup](ASSIGNMENTS.md).
2. Install CPU inference: `python -m pip install torch==2.9.0 --index-url https://download.pytorch.org/whl/cpu`.
3. Run `python -m pip install -r requirements-llm.txt`.
4. Run `python -m scripts.summarize_log docs/evidence/github-red-run.txt --provider local-llm --revision 0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab --output reports/llm-summary.json`. The first run downloads model weights.
5. Inspect facts, summary, llm_used, model_revision and prompt_sha256.
6. For a fast deterministic option, explicitly choose `--provider extractive`. This output is labeled as having called no LLM.
7. In GitHub Actions, manually dispatch CI to run the same model demonstration and download its evidence artifact. Ordinary pushes use extraction to avoid repeated model downloads.

## Actual result and evaluation
[Committed actual local inference](evidence/assignments/llm-summary.json) records llm_used=true and the resolved model revision. It correctly extracts test_discount_boundaries, tests/test_pricing.py:11, comparison 100.0 == 101.0, and 1 failed/27 passed from the real red-run log. The model generated “1 failed, 27 passed.” This is accurate but incomplete: it omits the cause. The structured evidence supplies that missing detail.

The correct human explanation is: a zero-percent discount returns 100.0, but the deliberately changed test expected 101.0. Restore 100.0 and rerun CI. An initial verbose JSON prompt caused repetition; a concise factual prompt improved output. This experiment demonstrates actual LLM inference without claiming human-level diagnosis.

## Learning and safeguards
Small models can omit causes or hallucinate. Keep exact log references, review model output and never automatically apply its suggested fixes. Redaction patterns are best-effort, not a guarantee of secret removal; inference is local and logs are not sent to an external inference service. Inputs are bounded to the last 2 MB; the JSON flags truncation. Unit tests inject a fake generator only to verify integration; the committed inference was produced by the real downloaded model.

See the [official FLAN-T5 model card](https://huggingface.co/google/flan-t5-small). The workflow's deterministic summary is not described as LLM output.

