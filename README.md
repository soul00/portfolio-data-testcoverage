# portfolio-data-testcoverage

[![ci](https://github.com/soul00/portfolio-data-testcoverage/actions/workflows/ci.yml/badge.svg)](https://github.com/soul00/portfolio-data-testcoverage/actions/workflows/ci.yml)

Quality gate for ML training data. New versions of a dataset get checked (schema,
null rates, duplicates, label balance, drift against a baseline) before they are
allowed into model training. If the gate fails you get a report of what exactly is
wrong, instead of a model that silently got worse.

This is a portfolio project. The main goal is to show how I approach test
automation, so the test setup is more thorough than a project of this size would
normally need: unit tests for the validation logic, API and contract tests,
browser tests for the dashboard, load tests, all wired into CI.

Demo dataset is [IMDB movie reviews](https://huggingface.co/datasets/stanfordnlp/imdb)
from Hugging Face — 50k reviews labeled positive/negative. It contains real
duplicates, so the duplicate check has something to catch.

## Stack

- Python, FastAPI, pandas — validation engine and API
- Postgres — results and run history
- S3 for dataset versions (LocalStack in tests, CI needs no cloud access)
- Next.js dashboard
- pytest, schemathesis, Playwright, k6
- GitHub Actions

## Status

Early stage, building this in the evenings. Rough plan:

- [x] validation engine + unit tests
- [ ] API, Postgres, dataset ingestion
- [ ] API and contract tests running in CI
- [ ] dashboard + browser tests
- [ ] deployment, smoke tests, nightly runs
- [ ] load tests

## License

MIT
