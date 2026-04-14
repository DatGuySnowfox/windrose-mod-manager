"""Tests for archive inspection / classification logic."""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from windrose_deployer.models.archive_info import ArchiveInfo, ArchiveEntry, ArchiveType
from windrose_deployer.core.archive_inspector import _classify, _detect_variants, _detect_root_prefix, _suggest_target


def _info_with_entries(entries: list[ArchiveEntry]) -> ArchiveInfo:
    info = ArchiveInfo(archive_path="test.zip")
    for e in entries:
        info.entries.append(e)
        if e.is_dir:
            continue
        if e.is_pak:
            info.pak_entries.append(e)
        elif e.is_utoc or e.is_ucas:
            info.companion_entries.append(e)
        else:
            info.loose_entries.append(e)
    return info


class TestClassify:
    def test_pak_only(self):
        info = _info_with_entries([
            ArchiveEntry(path="mod.pak", size=100),
        ])
        _classify(info)
        assert info.archive_type == ArchiveType.PAK_ONLY

    def test_loose_files(self):
        info = _info_with_entries([
            ArchiveEntry(path="config/settings.ini", size=50),
        ])
        _classify(info)
        assert info.archive_type == ArchiveType.LOOSE_FILES

    def test_mixed(self):
        info = _info_with_entries([
            ArchiveEntry(path="mod.pak", size=100),
            ArchiveEntry(path="readme.txt", size=10),
        ])
        _classify(info)
        assert info.archive_type == ArchiveType.MIXED

    def test_empty_archive(self):
        info = _info_with_entries([
            ArchiveEntry(path="folder/", is_dir=True),
        ])
        _classify(info)
        assert info.archive_type == ArchiveType.UNKNOWN

    def test_pak_with_utoc_ucas(self):
        info = _info_with_entries([
            ArchiveEntry(path="mod.pak", size=100),
            ArchiveEntry(path="mod.utoc", size=50),
            ArchiveEntry(path="mod.ucas", size=200),
        ])
        _classify(info)
        assert info.archive_type == ArchiveType.PAK_ONLY


class TestDetectVariants:
    def test_numbered_variants(self):
        info = _info_with_entries([
            ArchiveEntry(path="mod_x02.pak", size=100),
            ArchiveEntry(path="mod_x03.pak", size=100),
            ArchiveEntry(path="mod_x04.pak", size=100),
        ])
        _classify(info)
        _detect_variants(info)
        assert len(info.variant_groups) >= 1

    def test_single_pak_no_variants(self):
        info = _info_with_entries([
            ArchiveEntry(path="mod.pak", size=100),
        ])
        _classify(info)
        _detect_variants(info)
        assert len(info.variant_groups) == 0


class TestDetectRootPrefix:
    def test_single_non_game_folder(self):
        info = _info_with_entries([
            ArchiveEntry(path="MyMod/mod.pak", size=100),
        ])
        _detect_root_prefix(info)
        assert info.root_prefix == "MyMod/"

    def test_game_root_folder(self):
        info = _info_with_entries([
            ArchiveEntry(path="R5/Content/Paks/mod.pak", size=100),
        ])
        _detect_root_prefix(info)
        assert info.root_prefix == ""

    def test_flat_archive(self):
        info = _info_with_entries([
            ArchiveEntry(path="mod.pak", size=100),
        ])
        _detect_root_prefix(info)
        assert info.root_prefix == ""


class TestSuggestTarget:
    def test_pak_only_suggests_paks(self):
        info = _info_with_entries([
            ArchiveEntry(path="mod.pak", size=100),
        ])
        _classify(info)
        _suggest_target(info)
        assert info.suggested_target == "paks"

    def test_loose_files_suggests_root(self):
        info = _info_with_entries([
            ArchiveEntry(path="R5/Content/config.ini", size=50),
        ])
        _classify(info)
        _suggest_target(info)
        assert info.suggested_target == "root"
