"""Tests for date-like methods on GormanDate."""

from datetime import date
import pytest
from dateutil_gorman.types import GormanDate
from dateutil_gorman.conversion import gregorian_to_gorman


def test_weekday() -> None:
    """GormanDate.weekday() should return weekday (0=Monday, 6=Sunday)."""
    gorman = GormanDate(year=2024, month=1, day=1)
    gregorian = gorman.to_gregorian()
    
    assert gorman.weekday() == gregorian.weekday()
    assert gorman.weekday() == 0  # Jan 1, 2024 is a Monday


def test_isoweekday() -> None:
    """GormanDate.isoweekday() should return ISO weekday (1=Monday, 7=Sunday)."""
    gorman = GormanDate(year=2024, month=1, day=1)
    gregorian = gorman.to_gregorian()
    
    assert gorman.isoweekday() == gregorian.isoweekday()
    assert gorman.isoweekday() == 1  # Jan 1, 2024 is a Monday


def test_gorman_week_calendar() -> None:
    """GormanDate.gorman_week_calendar() should return (year, week 1-52, weekday)."""
    gorman = GormanDate(year=2024, month=1, day=1)
    result = gorman.gorman_week_calendar()
    assert result[0] == 2024
    assert result[1] == 1
    assert result[2] == gorman.isoweekday()


def test_fromordinal() -> None:
    """GormanDate.fromordinal() should create GormanDate from ordinal."""
    gorman1 = GormanDate.fromordinal(1)
    assert gorman1.year == 1
    assert gorman1.month == 1
    assert gorman1.day == 1
    
    gregorian1 = gorman1.to_gregorian()
    assert gregorian1 == date(1, 1, 1)


def test_fromordinal_round_trip() -> None:
    """Converting to ordinal and back should preserve the date."""
    test_dates = [
        GormanDate(year=2024, month=1, day=1),
        GormanDate(year=2024, month=1, day=28),
        GormanDate(year=2024, month=7, day=15),
        GormanDate(year=2024, month=13, day=28),
    ]
    
    for gorman in test_dates:
        ordinal = gorman.toordinal()
        reconstructed = GormanDate.fromordinal(ordinal)
        assert reconstructed == gorman


def test_toordinal() -> None:
    """GormanDate.toordinal() should return ordinal number."""
    gorman = GormanDate(year=2024, month=1, day=1)
    ordinal = gorman.toordinal()
    
    assert ordinal > 0
    assert isinstance(ordinal, int)
    
    reconstructed = GormanDate.fromordinal(ordinal)
    assert reconstructed == gorman


def test_weekday_various_dates() -> None:
    """weekday() should work correctly for various dates."""
    test_cases = [
        (date(2024, 1, 1), 0),  # Monday
        (date(2024, 1, 2), 1),  # Tuesday
        (date(2024, 1, 3), 2),  # Wednesday
        (date(2024, 1, 4), 3),  # Thursday
        (date(2024, 1, 5), 4),  # Friday
        (date(2024, 1, 6), 5),  # Saturday
        (date(2024, 1, 7), 6),  # Sunday
    ]
    
    for gregorian, expected_weekday in test_cases:
        gorman = gregorian_to_gorman(gregorian)
        if hasattr(gorman, 'month'):  # Not an Intermission
            assert gorman.weekday() == expected_weekday


def test_isoweekday_various_dates() -> None:
    """isoweekday() should work correctly for various dates."""
    test_cases = [
        (date(2024, 1, 1), 1),  # Monday
        (date(2024, 1, 2), 2),  # Tuesday
        (date(2024, 1, 3), 3),  # Wednesday
        (date(2024, 1, 4), 4),  # Thursday
        (date(2024, 1, 5), 5),  # Friday
        (date(2024, 1, 6), 6),  # Saturday
        (date(2024, 1, 7), 7),  # Sunday
    ]
    
    for gregorian, expected_isoweekday in test_cases:
        gorman = gregorian_to_gorman(gregorian)
        if hasattr(gorman, 'month'):  # Not an Intermission
            assert gorman.isoweekday() == expected_isoweekday


def test_fromordinal_intermission_raises_error() -> None:
    """fromordinal() should raise error for ordinals corresponding to intermission days."""
    from dateutil_gorman.types import Intermission
    
    intermission = Intermission(year=2024, day=1)
    ordinal = intermission.toordinal()
    
    with pytest.raises(ValueError, match="intermission"):
        GormanDate.fromordinal(ordinal)


def test_intermission_weekday_raises() -> None:
    """Intermission has no weekday; it is not part of the Monday–Sunday week."""
    from dateutil_gorman.types import Intermission
    
    intermission = Intermission(year=2024, day=1)
    with pytest.raises(ValueError, match="no weekday|not part of.*week"):
        intermission.weekday()


def test_intermission_isoweekday_raises() -> None:
    """Intermission has no weekday; it is not part of the Monday–Sunday week."""
    from dateutil_gorman.types import Intermission
    
    intermission = Intermission(year=2024, day=1)
    with pytest.raises(ValueError, match="no weekday|not part of.*week"):
        intermission.isoweekday()


def test_intermission_isocalendar_raises() -> None:
    """Intermission has no week or weekday; it is not part of any week."""
    from dateutil_gorman.types import Intermission
    
    intermission = Intermission(year=2024, day=1)
    with pytest.raises(ValueError, match="no week|not part of.*week"):
        intermission.isocalendar()


def test_intermission_toordinal() -> None:
    """Intermission.toordinal() should work correctly."""
    from dateutil_gorman.types import Intermission
    
    intermission = Intermission(year=2024, day=1)
    gregorian = intermission.to_gregorian()
    
    assert intermission.toordinal() == gregorian.toordinal()


def test_intermission_to_gregorian_still_gives_calendar_date() -> None:
    """Intermission maps to a Gregorian date; that date has a weekday, but Intermission does not."""
    from dateutil_gorman.types import Intermission
    
    intermission = Intermission(year=2024, day=1)
    assert intermission.to_gregorian() == date(2024, 12, 30)
    intermission2 = Intermission(year=2024, day=2)
    assert intermission2.to_gregorian() == date(2024, 12, 31)
    intermission_2023 = Intermission(year=2023, day=1)
    assert intermission_2023.to_gregorian() == date(2023, 12, 31)


def test_intermission_week_of_month_raises() -> None:
    """Intermission.week_of_month() should raise ValueError."""
    from dateutil_gorman.types import Intermission
    import pytest
    
    intermission = Intermission(year=2024, day=1)
    with pytest.raises(ValueError, match="not part of any"):
        intermission.week_of_month()


def test_intermission_week_of_year_raises() -> None:
    """Intermission.week_of_year() should raise ValueError."""
    from dateutil_gorman.types import Intermission
    import pytest
    
    intermission = Intermission(year=2024, day=1)
    with pytest.raises(ValueError, match="not part of any"):
        intermission.week_of_year()
