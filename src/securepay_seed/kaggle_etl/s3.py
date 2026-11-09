"""The Kaggle CSVs from the data lake instead of a local folder.

In AWS the ETL runs in the admin task, which has no copy of the CSVs: it
reads them from the raw layer, where securepay-csv's loader (or the apply of
SecurePay's dev environment) leaves them untouched. HIST_RAW_DIR (or
--raw-dir) set to s3://<bucket>/raw/kaggle downloads both files to a
temporary folder with their original names, and the rest of the ETL reads
them from there as from any folder: same checks, same sample.
"""

import tempfile
from pathlib import Path

from securepay_seed.kaggle_etl.config import FRAUDTEST_ARCHIVO, PAYSIM_ARCHIVO

# Key of each file under the prefix, as securepay-csv's loader writes them
# (securepay_csv.kaggle_datasets): raw/kaggle/paysim/paysim.csv and
# raw/kaggle/sparkov/fraudtest/fraudTest.csv.
KEYS = {
    PAYSIM_ARCHIVO: "paysim/paysim.csv",
    FRAUDTEST_ARCHIVO: "sparkov/fraudtest/fraudTest.csv",
}


def is_s3(path) -> bool:
    return str(path).startswith("s3://")


def split(uri: str) -> tuple[str, str]:
    """s3://bucket/a/b/ -> ("bucket", "a/b")."""
    bucket, _, prefix = uri.removeprefix("s3://").partition("/")
    if not bucket:
        raise ValueError(f"{uri} has no bucket")
    return bucket, prefix.strip("/")


def download(uri: str, target: Path | None = None, client=None) -> Path:
    """Both CSVs of `uri` into `target` (a new temporary folder by default)
    with the names the ETL expects. Returns the folder."""
    bucket, prefix = split(uri)
    if client is None:
        # Imported here: a local run never needs boto3.
        from securepay_shared.aws import get_client

        client = get_client("s3")
    target = Path(target or tempfile.mkdtemp(prefix="kaggle-"))
    target.mkdir(parents=True, exist_ok=True)
    for name, key in KEYS.items():
        full_key = f"{prefix}/{key}" if prefix else key
        print(f"  s3://{bucket}/{full_key} -> {target / name}")
        client.download_file(bucket, full_key, str(target / name))
    return target
