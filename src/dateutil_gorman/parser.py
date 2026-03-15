"""Parsing utilities for Gorman calendar strings."""

from __future__ import annotations

import logging
import re
from datetime import datetime, time

from dateutil_gorman.constants import GORMAN_MONTHS
from dateutil_gorman.conversion import gorman_to_gregorian, intermission_to_gregorian

LOGGER = logging.getLogger(__name__)
_MONTH_PATTERN = "|".join(re.escape(month) for month in GORMAN_MONTHS)
_TIME_PATTERN = (
    r"(?:\s+(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(?::(?P<second>\d{1,2}))?)?"
)
_INTERMISSION_PATTERN = re.compile(
    rf"^Intermission\s+(?P<day>\d+)\s+(?P<year>\d{{4}}){_TIME_PATTERN}$",
    re.IGNORECASE,
)
_DAY_MONTH_YEAR_PATTERN = re.compile(
    rf"^(?P<day>\d{{1,2}})\s+(?P<month>{_MONTH_PATTERN})\s+(?P<year>\d{{4}}){_TIME_PATTERN}$",
    re.IGNORECASE,
)
_MONTH_DAY_YEAR_PATTERN = re.compile(
    rf"^(?P<month>{_MONTH_PATTERN})\s+(?P<day>\d{{1,2}}),?\s+(?P<year>\d{{4}}){_TIME_PATTERN}$",
    re.IGNORECASE,
)
_MONTH_LOOKUP = {
    month.lower(): index for index, month in enumerate(GORMAN_MONTHS, start=1)
}
_VALID_MONTHS = ", ".join(GORMAN_MONTHS)


def _parse_time_parts(match: re.Match[str]) -> time:
    """Create a ``time`` object from optional regex capture groups."""
    hour = int(match.group("hour") or 0)
    minute = int(match.group("minute") or 0)
    second = int(match.group("second") or 0)
    return time(hour, minute, second)


def parse_gorman(date_string: str) -> datetime:
    """Parse a Gorman calendar string into the matching Gregorian datetime.

    Supported formats include ``"1 March 2024"``, ``"March 1, 2024"``,
    ``"Intermission 1 2024"``, and the same forms with an optional
    ``HH:MM[:SS]`` suffix.

    Args:
        date_string: Gorman date string to parse.

    Returns:
        Gregorian ``datetime`` corresponding to the supplied Gorman value.

    Raises:
        ValueError: If the string is empty, malformed, or contains invalid date
            components.
    """
    normalized = date_string.strip()
    if not normalized:
        raise ValueError("Could not parse an empty Gorman date string")

    LOGGER.debug("Parsing Gorman date string", extra={"date_string": normalized})

    intermission_match = _INTERMISSION_PATTERN.fullmatch(normalized)
    if intermission_match is not None:
        day = int(intermission_match.group("day"))
        year = int(intermission_match.group("year"))
        gregorian_date = intermission_to_gregorian(year, day)
        return datetime.combine(gregorian_date, _parse_time_parts(intermission_match))

    date_match = _DAY_MONTH_YEAR_PATTERN.fullmatch(normalized)
    if date_match is None:
        date_match = _MONTH_DAY_YEAR_PATTERN.fullmatch(normalized)
    if date_match is None:
        raise ValueError(f"Could not parse Gorman date string: {date_string}")

    day = int(date_match.group("day"))
    month_name = date_match.group("month")
    year = int(date_match.group("year"))
    month_index = _MONTH_LOOKUP.get(month_name.lower())
    if month_index is None:
        raise ValueError(
            f"Unknown month name: {month_name}. Valid months are: {_VALID_MONTHS}"
        )

    if not 1 <= day <= 28:
        raise ValueError(f"Day must be between 1 and 28 for Gorman months, got {day}")

    gregorian_date = gorman_to_gregorian(year, month_index, day)
    return datetime.combine(gregorian_date, _parse_time_parts(date_match))
