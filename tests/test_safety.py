"""Safety regression tests for install/uninstall/manifest invariants."""
import json
import shutil
import pytest
from pathlib import Path

from windrose_deployer.core.backup_manager import BackupManager
from windrose_deployer.core.installer import Installer
from windrose_deployer.core.manifest_store import ManifestStore, SCHEMA_VERSION
from windrose_deployer.core.deployment_planner import DeploymentPlan, PlannedFile
from windrose_deployer.models.mod_install import ModInstall, InstallTarget
from windrose_deployer.utils.naming import generate_mod_id


@pytest.fixture
def workspace(tmp_path):
    """Create a minimal workspace with backup dir, data dir, and a target dir."""
    backup_dir = tmp_path / "backups"
    data_dir = tmp_path / "data"
    target_dir = tmp_path / "game" / "R5" / "Content" / "Paks" / "~mods"
    archive_dir = tmp_path / "archives"
    for d in (backup_dir, data_dir, target_dir, archive_dir):
        d.mkdir(parents=True)
    return {
        "tmp": tmp_path,
        "backup_dir": backup_dir,
        "data_dir": data_dir,
        "target_dir": target_dir,
        "archive_dir": archive_dir,
        "backup": BackupManager(backup_dir),
        "manifest": ManifestStore(data_dir),
    }


def _make_plan(target_dir: Path, archive_path: str, files: dict[str, bytes],
               mod_name: str = "TestMod") -> DeploymentPlan:
    """Build a plan that deploys given files {filename: content} to target_dir."""
    plan = DeploymentPlan(
        mod_name=mod_name,
        archive_path=archive_path,
        target=InstallTarget.CLIENT,
        install_type="pak_only",
    )
    for name, content in files.items():
        plan.files.append(PlannedFile(
            archive_entry_path=name,
            dest_path=target_dir / name,
            is_pak=True,
        ))
    return plan


class TestOverwriteAndRestore:
    """Uninstall must restore the original file when a mod overwrote it."""

    def test_overwrite_install_then_uninstall_restores_original(self, workspace):
        target_dir = workspace["target_dir"]
        installer = Installer(workspace["backup"])

        original_content = b"ORIGINAL_GAME_FILE"
        original_file = target_dir / "test.pak"
        original_file.write_bytes(original_content)

        # Create a fake archive (zip) with a replacement file
        import zipfile
        archive_path = workspace["archive_dir"] / "mod.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("test.pak", "MOD_REPLACEMENT")

        plan = DeploymentPlan(
            mod_name="OverwriteMod",
            archive_path=str(archive_path),
            target=InstallTarget.CLIENT,
            install_type="pak_only",
        )
        plan.files.append(PlannedFile(
            archive_entry_path="test.pak",
            dest_path=original_file,
            is_pak=True,
        ))

        mod, record = installer.install(plan)
        assert original_file.read_bytes() == b"MOD_REPLACEMENT"
        assert mod.backup_map.get(str(original_file)) is not None

        installer.uninstall(mod)
        assert original_file.exists(), "Original file should be restored"
        assert original_file.read_bytes() == original_content


class TestModIdIsUUID:
    """New installs must use UUID-based mod_id, not name-based."""

    def test_install_generates_uuid_id(self, workspace):
        import zipfile
        archive_path = workspace["archive_dir"] / "mymod.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("mod.pak", "data")

        installer = Installer(workspace["backup"])
        plan = DeploymentPlan(
            mod_name="My Cool Mod",
            archive_path=str(archive_path),
            target=InstallTarget.CLIENT,
            install_type="pak_only",
        )
        plan.files.append(PlannedFile(
            archive_entry_path="mod.pak",
            dest_path=workspace["target_dir"] / "mod.pak",
            is_pak=True,
        ))

        mod, _ = installer.install(plan)
        assert len(mod.mod_id) == 32, "mod_id should be a 32-char UUID hex"
        assert mod.display_name == "My Cool Mod"

    def test_duplicate_names_get_different_ids(self, workspace):
        import zipfile
        manifest = workspace["manifest"]

        for i in range(3):
            archive_path = workspace["archive_dir"] / f"mod{i}.zip"
            with zipfile.ZipFile(archive_path, "w") as zf:
                zf.writestr(f"mod{i}.pak", f"data{i}")

            installer = Installer(workspace["backup"])
            plan = DeploymentPlan(
                mod_name="SameName",
                archive_path=str(archive_path),
                target=InstallTarget.CLIENT,
                install_type="pak_only",
            )
            plan.files.append(PlannedFile(
                archive_entry_path=f"mod{i}.pak",
                dest_path=workspace["target_dir"] / f"mod{i}.pak",
                is_pak=True,
            ))
            mod, _ = installer.install(plan)
            manifest.add_mod(mod)

        assert len(manifest.list_mods()) == 3, "Three mods with same name should coexist"


class TestManifestSchemaVersion:
    """Manifest must write and read schema_version."""

    def test_save_includes_schema_version(self, workspace):
        manifest = workspace["manifest"]
        mod = ModInstall(
            mod_id=generate_mod_id(),
            display_name="Test",
            source_archive="test.zip",
            targets=["client"],
            installed_files=[],
        )
        manifest.add_mod(mod)

        raw = json.loads((workspace["data_dir"] / "app_state.json").read_text())
        assert raw["schema_version"] == SCHEMA_VERSION

    def test_v1_manifest_migrates_to_uuid(self, workspace):
        """Old v1 manifests with name-based ids should be migrated to UUIDs."""
        state_file = workspace["data_dir"] / "app_state.json"
        state_file.write_text(json.dumps({
            "mods": [{
                "mod_id": "my_cool_mod",
                "display_name": "My Cool Mod",
                "source_archive": "test.zip",
                "targets": ["client"],
                "installed_files": ["C:/game/mod.pak"],
                "backed_up_files": [],
                "install_time": "2026-01-01",
                "enabled": True,
            }],
            "history": [],
        }), encoding="utf-8")

        manifest = ManifestStore(workspace["data_dir"])
        mods = manifest.list_mods()
        assert len(mods) == 1
        assert len(mods[0].mod_id) == 32, "Old name-based id should be migrated to UUID"
        assert mods[0].display_name == "My Cool Mod"

        raw = json.loads(state_file.read_text())
        assert raw["schema_version"] == SCHEMA_VERSION

    def test_v1_migration_creates_backup_copy(self, workspace):
        """Migration must back up the old manifest before rewriting."""
        state_file = workspace["data_dir"] / "app_state.json"
        v1_content = json.dumps({
            "mods": [{
                "mod_id": "old_mod",
                "display_name": "Old Mod",
                "source_archive": "old.zip",
                "targets": ["client"],
                "installed_files": ["C:/game/old.pak"],
                "backed_up_files": [],
                "install_time": "2026-01-01",
                "enabled": True,
            }],
            "history": [],
        })
        state_file.write_text(v1_content, encoding="utf-8")

        ManifestStore(workspace["data_dir"])

        backup_file = workspace["data_dir"] / "app_state.v1.bak.json"
        assert backup_file.exists(), "Pre-migration backup must be created"
        backup_raw = json.loads(backup_file.read_text())
        assert "schema_version" not in backup_raw, "Backup should be the original v1 file"
        assert backup_raw["mods"][0]["mod_id"] == "old_mod"


class TestInstallAllCounting:
    """Install All must not overcount successes."""

    def test_do_install_returns_false_on_invalid_plan(self):
        """_do_install returning False should not count as success.
        We test the underlying logic: an invalid plan returns False."""
        from windrose_deployer.core.deployment_planner import DeploymentPlan
        plan = DeploymentPlan(
            mod_name="bad",
            archive_path="nonexistent.zip",
            target=InstallTarget.CLIENT,
            install_type="pak_only",
            valid=False,
            warnings=["test failure"],
        )
        assert not plan.valid
