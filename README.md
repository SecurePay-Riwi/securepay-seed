# securepay-seed

Database seed and ETL datasets for the SecurePay Antifraude project.

## Sources

| ID | Source | Type |
|----|--------|------|
| F4 | Users, accounts, devices, merchants, restricted list | Simulated DB (seed) |

Seed data is reproducible: running it multiple times does not duplicate records.
Volume is configurable via environment variables.

## Setup

```bash
git clone https://github.com/SecurePay-Riwi/securepay-seed.git
cd securepay-seed
cp .env.example .env
uv sync
```

## Usage

```bash
# Run the full seed (creates tables + inserts data)
uv run python -m seed.run

# Run ETL datasets load
uv run python -m datasets.load
```

## Dependencies

- [`securepay-shared`](https://pypi.org/project/securepay-shared/) — shared models, DB and config
