"""Conversion functions between Gregorian and Gorman calendars."""

from datetime import date, datetime
from typing import Union
from dateutil_gorman.types import GormanDate, Intermission


def _is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _day_of_year(d: date) -> int:
    """Calculate the day of year (1-366) for a given date."""
    return d.timetuple().tm_yday


def _gorman_month_day_from_day_of_year(day_of_year: int) -> tuple[int, int]:
    """Convert day of year (1-364) to Gorman (month, day).
    
    Args:
        day_of_year: Day of year (1-364, must be within the 13 months)
    
    Returns:
        Tuple of (month, day) where month is 1-13 and day is 1-28
    """
    month = ((day_of_year - 1) // 28) + 1
    day = ((day_of_year - 1) % 28) + 1
    return (month, day)


def gregorian_to_gorman(d: Union[date, datetime]) -> Union[GormanDate, Intermission]:
    """Convert a Gregorian date to Gorman calendar.

    Intermission is always one or two separate 24-hour days (Intermission 1
    and, in leap years, Intermission 2), never a single 48-hour day.

    Args:
        d: Gregorian date or datetime

    Returns:
        GormanDate if within the 13 months, Intermission if an intermission day.
        If a datetime is provided, the time component is preserved.
    """
    if isinstance(d, datetime):
        date_obj = d.date()
        time_obj = d.time()
    else:
        date_obj = d
        time_obj = None
    
    day_of_year = _day_of_year(date_obj)
    year = date_obj.year
    is_leap = _is_leap_year(year)
    
    if day_of_year <= 364:
        month, day = _gorman_month_day_from_day_of_year(day_of_year)
        return GormanDate(year=year, month=month, day=day, time=time_obj)
    elif day_of_year == 365:
        if is_leap:
            return Intermission(year=year, day=1, time=time_obj)
        else:
            return Intermission(year=year, day=1, time=time_obj)
    else:  # day_of_year == 366 (leap year only)
        return Intermission(year=year, day=2, time=time_obj)


def gorman_to_gregorian(year: int, month: int, day: int) -> date:
    """Convert a Gorman calendar date to Gregorian.
    
    Args:
        year: Gorman year
        month: Gorman month (1-13)
        day: Gorman day (1-28)
    
    Returns:
        Gregorian date
    
    Raises:
        ValueError: If month or day is out of valid range
    """
    if month < 1 or month > 13:
        raise ValueError(f"Month must be between 1 and 13, got {month}")
    if day < 1 or day > 28:
        raise ValueError(f"Day must be between 1 and 28, got {day}")
    
    day_of_year = (month - 1) * 28 + day
    
    return date(year, 1, 1) + date.resolution * (day_of_year - 1)


def intermission_to_gregorian(year: int, day: int) -> date:
    """Convert one intermission day to Gregorian date.

    Each intermission day is a separate 24-hour day. Intermission 1 and
    Intermission 2 (leap years only) map to distinct Gregorian dates.

    Args:
        year: Gorman year
        day: Intermission day (1 or 2; 2 only valid in leap years)

    Returns:
        Gregorian date for that single 24h intermission day

    Raises:
        ValueError: If day is invalid for the given year
    """
    is_leap = _is_leap_year(year)
    
    if day == 1:
        if is_leap:
            return date(year, 12, 30)
        else:
            return date(year, 12, 31)
    elif day == 2:
        if is_leap:
            return date(year, 12, 31)
        else:
            raise ValueError(f"Intermission day 2 is only valid in leap years, {year} is not a leap year")
    else:
        raise ValueError(f"Intermission day must be 1 or 2, got {day}")
