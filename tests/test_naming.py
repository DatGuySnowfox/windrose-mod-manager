"""Tests for windrose_deployer.utils.naming."""
import pytest
from windrose_deployer.utils.naming import sanitize_mod_id, timestamp_slug, mod_display_name_from_archive


class TestSanitizeModId:
    def test_basic(self):
        assert sanitize_mod_id("My Cool Mod") == "my_cool_mod"

    def test_special_chars(self):
        assert sanitize_mod_id("mod@v1.2!") == "mod_v1.2"

    def test_empty_string(self):
        result = sanitize_mod_id("")
        assert result.startswith("mod_")

    def test_whitespace_only(self):
        result = sanitize_mod_id("   ")
        assert result.startswith("mod_")

    def test_preserves_dots_and_hyphens(self):
        assert sanitize_mod_id("mod-name.v2") == "mod-name.v2"

    def test_collapses_underscores(self):
        assert sanitize_mod_id("a   b   c") == "a_b_c"


class TestTimestampSlug:
    def test_format(self):
        slug = timestamp_slug()
        assert len(slug) == 15  # YYYYMMDD_HHMMSS
        assert slug[8] == "_"


class TestModDisplayName:
    def test_basic(self):
        assert mod_display_name_from_archive("cool-mod-v2.zip") == "Cool Mod V2"

    def test_underscores(self):
        assert mod_display_name_from_archive("my_mod_pack.7z") == "My Mod Pack"
