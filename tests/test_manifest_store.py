"""Tests for windrose_deployer.core.manifest_store."""
import json
import pytest
from pathlib import Path

from windrose_deployer.core.manifest_store import ManifestStore
from windrose_deployer.models.mod_install import ModInstall


def _make_mod(mod_id: str = "test_mod", files: list[str] | None = None) -> ModInstall:
    return ModInstall(
        mod_id=mod_id,
        display_name=mod_id.replace("_", " ").title(),
        source_archive="test.zip",
        archive_hash="abc123",
        install_type="pak_only",
        selected_variant=None,
        targets=["client"],
        installed_files=files or ["C:/mods/test.pak"],
        backed_up_files=[],
        enabled=True,
    )


class TestManifestStore:
    def test_add_and_get(self, tmp_path):
        store = ManifestStore(tmp_path)
        mod = _make_mod()
        store.add_mod(mod)
        assert store.get_mod("test_mod") is not None
        assert store.get_mod("nonexistent") is None

    def test_persistence(self, tmp_path):
        store = ManifestStore(tmp_path)
        store.add_mod(_make_mod())

        store2 = ManifestStore(tmp_path)
        assert store2.get_mod("test_mod") is not None
        assert store2.get_mod("test_mod").display_name == "Test Mod"

    def test_remove(self, tmp_path):
        store = ManifestStore(tmp_path)
        store.add_mod(_make_mod())
        removed = store.remove_mod("test_mod")
        assert removed is not None
        assert store.get_mod("test_mod") is None

    def test_update(self, tmp_path):
        store = ManifestStore(tmp_path)
        mod = _make_mod()
        store.add_mod(mod)
        mod.enabled = False
        store.update_mod(mod)

        store2 = ManifestStore(tmp_path)
        assert store2.get_mod("test_mod").enabled is False

    def test_files_map_excludes_disabled(self, tmp_path):
        store = ManifestStore(tmp_path)
        mod = _make_mod(files=["C:/game/mods/a.pak"])
        mod.enabled = False
        store.add_mod(mod)
        assert store.get_files_map() == {}

    def test_files_map_includes_enabled(self, tmp_path):
        store = ManifestStore(tmp_path)
        store.add_mod(_make_mod(files=["C:/game/mods/a.pak"]))
        fmap = store.get_files_map()
        assert "C:/game/mods/a.pak" in fmap

    def test_corrupt_json_recovery(self, tmp_path):
        state_file = tmp_path / "app_state.json"
        state_file.write_text("{invalid json", encoding="utf-8")
        store = ManifestStore(tmp_path)
        assert store.list_mods() == []

    def test_corrupt_entry_skipped(self, tmp_path):
        state_file = tmp_path / "app_state.json"
        state_file.write_text(json.dumps({
            "mods": [
                {"bad_key": "no_mod_id"},
                _make_mod().to_dict(),
            ],
            "history": [],
        }), encoding="utf-8")
        store = ManifestStore(tmp_path)
        assert len(store.list_mods()) == 1
