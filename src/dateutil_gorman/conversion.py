"""Conversion helpers between Gregorian and Gorman calendars."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

from dateutil_gorman.types import GormanDate, Intermission

LOGGER = logging.getLogger(__name__)
GormanValue = GormanDate | Intermission


def _is_leap_year(year: int) -> bool:
    """Return whether ``year`` is a Gregorian leap year.

    Args:
        year: Gregorian year value.

    Returns:
        ``True`` when the year is leap, otherwise ``False``.
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _day_of_year(d: date) -> int:
    """Return the Gregorian day-of-year for ``d``.

    Args:
        d: Gregorian date value.

    Returns:
        Integer in the inclusive range ``1`` to ``366``.
    """
    return d.timetuple().tm_yday


def _gorman_month_day_from_day_of_year(day_of_year: int) -> tuple[int, int]:
    """Convert a Gregorian day-of-year into a Gorman month/day pair.

    Args:
        day_of_year: Gregorian day of year in the inclusive range ``1`` to
            ``364``.

    Returns:
        Tuple ``(month, day)`` where ``month`` is ``1`` to ``13`` and ``day``
        is ``1`` to ``28``.

    Raises:
        ValueError: If ``day_of_year`` falls outside the month portion of the
            Gorman year.
    """
    if not 1 <= day_of_year <= 364:
        raise ValueError(f"day_of_year must be between 1 and 364, got {day_of_year}")

    month = ((day_of_year - 1) // 28) + 1
    day = ((day_of_year - 1) % 28) + 1
    return month, day


def gregorian_to_gorman(d: date | datetime) -> GormanValue:
    """Convert a Gregorian value into the Gorman calendar.

    Intermission is modeled as one or two distinct 24-hour days, never as a
    single 48-hour period.

    Args:
        d: Gregorian ``date`` or ``datetime`` value.

    Returns:
        A ``GormanDate`` when the value falls inside the 13 regular months, or
        an ``Intermission`` for the year-ending intermission day(s). When a
        ``datetime`` is provided, the time component is preserved.
    """
    if isinstance(d, datetime):
        date_obj = d.date()
        time_obj = d.time()
    else:
        date_obj = d
        time_obj = None

    day_of_year = _day_of_year(date_obj)
    year = date_obj.year
    LOGGER.debug(
        "Converting Gregorian value to Gorman", extra={"date": date_obj.isoformat()}
    )

    if day_of_year <= 364:
        month, day = _gorman_month_day_from_day_of_year(day_of_year)
        return GormanDate(year=year, month=month, day=day, time=time_obj)

    if day_of_year == 365:
        return Intermission(year=year, day=1, time=time_obj)

    if _is_leap_year(year):
        return Intermission(year=year, day=2, time=time_obj)

    raise ValueError(
        f"Gregorian year {year} does not contain a day-of-year value of {day_of_year}"
    )


def gorman_to_gregorian(year: int, month: int, day: int) -> date:
    """Convert a regular Gorman date into the Gregorian calendar.

    Args:
        year: Gorman year.
        month: Gorman month in the inclusive range ``1`` to ``13``.
        day: Gorman day in the inclusive range ``1`` to ``28``.

    Returns:
        Gregorian ``date`` value for the supplied Gorman date.

    Raises:
        ValueError: If ``month`` or ``day`` is outside the valid range.
    """
    if not 1 <= month <= 13:
        raise ValueError(f"Month must be between 1 and 13, got {month}")
    if not 1 <= day <= 28:
        raise ValueError(f"Day must be between 1 and 28, got {day}")

    LOGGER.debug(
        "Converting Gorman month/day to Gregorian",
        extra={"year": year, "month": month, "day": day},
    )
    day_of_year = (month - 1) * 28 + day

    return date(year, 1, 1) + timedelta(days=day_of_year - 1)


def intermission_to_gregorian(year: int, day: int) -> date:
    """Convert an intermission day into the Gregorian calendar.

    Each intermission day is a separate 24-hour period. ``Intermission 2`` is
    only valid in Gregorian leap years.

    Args:
        year: Gorman year.
        day: Intermission day number, either ``1`` or ``2``.

    Returns:
        Gregorian ``date`` for the requested intermission day.

    Raises:
        ValueError: If ``day`` is invalid for the supplied year.
    """
    is_leap = _is_leap_year(year)

    LOGGER.debug(
        "Converting Gorman intermission to Gregorian", extra={"year": year, "day": day}
    )

    if day == 1:
        return date(year, 12, 30) if is_leap else date(year, 12, 31)

    if day == 2:
        if is_leap:
            return date(year, 12, 31)
        raise ValueError(
            f"Intermission day 2 is only valid in leap years, {year} is not a leap year"
        )

    raise ValueError(f"Intermission day must be 1 or 2, got {day}")
