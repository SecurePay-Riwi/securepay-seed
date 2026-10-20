# securepay-seed

Database seed and Kaggle ETL for the SecurePay Antifraude project.

## Data sources

| ID | Source | Type |
|----|--------|------|
| F4 | Users, accounts, devices, merchants, restricted list | Deterministic seed → PostgreSQL |

## What it does

- **Seed** (`db/seed/`): creates 100 users, 100 accounts, 150 devices, 50 merchants and
  20 restricted-list entries. Exports the list to `generated/listas/lista_restrictiva.jsonl`
  (and optionally to S3).
- **Kaggle ETL** (`db/datasets/`): loads 70 000 historical transactions from PaySim and
  fraudTest into the `transacciones` table, linked to seed users and devices.

All runs are reproducible: the seed and ETL share `SEED=42` and `FECHA_REFERENCIA=2026-10-01`.

## Setup

```bash
git clone https://github.com/SecurePay-Riwi/securepay-seed.git
cd securepay-seed
cp .env.example .env   # set DATABASE_URL
uv sync                # installs securepay-shared from PyPI automatically
```

PostgreSQL must be running and the `pagoseguro` database must exist before running the seed.
See the [monorepo README](https://github.com/SecurePay-Riwi/SecurePay) for DB setup steps.

## Usage

```bash
# Run the seed (master data only)
uv run python -m db.seed.seed

# Load Kaggle historical transactions (requires the two CSVs in data/kaggle/)
uv run python -m db.datasets.etl

# Dry-run: see what the ETL would do without writing anything
uv run python -m db.datasets.etl --dry-run

# Run tests (no real DB or CSVs needed)
uv run pytest
```

## Required Kaggle CSVs (for the ETL)

Place these in `data/kaggle/` (Git-ignored):

| File | Dataset |
|------|---------|
| `PS_20174392719_1491204439457_log.csv` | [ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1) |
| `fraudTest.csv` | [kartik2112/fraud-detection](https://www.kaggle.com/datasets/kartik2112/fraud-detection) |

## Reproducibility check

After the ETL, the SHA-256 fingerprint of the loaded batch should be:

```
3c1004fc13346d567832acf8b916114ff4c829cad3114a31a19e117e2e667b9c
```

(Linux, PostgreSQL 16, default `.env` values, `dev` mode with 100 users / 50 merchants.)

## Dependencies

- [`securepay-shared`](https://pypi.org/project/securepay-shared/) — shared models, DB and config
- PostgreSQL 16+
