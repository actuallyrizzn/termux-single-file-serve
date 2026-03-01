"""Unit tests for url_safe_basename."""
import pytest

from serve import url_safe_basename


@pytest.mark.unit
class TestUrlSafeBasename:
    def test_simple_name_unchanged(self):
        assert url_safe_basename("/tmp/foo.apk") == "foo.apk"
        assert url_safe_basename("README.md") == "README.md"

    def test_spaces_to_underscores(self):
        assert url_safe_basename("/path/foo bar.apk") == "foo_bar.apk"
        assert url_safe_basename("my file (1).apk") == "my_file_1_.apk"

    def test_unsafe_chars_replaced(self):
        assert url_safe_basename("a%b#c.d") == "a_b_c.d"
        assert url_safe_basename("file with spaces.txt") == "file_with_spaces.txt"

    def test_leading_slash_stripped(self):
        assert url_safe_basename("/single") == "single"

    def test_slash_only_returns_download(self):
        """Path '/' yields basename '' -> sanitization gives empty -> 'download'."""
        assert url_safe_basename("/") == "download"

    def test_multiple_underscores_collapsed(self):
        assert url_safe_basename("a   b.apk") == "a_b.apk"

    def test_empty_basename_fallback(self):
        # Path that yields empty after sanitization (only underscores)
        assert url_safe_basename("/___") == "download"
        assert url_safe_basename("   ") == "download"

    def test_unicode_stripped_to_ascii_safe(self):
        # Only \w, -, . kept (ASCII)
        assert url_safe_basename("fïle.apk") == "f_le.apk"
