# securepay-seed

Database seed and Kaggle ETL for the SecurePay Antifraude project.

## What it does

- **Seed** (`securepay_seed`): fills PostgreSQL with users, accounts, devices,
  merchants and the restricted list (100 users, 100 accounts, 150 devices,
  50 merchants and 20 list entries in `dev` mode). It also exports the list to
  `generated/listas/lista_restrictiva.jsonl` (and optionally to S3) for the
  restricted-list service in **securepay-apis**.
  - Reproducible: the same `SEED` gives the same data on Windows and Linux.
  - Idempotent: running it again does not duplicate rows (`SEED_RESET=true` starts over).
  - Sizes come from environment variables (see `.env.example`).
- **Kaggle ETL** (`securepay_seed.kaggle_etl`): loads 70 000 historical
  transactions from PaySim and fraudTest into the `transacciones` table, linked
  to seed users and devices.

All runs share `SEED=42` and `FECHA_REFERENCIA=2026-10-01`.

## Setup

```bash
git clone https://github.com/SecurePay-Riwi/securepay-seed.git
cd securepay-seed
cp .env.example .env   # DATABASE_URL points to the Compose PostgreSQL (port 5433)
uv sync                # installs securepay-shared from PyPI
```

## Local services

PostgreSQL (port 5433) and LocalStack run with the Docker Compose of the
[SecurePay](https://github.com/SecurePay-Riwi/SecurePay) repository (`docker compose up -d`).

## Usage

```bash
# Run the seed (master data only)
uv run python -m securepay_seed.seed

# Load the Kaggle historical transactions
uv run python -m securepay_seed.kaggle_etl.etl

# Dry run: show what the ETL would do without writing anything
uv run python -m securepay_seed.kaggle_etl.etl --dry-run

# Run the tests (no database or CSVs needed)
uv run pytest
```

## Kaggle CSVs (for the ETL)

The ETL looks for both CSVs, in this order, in `src/securepay_seed/kaggle_etl/raw/`,
in `KAGGLE_DOWNLOAD_DIR` (default `data/kaggle/`) and in
`../securepay-csv/data/kaggle/`, where **securepay-csv** downloads them. All of
them are Git-ignored.

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

## Repository layout

```
src/securepay_seed/
├── seed.py           # entry point: python -m securepay_seed.seed
├── config.py         # volumes, percentages, reference date
├── fechas.py         # deterministic dates (no Faker dates)
├── export_lista.py   # restricted list export for securepay-apis
├── tables/           # one generator per table
├── defects/          # defect injection
└── kaggle_etl/       # ETL of PaySim and fraudTest (python -m securepay_seed.kaggle_etl.etl)
tests/
├── seed/
└── kaggle_etl/
```

All code lives in one package under `src/`; tests mirror it under `tests/`.
Read [AGENTS.md](AGENTS.md) before adding folders or modules.

## Working with the other repositories

The repositories pass data through files (and through S3 in AWS), never through
imports. Clone them side by side in the same folder and each one finds the files
the others produce, without setting paths by hand:

```
SecurePay-Riwi/
├── securepay-seed/        # PostgreSQL master data + restricted list export
├── securepay-generator/   # reads the seed, writes generated/instance-*/
├── securepay-csv/         # Kaggle downloads + partner statements (reads the generator)
└── securepay-apis/        # restricted-list service (reads the seed export)
```

Environment variables still override every path (see `.env.example`).

## Dependencies

- [`securepay-shared`](https://pypi.org/project/securepay-shared/): shared models, database and config
- PostgreSQL 16+
