"""The ETL reads the CSVs from S3 when it runs in AWS. No AWS here: a fake
client writes what it would download."""

from pathlib import Path

import pytest

from securepay_seed.kaggle_etl import etl
from securepay_seed.kaggle_etl.config import FRAUDTEST_ARCHIVO, PAYSIM_ARCHIVO
from securepay_seed.kaggle_etl.s3 import download, is_s3, split


class FakeS3:
    def __init__(self):
        self.calls = []

    def download_file(self, bucket, key, filename):
        self.calls.append((bucket, key))
        Path(filename).write_text(key, encoding="utf-8")


def test_split_takes_the_bucket_and_the_prefix():
    assert split("s3://lake/raw/kaggle/") == ("lake", "raw/kaggle")
    assert split("s3://lake") == ("lake", "")
    with pytest.raises(ValueError):
        split("s3:///raw")


def test_is_s3():
    assert is_s3("s3://lake/raw/kaggle")
    assert not is_s3("data/kaggle")
    assert not is_s3(Path("data/kaggle"))


def test_download_uses_the_keys_of_securepay_csv(tmp_path):
    client = FakeS3()

    folder = download("s3://lake/raw/kaggle", tmp_path, client)

    assert folder == tmp_path
    assert client.calls == [
        ("lake", "raw/kaggle/paysim/paysim.csv"),
        ("lake", "raw/kaggle/sparkov/fraudtest/fraudTest.csv"),
    ]
    # Saved with the names the ETL looks for.
    assert (tmp_path / PAYSIM_ARCHIVO).read_text() == "raw/kaggle/paysim/paysim.csv"
    assert (tmp_path / FRAUDTEST_ARCHIVO).is_file()


def test_download_without_prefix(tmp_path):
    client = FakeS3()
    download("s3://lake", tmp_path, client)
    assert client.calls[0] == ("lake", "paysim/paysim.csv")


def test_an_s3_raw_dir_is_downloaded_first(monkeypatch, tmp_path):
    asked = []

    def fake_download(uri):
        asked.append(uri)
        return tmp_path

    monkeypatch.delenv("HIST_RAW_DIR", raising=False)
    assert etl.resolver_raw("s3://lake/raw/kaggle", fake_download) == tmp_path
    assert asked == ["s3://lake/raw/kaggle"]


def test_hist_raw_dir_can_be_s3(monkeypatch, tmp_path):
    monkeypatch.setenv("HIST_RAW_DIR", "s3://lake/raw/kaggle")
    assert etl.resolver_raw(None, lambda uri: tmp_path) == tmp_path


def test_a_local_raw_dir_is_used_as_is(monkeypatch, tmp_path):
    monkeypatch.delenv("HIST_RAW_DIR", raising=False)

    def never(uri):
        raise AssertionError("must not download")

    assert etl.resolver_raw(str(tmp_path), never) == tmp_path
