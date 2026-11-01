# Assignment 4.2 — Smart Build-Cache Invalidation
## Objective and implementation
Avoid rebuilding unchanged Python modules while invalidating dependent modules when inputs change. [cache_build.py](../scripts/cache_build.py) produces real checked-hash .pyc artifacts. [dependencies.py](../scripts/dependencies.py) parses imports into a directed graph.

Each key includes Python/runtime/platform identity, dependency manifests, build-tool source and the content of the module's complete transitive dependency closure. A stored SHA-256 receipt verifies the artifact before reuse. Missing or corrupted artifacts rebuild. Dependencies are conservatively invalidated when requirements change.

## Steps and observed results
1. Install the locked environment as described in [setup](ASSIGNMENTS.md).
2. Run `python -m scripts.cache_build --output reports/cache.json`. This builds src modules into .smartci/build-cache.
3. Run it again. Unchanged keys and valid receipts produce hits.
4. Run `python -m scripts.demo_assignments`. It uses a disposable copy; it never edits your working source.
5. Inspect reports/experiments/cache-experiments.json. The committed [actual experiment](evidence/assignments/cache-experiments.json) shows cold: 0 hits/4 misses; warm: 4 hits/0 misses; pricing changed: 2 hits/2 misses; requirements changed: 0 hits/4 misses.
6. Pricing changes invalidate pricing and cart because cart imports pricing. Inventory remains reusable.
7. In Actions, open **Restore build cache**, **Build with dependency-aware invalidation**, and the uploaded smartci-evidence artifact. Outer GitHub caching transports the directory; inner module keys establish validity.

## Validation and learning
Tests cover cold/warm behavior, transitive changes, dependency changes, valid bytecode and corrupt artifacts. A cache key must describe inputs, not merely a branch name. The cache is an optimization; rebuilding is the safe response to uncertainty. This small compilation demo measures reuse counts, not a proven wall-clock speedup. Tests import normal source; cached artifacts demonstrate build reuse and are not substituted into the test interpreter.

GitHub cache entries are immutable; a changed aggregate source hash saves a new entry, while a restore prefix retrieves earlier module artifacts for individual validation. See [official caching documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching).

