# Publication sanitization log

All operations apply only to this derivative. The private source ZIPs remain unchanged.

## Excluded non-source compiled caches

| Original path | Reason | Classification | Corresponding source remains? |
|---|---|---|---|
| `scripts/__pycache__/clean_replay.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `src/__pycache__/__init__.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `src/__pycache__/checker.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `src/__pycache__/parsing.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `src/__pycache__/schemas.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `src/__pycache__/scoring.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `src/__pycache__/utils.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `tests/__pycache__/test_amendment_h01_h06.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `tests/__pycache__/test_cases.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `tests/__pycache__/test_checker.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `tests/__pycache__/test_model_run.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `tests/__pycache__/test_reproducibility.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |
| `tests/__pycache__/test_scoring.cpython-312.pyc` | Compiled Python cache embeds local build/runtime metadata and is not canonical source evidence. | NON-SOURCE COMPILED CACHE | YES |

## Local-path redactions

| Derivative file | Line | Original category | Replacement | Reason |
|---|---:|---|---|---|
| `baseline/a1_revision_bundle/revision/checker_execution_log_rev2.txt` | 12 | LOCAL CONTAINER PATH | `[LOCAL_PATH_REDACTED]` | Remove local environment identifier while preserving the log line. |
| `baseline/a1_revision_bundle/revision/checker_execution_log_rev2.txt` | 150 | LOCAL CONTAINER PATH | `[LOCAL_PATH_REDACTED]` | Remove local environment identifier while preserving the log line. |
| `evidence/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Public_Safe.zip!/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Freeze_Candidate/baseline/a1_revision_bundle/revision/checker_execution_log_rev2.txt` | 12 | LOCAL CONTAINER PATH | `[LOCAL_PATH_REDACTED]` | Remove duplicated local environment identifier in public-safe embedded source. |
| `evidence/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Public_Safe.zip!/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Freeze_Candidate/baseline/a1_revision_bundle/revision/checker_execution_log_rev2.txt` | 150 | LOCAL CONTAINER PATH | `[LOCAL_PATH_REDACTED]` | Remove duplicated local environment identifier in public-safe embedded source. |
| `evidence/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Public_Safe.zip!/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Freeze_Candidate/results/fresh_rev2_execution.log` | 12 | LOCAL CONTAINER PATH | `[LOCAL_PATH_REDACTED]` | Remove duplicated local environment identifier in public-safe embedded execution record. |
| `evidence/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Public_Safe.zip!/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Freeze_Candidate/results/fresh_rev2_execution.log` | 150 | LOCAL CONTAINER PATH | `[LOCAL_PATH_REDACTED]` | Remove duplicated local environment identifier in public-safe embedded execution record. |

Files path-sanitized: **3**
Individual path occurrences redacted: **6**

No substantive log line was removed. Python source files remain unchanged.
