import os
import pytest
from networksecurity.cloud.s3_syncer import S3Sync

def test_example():
    assert 1 + 1 == 2

def test_sync_folder_to_s3_command(monkeypatch):
    syncer = S3Sync()
    folder = "/tmp/test_folder"
    bucket_url = "s3://my-test-bucket"

    called = {}

    def fake_system(cmd):
        called['cmd'] = cmd
        return 0

    monkeypatch.setattr(os, "system", fake_system)
    syncer.sync_folder_to_s3(folder, bucket_url)
    assert called['cmd'] == f"aws s3 sync {folder} {bucket_url} "

def test_sync_folder_from_s3_command(monkeypatch):
    syncer = S3Sync()
    folder = "/tmp/test_folder"
    bucket_url = "s3://my-test-bucket"

    called = {}

    def fake_system(cmd):
        called['cmd'] = cmd
        return 0

    monkeypatch.setattr(os, "system", fake_system)
    syncer.sync_folder_from_s3(folder, bucket_url)
    assert called['cmd'] == f"aws s3 sync {bucket_url} {folder} "

