"""Tests for Gorman week calculation methods."""

from datetime import date
from dateutil_gorman.types import GormanDate
from dateutil_gorman.conversion import gregorian_to_gorman


def test_week_of_month() -> None:
    """week_of_month() should return week number within month (1-4)."""
    gorman = GormanDate(year=2024, month=1, day=1)
    assert gorman.week_of_month() == 1
    
    gorman = GormanDate(year=2024, month=1, day=7)
    assert gorman.week_of_month() == 1
    
    gorman = GormanDate(year=2024, month=1, day=8)
    assert gorman.week_of_month() == 2
    
    gorman = GormanDate(year=2024, month=1, day=14)
    assert gorman.week_of_month() == 2
    
    gorman = GormanDate(year=2024, month=1, day=15)
    assert gorman.week_of_month() == 3
    
    gorman = GormanDate(year=2024, month=1, day=21)
    assert gorman.week_of_month() == 3
    
    gorman = GormanDate(year=2024, month=1, day=22)
    assert gorman.week_of_month() == 4
    
    gorman = GormanDate(year=2024, month=1, day=28)
    assert gorman.week_of_month() == 4


def test_week_of_year() -> None:
    """week_of_year() should return week number within year (1-52)."""
    gorman = GormanDate(year=2024, month=1, day=1)
    assert gorman.week_of_year() == 1
    
    gorman = GormanDate(year=2024, month=1, day=28)
    assert gorman.week_of_year() == 4
    
    gorman = GormanDate(year=2024, month=2, day=1)
    assert gorman.week_of_year() == 5
    
    gorman = GormanDate(year=2024, month=13, day=28)
    assert gorman.week_of_year() == 52


def test_gorman_week_calendar() -> None:
    """gorman_week_calendar() should return (year, gorman_week 1-52, weekday)."""
    gorman = GormanDate(year=2024, month=1, day=1)
    result = gorman.gorman_week_calendar()
    assert result[0] == 2024
    assert result[1] == 1
    assert result[2] == gorman.isoweekday()

    gorman = GormanDate(year=2024, month=13, day=28)
    result = gorman.gorman_week_calendar()
    assert result[0] == 2024
    assert result[1] == 52
    assert result[2] == gorman.isoweekday()


def test_week_consistency() -> None:
    """Week calculations should be consistent across the year."""
    for month in range(1, 14):
        for day in [1, 7, 8, 14, 15, 21, 22, 28]:
            gorman = GormanDate(year=2024, month=month, day=day)
            week_of_month = gorman.week_of_month()
            week_of_year = gorman.week_of_year()
            
            assert 1 <= week_of_month <= 4
            assert 1 <= week_of_year <= 52
            
            expected_week_of_year = ((month - 1) * 4) + week_of_month
            assert week_of_year == expected_week_of_year


def test_gorman_week_calendar_values() -> None:
    """gorman_week_calendar() returns (year, Gorman week 1-52, weekday). For ISO week use to_gregorian().isocalendar()."""
    gorman = GormanDate(year=2024, month=7, day=15)
    gorman_week = gorman.gorman_week_calendar()
    assert gorman_week[0] == 2024
    assert gorman_week[1] == gorman.week_of_year()
    assert gorman_week[1] == 27
    assert gorman_week[2] == gorman.isoweekday()


def test_gorman_weekday_same_as_gregorian() -> None:
    """weekday() and isoweekday() should match Gregorian since week cycle is the same."""
    test_dates = [
        date(2024, 1, 1),
        date(2024, 1, 7),
        date(2024, 6, 15),
        date(2024, 12, 28),
    ]
    
    for gregorian in test_dates:
        gorman = gregorian_to_gorman(gregorian)
        if hasattr(gorman, 'month'):  # Not an Intermission
            assert gorman.weekday() == gregorian.weekday()
            assert gorman.isoweekday() == gregorian.isoweekday()
