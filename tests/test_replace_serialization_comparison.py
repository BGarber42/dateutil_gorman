"""Tests for replace(), fromisoformat (ISO 8601 conformant), round-trip/symmetry, and comparisons."""

from datetime import time
import pytest
from dateutil_gorman.types import GormanDate, Intermission


def test_gorman_date_replace_year() -> None:
    """GormanDate.replace() should return new instance with updated year."""
    g = GormanDate(year=2024, month=3, day=15)
    g2 = g.replace(year=2025)
    assert g2.year == 2025
    assert g2.month == 3
    assert g2.day == 15
    assert g.year == 2024


def test_gorman_date_replace_month_day_time() -> None:
    """GormanDate.replace() should support month, day, time."""
    g = GormanDate(year=2024, month=1, day=1, time=time(12, 0))
    g2 = g.replace(month=13, day=28, time=time(23, 59))
    assert g2.month == 13 and g2.day == 28 and g2.time == time(23, 59)
    assert g.time == time(12, 0)


def test_intermission_replace() -> None:
    """Intermission.replace() should return new instance with updated fields."""
    i = Intermission(year=2024, day=1)
    i2 = i.replace(year=2023)
    assert i2.year == 2023 and i2.day == 1
    i3 = i.replace(day=2)
    assert i3.year == 2024 and i3.day == 2


def test_gorman_date_fromisoformat_accepts_iso8601_gregorian() -> None:
    """GormanDate.fromisoformat() accepts ISO 8601 (Gregorian) YYYY-MM-DD and returns GormanDate."""
    g = GormanDate.fromisoformat("2024-01-01")
    assert g == GormanDate(2024, 1, 1)
    g2 = GormanDate.fromisoformat("2024-03-15")
    assert g2 == GormanDate(2024, 3, 19)


def test_gorman_date_fromisoformat_raises_for_intermission_day() -> None:
    """GormanDate.fromisoformat() raises for Gregorian dates that are intermission days."""
    with pytest.raises(ValueError, match="intermission"):
        GormanDate.fromisoformat("2024-12-30")
    with pytest.raises(ValueError, match="intermission"):
        GormanDate.fromisoformat("2024-12-31")


def test_gorman_date_fromisoformat_raises_for_invalid_iso8601() -> None:
    """GormanDate.fromisoformat() raises for invalid ISO 8601 (uses date.fromisoformat)."""
    with pytest.raises(ValueError):
        GormanDate.fromisoformat("2024-I1")
    with pytest.raises(ValueError):
        GormanDate.fromisoformat("not-a-date")


def test_gorman_date_fromisoformat_round_trip_via_gregorian() -> None:
    """GormanDate fromisoformat(gregorian_iso) then to_gregorian().isoformat() round-trips."""
    s = "2024-06-10"
    g = GormanDate.fromisoformat(s)
    assert g.to_gregorian().isoformat() == s


def test_from_gorman_week_calendar() -> None:
    """GormanDate.from_gorman_week_calendar(year, week 1-52, weekday) creates correct date."""
    g = GormanDate.from_gorman_week_calendar(2024, 1, 1)
    assert g.year == 2024 and g.week_of_year() == 1 and g.isoweekday() == 1
    g2 = GormanDate.from_gorman_week_calendar(2024, 52, 7)
    assert g2.week_of_year() == 52 and g2.isoweekday() == 7


def test_gorman_week_calendar_round_trip() -> None:
    """GormanDate gorman_week_calendar then from_gorman_week_calendar round-trips."""
    g = GormanDate(2024, 5, 15)
    y, w, d = g.gorman_week_calendar()
    assert GormanDate.from_gorman_week_calendar(y, w, d) == g


def test_intermission_fromordinal() -> None:
    """Intermission.fromordinal() should create Intermission for intermission ordinals."""
    i = Intermission(2024, 1)
    ordinal = i.toordinal()
    i2 = Intermission.fromordinal(ordinal)
    assert i2 == i


def test_intermission_fromordinal_raises_for_gorman_date() -> None:
    """Intermission.fromordinal() should raise for non-intermission ordinal."""
    g = GormanDate(2024, 1, 1)
    with pytest.raises(ValueError, match="intermission|Gorman date"):
        Intermission.fromordinal(g.toordinal())


def test_gorman_date_less_than_gorman_date() -> None:
    """GormanDate < GormanDate should compare by ordinal."""
    g1 = GormanDate(2024, 1, 1)
    g2 = GormanDate(2024, 1, 15)
    assert g1 < g2
    assert g1 <= g2
    assert g2 > g1
    assert g2 >= g1
    assert not (g1 < g1)
    assert g1 <= g1


def test_gorman_date_vs_intermission_ordering() -> None:
    """GormanDate and Intermission should be ordered by ordinal."""
    g = GormanDate(2024, 13, 28)
    i1 = Intermission(2024, 1)
    i2 = Intermission(2024, 2)
    assert g < i1
    assert i1 < i2
    assert g <= i1 <= i2


def test_intermission_equals_intermission() -> None:
    """Intermission == Intermission by field equality."""
    assert Intermission(2024, 1) == Intermission(2024, 1)
    assert Intermission(2024, 1) != Intermission(2024, 2)
    assert Intermission(2024, 1) != Intermission(2023, 1)


def test_gorman_date_not_equal_intermission() -> None:
    """GormanDate and Intermission should not be equal even if same ordinal (different types)."""
    g = GormanDate(2024, 13, 28)
    i = Intermission(2024, 1)
    assert g != i
    assert not (g == i)


def test_comparison_with_wrong_type_returns_not_implemented() -> None:
    """Comparison with non-GormanDate/Intermission should return NotImplemented."""
    g = GormanDate(2024, 1, 1)
    assert g.__lt__(None) is NotImplemented
    assert g.__lt__(2024) is NotImplemented
    assert g.__lt__("2024-01-01") is NotImplemented
