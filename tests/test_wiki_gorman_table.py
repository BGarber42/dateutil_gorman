"""Verify conversions against the Gorman Calendar wiki table.

Reference: https://calendars.fandom.com/wiki/Gorman_Calendar
Table: Traditional to Gorman Calendar Conversion (Gregorian DD/MM/YYYY → Gorman).
"""

from datetime import date

import pytest

from dateutil_gorman.conversion import gregorian_to_gorman, gorman_to_gregorian
from dateutil_gorman.types import Intermission


_WIKI_TABLE_GREGORIAN_TO_GORMAN: list[tuple[tuple[int, int, int], tuple[int, int, int] | tuple[str, int]]] = [
    ((2024, 1, 1), (2024, 1, 1)),
    ((2024, 1, 28), (2024, 1, 28)),
    ((2024, 1, 29), (2024, 2, 1)),
    ((2024, 2, 14), (2024, 2, 17)),
    ((2024, 2, 29), (2024, 3, 4)),
    ((2024, 4, 1), (2024, 4, 8)),
    ((2024, 4, 8), (2024, 4, 15)),
    ((2024, 6, 15), (2024, 6, 27)),
    ((2024, 7, 4), (2024, 7, 18)),
    ((2024, 12, 25), (2024, 13, 24)),
    ((2024, 12, 28), (2024, 13, 27)),
    ((2024, 12, 29), (2024, 13, 28)),
    ((2024, 12, 30), ("intermission", 1)),
    ((2024, 12, 31), ("intermission", 2)),
    ((2023, 12, 31), ("intermission", 1)),
]


@pytest.mark.parametrize(
    ("gregorian_ymd", "expected_gorman"),
    [
        (g, e) for g, e in _WIKI_TABLE_GREGORIAN_TO_GORMAN
    ],
    ids=[
        f"Gregorian {g[0]}-{g[1]:02d}-{g[2]:02d}"
        for g, _ in _WIKI_TABLE_GREGORIAN_TO_GORMAN
    ],
)
def test_gregorian_to_gorman_matches_wiki_table(
    gregorian_ymd: tuple[int, int, int],
    expected_gorman: tuple[int, int, int] | tuple[str, int],
) -> None:
    """Gregorian → Gorman conversion matches the Calendar Wiki conversion table."""
    year, month, day = gregorian_ymd
    gregorian = date(year, month, day)
    result = gregorian_to_gorman(gregorian)

    if expected_gorman[0] == "intermission":
        assert isinstance(result, Intermission)
        assert result.year == year
        assert result.day == expected_gorman[1]
    else:
        exp_year, exp_month, exp_day = expected_gorman
        assert result.year == exp_year
        assert result.month == exp_month
        assert result.day == exp_day


_WIKI_TABLE_GORMAN_TO_GREGORIAN: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = [
    ((2024, 1, 1), (2024, 1, 1)),
    ((2024, 1, 28), (2024, 1, 28)),
    ((2024, 2, 1), (2024, 1, 29)),
    ((2024, 2, 17), (2024, 2, 14)),
    ((2024, 3, 4), (2024, 2, 29)),
    ((2024, 4, 8), (2024, 4, 1)),
    ((2024, 4, 15), (2024, 4, 8)),
    ((2024, 6, 27), (2024, 6, 15)),
    ((2024, 7, 18), (2024, 7, 4)),
    ((2024, 13, 24), (2024, 12, 25)),
    ((2024, 13, 27), (2024, 12, 28)),
    ((2024, 13, 28), (2024, 12, 29)),
]


@pytest.mark.parametrize(
    ("gorman_ymd", "expected_gregorian_ymd"),
    [
        (g, e) for g, e in _WIKI_TABLE_GORMAN_TO_GREGORIAN
    ],
    ids=[
        f"Gorman {g[0]} month {g[1]} day {g[2]}"
        for g, _ in _WIKI_TABLE_GORMAN_TO_GREGORIAN
    ],
)
def test_gorman_to_gregorian_matches_wiki_table(
    gorman_ymd: tuple[int, int, int],
    expected_gregorian_ymd: tuple[int, int, int],
) -> None:
    """Gorman → Gregorian conversion matches the Calendar Wiki conversion table."""
    g_year, g_month, g_day = gorman_ymd
    result = gorman_to_gregorian(g_year, g_month, g_day)
    exp_year, exp_month, exp_day = expected_gregorian_ymd
    expected = date(exp_year, exp_month, exp_day)
    assert result == expected
