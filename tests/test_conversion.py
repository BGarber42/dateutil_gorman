"""Tests for Gorman calendar conversion functions."""

from datetime import date, datetime
import pytest
from dateutil_gorman.conversion import (
    gregorian_to_gorman,
    gorman_to_gregorian,
    intermission_to_gregorian,
)


def test_january_1_2024_converts_to_march_1_2024() -> None:
    """Gregorian 1 January 2024 should convert to Gorman 1 March 2024."""
    gregorian = date(2024, 1, 1)
    result = gregorian_to_gorman(gregorian)
    
    assert result.year == 2024
    assert result.month == 1
    assert result.day == 1


def test_february_29_2024_converts_to_may_4_2024() -> None:
    """Gregorian 29 February 2024 (leap day) should convert to Gorman 4 May 2024."""
    gregorian = date(2024, 2, 29)
    result = gregorian_to_gorman(gregorian)
    
    assert result.year == 2024
    assert result.month == 3  # May is month 3 (March=1, April=2, May=3)
    assert result.day == 4


def test_invalid_gregorian_feb_29_non_leap_year_cannot_be_constructed() -> None:
    """February 29 in a non-leap year is not a valid Gregorian date.

    Python's date constructor raises ValueError, so such a value can never
    be passed to gregorian_to_gorman. This test documents that invalid
    Gregorian dates are rejected at construction time.
    """
    with pytest.raises(ValueError):
        date(2023, 2, 29)


def test_december_30_2024_converts_to_intermission_1() -> None:
    """Gregorian 30 December 2024 (leap year) should convert to Intermission 1."""
    gregorian = date(2024, 12, 30)
    result = gregorian_to_gorman(gregorian)
    
    assert result.year == 2024
    assert result.day == 1


def test_december_31_2024_converts_to_intermission_2() -> None:
    """Gregorian 31 December 2024 (leap year) should convert to Intermission 2."""
    gregorian = date(2024, 12, 31)
    result = gregorian_to_gorman(gregorian)
    
    assert result.year == 2024
    assert result.day == 2


def test_december_31_2023_converts_to_intermission() -> None:
    """Gregorian 31 December 2023 (non-leap year) should convert to Intermission."""
    gregorian = date(2023, 12, 31)
    result = gregorian_to_gorman(gregorian)
    
    assert result.year == 2023
    assert result.day == 1


def test_march_1_2024_converts_to_january_1_2024() -> None:
    """Gorman 1 March 2024 should convert to Gregorian 1 January 2024."""
    result = gorman_to_gregorian(2024, 1, 1)
    
    assert result == date(2024, 1, 1)


def test_may_4_2024_converts_to_february_29_2024() -> None:
    """Gorman 4 May 2024 should convert to Gregorian 29 February 2024."""
    result = gorman_to_gregorian(2024, 3, 4)  # May is month 3
    
    assert result == date(2024, 2, 29)


def test_intermission_1_2024_converts_to_december_30_2024() -> None:
    """Intermission 1 in 2024 (leap year) should convert to Gregorian 30 December 2024."""
    result = intermission_to_gregorian(2024, 1)
    
    assert result == date(2024, 12, 30)


def test_intermission_2_2024_converts_to_december_31_2024() -> None:
    """Intermission 2 in 2024 (leap year) should convert to Gregorian 31 December 2024."""
    result = intermission_to_gregorian(2024, 2)
    
    assert result == date(2024, 12, 31)


def test_intermission_1_2023_converts_to_december_31_2023() -> None:
    """Intermission 1 in 2023 (non-leap year) should convert to Gregorian 31 December 2023."""
    result = intermission_to_gregorian(2023, 1)
    
    assert result == date(2023, 12, 31)


def test_leap_year_intermission_1_and_2_are_two_separate_24h_days() -> None:
    """In leap years, Intermission 1 and Intermission 2 are two separate 24-hour days, not one 48h day."""
    from dateutil_gorman.types import Intermission
    
    intermission_1 = Intermission(year=2024, day=1)
    intermission_2 = Intermission(year=2024, day=2)
    d1 = intermission_1.to_gregorian()
    d2 = intermission_2.to_gregorian()
    
    assert d1 == date(2024, 12, 30)
    assert d2 == date(2024, 12, 31)
    assert (d2 - d1).days == 1
    assert intermission_2.toordinal() - intermission_1.toordinal() == 1


def test_round_trip_conversion() -> None:
    """Converting Gregorian to Gorman and back should return the original date."""
    test_dates = [
        date(2024, 1, 1),
        date(2024, 1, 28),
        date(2024, 2, 14),
        date(2024, 2, 29),
        date(2024, 6, 15),
        date(2024, 12, 28),
    ]
    
    for gregorian in test_dates:
        gorman = gregorian_to_gorman(gregorian)
        if hasattr(gorman, 'month'):  # Not an Intermission
            result = gorman_to_gregorian(gorman.year, gorman.month, gorman.day)
            assert result == gregorian


def test_accepts_datetime() -> None:
    """gregorian_to_gorman should accept datetime objects and preserve time."""
    dt = datetime(2024, 1, 1, 12, 30, 45)
    result = gregorian_to_gorman(dt)
    
    assert result.year == 2024
    assert result.month == 1
    assert result.day == 1
    assert result.time == dt.time()


def test_datetime_preserves_time_components() -> None:
    """gregorian_to_gorman should preserve time components when converting from datetime."""
    dt1 = datetime(2024, 1, 1, 0, 0, 0)
    dt2 = datetime(2024, 1, 1, 23, 59, 59)
    dt3 = datetime(2024, 1, 1, 12, 30, 45, 123456)
    
    result1 = gregorian_to_gorman(dt1)
    result2 = gregorian_to_gorman(dt2)
    result3 = gregorian_to_gorman(dt3)
    
    assert result1.year == result2.year == result3.year == 2024
    assert result1.month == result2.month == result3.month == 1
    assert result1.day == result2.day == result3.day == 1
    
    assert result1.time == dt1.time()
    assert result2.time == dt2.time()
    assert result3.time == dt3.time()
    
    assert result1.time != result2.time != result3.time


def test_datetime_with_intermission_day() -> None:
    """datetime objects for intermission days should convert correctly and preserve time."""
    dt = datetime(2024, 12, 30, 15, 30, 0)
    result = gregorian_to_gorman(dt)
    
    assert result.year == 2024
    assert result.day == 1
    assert result.time == dt.time()


def test_datetime_with_leap_day() -> None:
    """datetime objects for leap day should convert correctly and preserve time."""
    dt = datetime(2024, 2, 29, 10, 15, 30)
    result = gregorian_to_gorman(dt)
    
    assert result.year == 2024
    assert result.month == 3
    assert result.day == 4
    assert result.time == dt.time()


def test_invalid_datetime_feb_29_non_leap_year_cannot_be_constructed() -> None:
    """February 29 in a non-leap year is not a valid datetime.

    Python's datetime constructor raises ValueError, so such a value can never
    be passed to gregorian_to_gorman. This test documents that invalid
    datetime values are rejected at construction time.
    """
    with pytest.raises(ValueError):
        datetime(2023, 2, 29, 12, 0, 0)


def test_datetime_round_trip_conversion() -> None:
    """Converting datetime to Gorman and back should preserve both date and time."""
    test_datetimes = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 12, 30, 45),
        datetime(2024, 2, 29, 23, 59, 59),
        datetime(2024, 12, 30, 15, 30, 0),
    ]
    
    for dt in test_datetimes:
        gorman = gregorian_to_gorman(dt)
        result_datetime = gorman.to_gregorian_datetime()
        assert result_datetime == dt


def test_date_objects_have_no_time() -> None:
    """date objects (not datetime) should result in GormanDate/Intermission with no time."""
    d = date(2024, 1, 1)
    result = gregorian_to_gorman(d)
    
    assert result.time is None


def test_boundary_28_march_to_28_january() -> None:
    """Gorman 28 March (month 1 day 28) should convert to Gregorian 28 January."""
    result = gorman_to_gregorian(2024, 1, 28)
    
    assert result == date(2024, 1, 28)


def test_boundary_1_april_to_29_january() -> None:
    """Gorman 1 April (month 2 day 1) should convert to Gregorian 29 January."""
    result = gorman_to_gregorian(2024, 2, 1)
    
    assert result == date(2024, 1, 29)


def test_28_gormanuary_non_leap() -> None:
    """Gorman 28 Gormanuary in non-leap year should convert to Gregorian 30 December."""
    result = gorman_to_gregorian(2023, 13, 28)
    
    assert result == date(2023, 12, 30)  # Day 364 of 365-day year


def test_28_gormanuary_leap() -> None:
    """Gorman 28 Gormanuary in leap year should convert to Gregorian 29 December."""
    result = gorman_to_gregorian(2024, 13, 28)
    
    assert result == date(2024, 12, 29)  # Day 364 of 366-day year
