"""Tests for CLI commands."""

import pytest

from src.cli.commands import parse_task_id
from src.exceptions import InvalidIdError


class TestParseTaskId:
    """Tests for parse_task_id helper function."""

    def test_parse_valid_id(self):
        """parse_task_id returns integer for valid input."""
        result = parse_task_id("1")

        assert result == 1

    def test_parse_larger_id(self):
        """parse_task_id handles larger numbers."""
        result = parse_task_id("100")

        assert result == 100

    def test_parse_with_whitespace(self):
        """parse_task_id handles whitespace (pre-stripped)."""
        result = parse_task_id("5")

        assert result == 5

    def test_parse_zero_raises_error(self):
        """parse_task_id raises InvalidIdError for zero."""
        with pytest.raises(InvalidIdError):
            parse_task_id("0")

    def test_parse_negative_raises_error(self):
        """parse_task_id raises InvalidIdError for negative numbers."""
        with pytest.raises(InvalidIdError):
            parse_task_id("-1")

    def test_parse_non_numeric_raises_error(self):
        """parse_task_id raises InvalidIdError for non-numeric input."""
        with pytest.raises(InvalidIdError):
            parse_task_id("abc")

    def test_parse_empty_raises_error(self):
        """parse_task_id raises InvalidIdError for empty string."""
        with pytest.raises(InvalidIdError):
            parse_task_id("")

    def test_parse_float_raises_error(self):
        """parse_task_id raises InvalidIdError for float strings."""
        with pytest.raises(InvalidIdError):
            parse_task_id("1.5")
