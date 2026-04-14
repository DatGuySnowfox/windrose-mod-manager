"""Tests for windrose_deployer.core.backup_manager."""
import time
import pytest
from pathlib import Path

from windrose_deployer.core.backup_manager import BackupManager, BackupRecord


class TestBackupManager:
    def test_backup_and_list(self, tmp_path):
        src_file = tmp_path / "original.txt"
        src_file.write_text("hello")
        backup_root = tmp_path / "backups"
        mgr = BackupManager(backup_root)

        record = mgr.backup_file(src_file, category="installs", description="test")
        assert record is not None
        assert Path(record.backup_path).is_file()
        assert len(mgr.list_backups()) == 1

    def test_restore(self, tmp_path):
        src_file = tmp_path / "original.txt"
        src_file.write_text("version1")
        backup_root = tmp_path / "backups"
        mgr = BackupManager(backup_root)

        record = mgr.backup_file(src_file, category="installs")
        src_file.write_text("version2")
        assert mgr.restore_backup(record)
        assert src_file.read_text() == "version1"

    def test_latest_backup(self, tmp_path):
        src_file = tmp_path / "data.json"
        src_file.write_text("v1")
        backup_root = tmp_path / "backups"
        mgr = BackupManager(backup_root)

        r1 = mgr.backup_file(src_file, category="server_config", description="first")
        time.sleep(0.05)
        src_file.write_text("v2")
        r2 = mgr.backup_file(src_file, category="server_config", description="second")

        latest = mgr.latest_backup(category="server_config")
        assert latest is not None
        assert latest.backup_id == r2.backup_id

    def test_latest_backup_empty(self, tmp_path):
        mgr = BackupManager(tmp_path / "backups")
        assert mgr.latest_backup() is None

    def test_backup_nonexistent_file(self, tmp_path):
        mgr = BackupManager(tmp_path / "backups")
        result = mgr.backup_file(tmp_path / "ghost.txt")
        assert result is None

    def test_category_filter(self, tmp_path):
        src = tmp_path / "f.txt"
        src.write_text("x")
        mgr = BackupManager(tmp_path / "backups")
        mgr.backup_file(src, category="installs")
        mgr.backup_file(src, category="server_config")
        mgr.backup_file(src, category="world_config")

        assert len(mgr.list_backups("installs")) == 1
        assert len(mgr.list_backups("server_config")) == 1
        assert len(mgr.list_backups("world_config")) == 1
        assert len(mgr.list_backups()) == 3

    def test_from_dict_resilient(self):
        record = BackupRecord.from_dict({"backup_id": "x", "timestamp": "t"})
        assert record.backup_id == "x"
        assert record.category == "installs"
