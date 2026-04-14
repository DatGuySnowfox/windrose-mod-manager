"""Tests for installer safety functions."""
import pytest

from windrose_deployer.core.installer import _is_safe_relative_path


class TestPathTraversalProtection:
    def test_normal_path(self):
        assert _is_safe_relative_path("mods/test.pak") is True

    def test_dotdot(self):
        assert _is_safe_relative_path("../etc/passwd") is False

    def test_nested_dotdot(self):
        assert _is_safe_relative_path("mods/../../secret.txt") is False

    def test_absolute_posix(self):
        assert _is_safe_relative_path("/etc/passwd") is False

    def test_absolute_windows(self):
        assert _is_safe_relative_path("C:\\Windows\\System32\\file.dll") is False

    def test_simple_filename(self):
        assert _is_safe_relative_path("test.pak") is True

    def test_deep_relative(self):
        assert _is_safe_relative_path("R5/Content/Paks/~mods/test.pak") is True

    def test_backslash_path(self):
        assert _is_safe_relative_path("mods\\test.pak") is True

    def test_empty(self):
        assert _is_safe_relative_path("") is True
