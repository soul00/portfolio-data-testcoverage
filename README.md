# portfolio-data-testcoverage

[![ci](https://github.com/soul00/portfolio-data-testcoverage/actions/workflows/ci.yml/badge.svg)](https://github.com/soul00/portfolio-data-testcoverage/actions/workflows/ci.yml)

Quality gate for ML training data. New versions of a dataset get validated
before they are allowed into model training. If the data is broken, the gate
fails and reports what exactly is wrong, instead of letting a model silently
train on garbage.

This is a portfolio project — the test setup is the point, so it's more
thorough than a project of this size would normally need.

## The problem

Teams that retrain models on fresh data get burned by silent data issues: an
export breaks and half the rows disappear, a column changes type, duplicates
pile up, labels drift out of balance. Nothing crashes. The model just gets
worse and nobody knows why until it shows in production. The fix is to treat
data like code: validate it with tests, in CI, on every change. That's what
this repo does end to end.

## How it works

The core is a small validation engine in `backend/quality_gate/`:

- `checks.py` — five checks: row count, schema, null rates, duplicate rate,
  label balance. Each returns a structured result with the measured numbers,
  so a failure says "duplicates: 7.3% vs 0.5% allowed", not just "failed".
- `gate.py` — runs the configured checks, produces the pass/fail verdict.
- `api.py` — FastAPI wrapper: validate ad-hoc data, store and browse gate runs.
- `storage.py` — Postgres model for run history (results only, never the data).
- `ingest.py` / `corrupt.py` — download the demo dataset / break it on purpose.

Demo dataset is [IMDB movie reviews](https://huggingface.co/datasets/stanfordnlp/imdb)
from Hugging Face — 50k reviews labeled positive/negative, two columns total.

## The tests

- unit tests for every check — failure details, threshold boundaries
  (exactly-at-limit passes), empty inputs
- API tests through HTTP
- contract tests generated from the OpenAPI schema with schemathesis. Worth
  mentioning: the first schemathesis run found 6 real bugs in an API that
  already had 44 green handwritten tests — a negative `limit` leaking a raw
  SQL error, an int32 overflow on the id path, a NUL byte crashing inserts,
  undocumented status codes, silent type coercion in the config
- dataset tests that run the checks against the actual snapshot on disk

## The pipeline

Every push runs the same 20 tests twice:

- **Passing run** — ingests the clean dataset. Everything green.
- **Failing run** — ingests the same dataset, then corrupts it on purpose
  (drops 4k rows, injects nulls and duplicate rows, breaks the label dtype,
  skews the class balance). The dataset tests catch every defect. This job is
  red by design; `continue-on-error` keeps the workflow itself green.

Same tests, different data — the diff between the two runs is the proof that
the gate catches real issues instead of passing blindly.

Why a pipeline and not a script: a gate only helps if nobody can forget to run
it. In CI it runs on every push, can be scheduled, and can be triggered on
demand — which is how it would sit in front of a real training job.

Both runs are shown live on my portfolio page, which reads this repo's Actions
through the GitHub API, and the pipeline can be triggered from there
(`workflow_dispatch`).

## Running locally

```
cd backend
python -m venv .venv
.venv\Scripts\activate        # source .venv/bin/activate on unix
pip install -e .[dev]
docker compose up -d db       # from the repo root
python -m quality_gate.ingest
pytest
```

All 20 tests should pass. To see the failing state, run
`python -m quality_gate.corrupt` and run pytest again — the 5 dataset tests
go red with the exact defects in the assertion output.

## Stack

Python, pandas, FastAPI, Postgres, pytest, schemathesis, Docker,
GitHub Actions.

## License

MIT
