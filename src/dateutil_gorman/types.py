"""Immutable value objects representing Gorman calendar dates."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import cast

from dateutil_gorman.constants import GORMAN_MONTHS

LOGGER = logging.getLogger(__name__)
_Time = time
_MISSING = object()


def _comparison_ordinal(other: object) -> int | None:
    """Return an ordinal for supported comparison operands."""
    if isinstance(other, (GormanDate, Intermission)):
        return other.toordinal()
    return None


@dataclass(frozen=True, slots=True)
class GormanDate:
    """Represent a date in one of the 13 standard Gorman months.

    Attributes:
        year: Gorman year value.
        month: Gorman month number in the inclusive range ``1`` to ``13``.
        day: Gorman day number in the inclusive range ``1`` to ``28``.
        time: Optional preserved time component when the value originated from a
            Gregorian ``datetime``.
    """

    year: int
    month: int
    day: int
    time: _Time | None = None

    def __post_init__(self) -> None:
        """Validate field values after dataclass initialization."""
        if self.year < 1:
            raise ValueError(
                f"Year must be greater than or equal to 1, got {self.year}"
            )
        if not 1 <= self.month <= len(GORMAN_MONTHS):
            raise ValueError(f"Month must be between 1 and 13, got {self.month}")
        if not 1 <= self.day <= 28:
            raise ValueError(f"Day must be between 1 and 28, got {self.day}")

    def replace(
        self,
        *,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
        time: _Time | None | object = _MISSING,
    ) -> GormanDate:
        """Return a copy with selected fields replaced.

        Args:
            year: Replacement year value.
            month: Replacement month value.
            day: Replacement day value.
            time: Replacement time value. Pass ``None`` to clear a preserved
                time component.

        Returns:
            A new ``GormanDate`` instance.
        """
        new_time = self.time if time is _MISSING else cast(_Time | None, time)
        return GormanDate(
            year=self.year if year is None else year,
            month=self.month if month is None else month,
            day=self.day if day is None else day,
            time=new_time,
        )

    @classmethod
    def fromisoformat(cls, s: str) -> GormanDate:
        """Build a ``GormanDate`` from a Gregorian ISO calendar date.

        Args:
            s: Gregorian ISO 8601 date string in ``YYYY-MM-DD`` form.

        Returns:
            ``GormanDate`` matching the Gregorian input.

        Raises:
            ValueError: If the string is invalid or maps to an intermission day.
        """
        from dateutil_gorman.conversion import gregorian_to_gorman

        gregorian = date.fromisoformat(s.strip())
        result = gregorian_to_gorman(gregorian)
        if not isinstance(result, cls):
            raise ValueError(
                f"Date {s!r} is an intermission day in the Gorman calendar"
            )
        return result

    @classmethod
    def from_gorman_week_calendar(
        cls, year: int, week: int, weekday: int
    ) -> GormanDate:
        """Build a date from the Gorman week calendar.

        Args:
            year: Gorman year.
            week: Gorman week of year in the inclusive range ``1`` to ``52``.
            weekday: Weekday in the inclusive range ``1`` to ``7`` where
                Monday is ``1``.

        Returns:
            ``GormanDate`` matching the provided week tuple.

        Raises:
            ValueError: If ``week`` or ``weekday`` is out of range.
        """
        if not 1 <= week <= 52:
            raise ValueError(f"Week must be between 1 and 52, got {week}")
        if not 1 <= weekday <= 7:
            raise ValueError(f"Weekday must be between 1 and 7, got {weekday}")

        day_of_year = ((week - 1) * 7) + weekday
        month = ((day_of_year - 1) // 28) + 1
        day = ((day_of_year - 1) % 28) + 1
        return cls(year=year, month=month, day=day)

    @classmethod
    def fromordinal(cls, ordinal: int) -> GormanDate:
        """Build a ``GormanDate`` from a proleptic Gregorian ordinal.

        Args:
            ordinal: Ordinal compatible with ``datetime.date.fromordinal``.

        Returns:
            ``GormanDate`` corresponding to the ordinal.

        Raises:
            ValueError: If the ordinal maps to an intermission day.
        """
        from dateutil_gorman.conversion import gregorian_to_gorman

        gregorian = date.fromordinal(ordinal)
        result = gregorian_to_gorman(gregorian)
        if not isinstance(result, cls):
            raise ValueError(
                "Ordinal "
                f"{ordinal} corresponds to an intermission day, not a Gorman "
                "date"
            )
        return result

    def gorman_week_calendar(self) -> tuple[int, int, int]:
        """Return the Gorman week-calendar tuple.

        Returns:
            Tuple of ``(year, week_of_year, weekday)`` where weekday follows
            ISO numbering with Monday as ``1`` and Sunday as ``7``.
        """
        return self.year, self.week_of_year(), self.isoweekday()

    def to_gregorian(self) -> date:
        """Convert this Gorman date to a Gregorian ``date``."""
        from dateutil_gorman.conversion import gorman_to_gregorian

        return gorman_to_gregorian(self.year, self.month, self.day)

    def to_gregorian_datetime(self) -> datetime:
        """Convert this value to a Gregorian ``datetime``.

        Returns:
            Gregorian ``datetime`` preserving the stored time when present, or
            midnight otherwise.
        """
        time_component = time.min if self.time is None else self.time
        return datetime.combine(self.to_gregorian(), time_component)

    def weekday(self) -> int:
        """Return the weekday using ``datetime.date.weekday`` semantics."""
        return self.to_gregorian().weekday()

    def isoweekday(self) -> int:
        """Return the ISO weekday using ``datetime.date.isoweekday`` semantics."""
        return self.to_gregorian().isoweekday()

    def week_of_month(self) -> int:
        """Return the week number within the Gorman month."""
        return ((self.day - 1) // 7) + 1

    def week_of_year(self) -> int:
        """Return the week number within the Gorman year."""
        day_of_year = ((self.month - 1) * 28) + self.day
        return ((day_of_year - 1) // 7) + 1

    def toordinal(self) -> int:
        """Return the matching proleptic Gregorian ordinal."""
        return self.to_gregorian().toordinal()

    def __lt__(self, other: object) -> bool:
        """Compare values using Gregorian ordinals."""
        other_ordinal = _comparison_ordinal(other)
        if other_ordinal is None:
            return NotImplemented
        return self.toordinal() < other_ordinal

    def __le__(self, other: object) -> bool:
        """Compare values using Gregorian ordinals."""
        other_ordinal = _comparison_ordinal(other)
        if other_ordinal is None:
            return NotImplemented
        return self.toordinal() <= other_ordinal

    def __gt__(self, other: object) -> bool:
        """Compare values using Gregorian ordinals."""
        other_ordinal = _comparison_ordinal(other)
        if other_ordinal is None:
            return NotImplemented
        return self.toordinal() > other_ordinal

    def __ge__(self, other: object) -> bool:
        """Compare values using Gregorian ordinals."""
        other_ordinal = _comparison_ordinal(other)
        if other_ordinal is None:
            return NotImplemented
        return self.toordinal() >= other_ordinal

    def __str__(self) -> str:
        """Return a human-readable representation."""
        month_name = GORMAN_MONTHS[self.month - 1]
        return f"{self.day} {month_name} {self.year}"


@dataclass(frozen=True, slots=True)
class Intermission:
    """Represent one intermission day outside the normal Gorman months.

    Attributes:
        year: Gorman year value.
        day: Intermission day number. ``2`` is only valid in leap years.
        time: Optional preserved time component when the value originated from a
            Gregorian ``datetime``.
    """

    year: int
    day: int
    time: _Time | None = None

    def __post_init__(self) -> None:
        """Validate intermission field values."""
        from dateutil_gorman.conversion import _is_leap_year

        if self.year < 1:
            raise ValueError(
                f"Year must be greater than or equal to 1, got {self.year}"
            )
        if self.day not in (1, 2):
            raise ValueError(f"Intermission day must be 1 or 2, got {self.day}")
        if self.day == 2 and not _is_leap_year(self.year):
            raise ValueError(
                "Intermission day 2 is only valid in leap years, "
                f"{self.year} is not a leap year"
            )

    def replace(
        self,
        *,
        year: int | None = None,
        day: int | None = None,
        time: _Time | None | object = _MISSING,
    ) -> Intermission:
        """Return a copy with selected fields replaced.

        Args:
            year: Replacement year value.
            day: Replacement intermission day.
            time: Replacement time value. Pass ``None`` to clear a preserved
                time component.

        Returns:
            A new ``Intermission`` instance.
        """
        new_time = self.time if time is _MISSING else cast(_Time | None, time)
        return Intermission(
            year=self.year if year is None else year,
            day=self.day if day is None else day,
            time=new_time,
        )

    @classmethod
    def fromordinal(cls, ordinal: int) -> Intermission:
        """Build an ``Intermission`` from a proleptic Gregorian ordinal.

        Args:
            ordinal: Ordinal compatible with ``datetime.date.fromordinal``.

        Returns:
            ``Intermission`` corresponding to the ordinal.

        Raises:
            ValueError: If the ordinal maps to a standard Gorman month/day.
        """
        from dateutil_gorman.conversion import gregorian_to_gorman

        gregorian = date.fromordinal(ordinal)
        result = gregorian_to_gorman(gregorian)
        if not isinstance(result, cls):
            raise ValueError(
                "Ordinal "
                f"{ordinal} corresponds to a Gorman date, not an intermission "
                "day"
            )
        return result

    def to_gregorian(self) -> date:
        """Convert this intermission day to a Gregorian ``date``."""
        from dateutil_gorman.conversion import intermission_to_gregorian

        return intermission_to_gregorian(self.year, self.day)

    def to_gregorian_datetime(self) -> datetime:
        """Convert this value to a Gregorian ``datetime``.

        Returns:
            Gregorian ``datetime`` preserving the stored time when present, or
            midnight otherwise.
        """
        time_component = time.min if self.time is None else self.time
        return datetime.combine(self.to_gregorian(), time_component)

    def weekday(self) -> int:
        """Raise because intermission days are outside the weekly cycle."""
        raise ValueError(
            "Intermission has no weekday; it is not part of the Monday-Sunday week"
        )

    def isoweekday(self) -> int:
        """Raise because intermission days are outside the weekly cycle."""
        raise ValueError(
            "Intermission has no weekday; it is not part of the Monday-Sunday week"
        )

    def isocalendar(self) -> tuple[int, int, int]:
        """Raise because intermission days are outside the weekly cycle."""
        raise ValueError(
            "Intermission has no week or weekday; it is not part of any week"
        )

    def week_of_month(self) -> int:
        """Raise because intermission days do not belong to a month."""
        raise ValueError("Intermission days are not part of any Gorman month or week")

    def week_of_year(self) -> int:
        """Raise because intermission days do not belong to the weekly calendar."""
        raise ValueError("Intermission days are not part of any Gorman month or week")

    def toordinal(self) -> int:
        """Return the matching proleptic Gregorian ordinal."""
        return self.to_gregorian().toordinal()

    def __lt__(self, other: object) -> bool:
        """Compare values using Gregorian ordinals."""
        other_ordinal = _comparison_ordinal(other)
        if other_ordinal is None:
            return NotImplemented
        return self.toordinal() < other_ordinal

    def __le__(self, other: object) -> bool:
        """Compare values using Gregorian ordinals."""
        other_ordinal = _comparison_ordinal(other)
        if other_ordinal is None:
            return NotImplemented
        return self.toordinal() <= other_ordinal

    def __gt__(self, other: object) -> bool:
        """Compare values using Gregorian ordinals."""
        other_ordinal = _comparison_ordinal(other)
        if other_ordinal is None:
            return NotImplemented
        return self.toordinal() > other_ordinal

    def __ge__(self, other: object) -> bool:
        """Compare values using Gregorian ordinals."""
        other_ordinal = _comparison_ordinal(other)
        if other_ordinal is None:
            return NotImplemented
        return self.toordinal() >= other_ordinal

    def __str__(self) -> str:
        """Return a human-readable representation."""
        return f"Intermission {self.day} {self.year}"
