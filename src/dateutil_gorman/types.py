"""Types for representing Gorman calendar dates."""

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional, Union, cast

# Type alias so replace(time=...) does not shadow datetime.time
_Time = time


@dataclass(frozen=True)
class GormanDate:
    """Represents a date in the Gorman calendar (within a month)."""

    year: int
    month: int  # 1-13
    day: int  # 1-28
    time: Optional[time] = None  # Optional time component if converted from datetime

    def replace(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        time: Optional[_Time] = None,
    ) -> "GormanDate":
        """Return a new GormanDate with the given fields replaced (immutable update)."""
        return GormanDate(
            year=year if year is not None else self.year,
            month=month if month is not None else self.month,
            day=day if day is not None else self.day,
            time=time if time is not None else self.time,
        )

    @classmethod
    def fromisoformat(cls, s: str) -> "GormanDate":
        """Parse an ISO 8601 (Gregorian) date string and return the corresponding GormanDate.

        Accepts only conformant ISO 8601 calendar dates (YYYY-MM-DD, Gregorian).
        Raises ValueError if the string is invalid or if that date is an intermission day.
        """
        from dateutil_gorman.conversion import gregorian_to_gorman
        gregorian = date.fromisoformat(s.strip())
        result = gregorian_to_gorman(gregorian)
        if not isinstance(result, GormanDate):
            raise ValueError(f"Date {s!r} is an intermission day in the Gorman calendar")
        return result

    def gorman_week_calendar(self) -> tuple[int, int, int]:
        """Return Gorman calendar tuple (year, week of year, weekday).

        Week is 1-52 (Gorman year has 13 months × 4 weeks), weekday is 1 (Monday)
        to 7 (Sunday). For ISO 8601 week date use to_gregorian().isocalendar().
        """
        return (self.year, self.week_of_year(), self.isoweekday())

    @classmethod
    def from_gorman_week_calendar(cls, year: int, week: int, weekday: int) -> "GormanDate":
        """Return GormanDate from Gorman calendar (year, week 1-52, weekday 1-7)."""
        if week < 1 or week > 52:
            raise ValueError(f"Week must be 1-52, got {week}")
        if weekday < 1 or weekday > 7:
            raise ValueError(f"Weekday must be 1-7, got {weekday}")
        day_of_year = (week - 1) * 7 + weekday
        if day_of_year < 1 or day_of_year > 364:
            raise ValueError(f"Invalid (week, weekday) for Gorman year: ({week}, {weekday})")
        month = ((day_of_year - 1) // 28) + 1
        day = ((day_of_year - 1) % 28) + 1
        return cls(year=year, month=month, day=day)

    def __lt__(self, other: object) -> bool:
        if type(other) not in (GormanDate, Intermission):
            return NotImplemented
        return self.toordinal() < cast(Union[GormanDate, Intermission], other).toordinal()

    def __le__(self, other: object) -> bool:
        if type(other) not in (GormanDate, Intermission):
            return NotImplemented
        return self.toordinal() <= cast(Union[GormanDate, Intermission], other).toordinal()

    def __gt__(self, other: object) -> bool:
        if type(other) not in (GormanDate, Intermission):
            return NotImplemented
        return self.toordinal() > cast(Union[GormanDate, Intermission], other).toordinal()

    def __ge__(self, other: object) -> bool:
        if type(other) not in (GormanDate, Intermission):
            return NotImplemented
        return self.toordinal() >= cast(Union[GormanDate, Intermission], other).toordinal()

    def __str__(self) -> str:
        """Return human-readable string representation, e.g. '15 March 2024'."""
        from dateutil_gorman.constants import GORMAN_MONTHS
        month_name = GORMAN_MONTHS[self.month - 1]
        return f"{self.day} {month_name} {self.year}"

    def to_gregorian(self) -> date:
        """Convert this Gorman date to a Gregorian date."""
        from dateutil_gorman.conversion import gorman_to_gregorian
        return gorman_to_gregorian(self.year, self.month, self.day)
    
    def to_gregorian_datetime(self) -> datetime:
        """Convert this Gorman date to a Gregorian datetime.
        
        If time was preserved from the original datetime, it will be included.
        Otherwise, returns midnight (00:00:00).
        """
        gregorian_date = self.to_gregorian()
        time_component = self.time if self.time is not None else time.min
        return datetime.combine(gregorian_date, time_component)
    
    def weekday(self) -> int:
        """Return the day of the week, Monday=0, Sunday=6 (same as datetime.date)."""
        day_of_year = (self.month - 1) * 28 + self.day
        ordinal = date(self.year, 1, 1).toordinal() + day_of_year - 1
        return (ordinal + 6) % 7

    def isoweekday(self) -> int:
        """Return the day of the week, Monday=1, Sunday=7 (same as datetime.date)."""
        return self.weekday() + 1

    def week_of_month(self) -> int:
        """Return the week number within the Gorman month (1-4).
        
        Each Gorman month has exactly 28 days (4 weeks), so this returns
        which week of the month this day falls in.
        
        Returns:
            Integer from 1 to 4
        """
        return ((self.day - 1) // 7) + 1
    
    def week_of_year(self) -> int:
        """Return the week number within the Gorman year (1-52).
        
        The Gorman year has 13 months × 4 weeks = 52 weeks in the months.
        Intermission days are not part of any week.
        
        Returns:
            Integer from 1 to 52
        """
        day_of_year = (self.month - 1) * 28 + self.day
        return ((day_of_year - 1) // 7) + 1
    
    def toordinal(self) -> int:
        """Return the proleptic Gregorian ordinal of the date.
        
        The ordinal is the number of days since January 1 of year 1.
        This uses the same ordinal system as Python's date.toordinal().
        
        Returns:
            Integer representing the ordinal
        """
        return self.to_gregorian().toordinal()
    
    @classmethod
    def fromordinal(cls, ordinal: int) -> "GormanDate":
        """Return the Gorman date corresponding to the proleptic Gregorian ordinal.
        
        The ordinal is the number of days since January 1 of year 1.
        This uses the same ordinal system as Python's date.fromordinal().
        
        Args:
            ordinal: Proleptic Gregorian ordinal
        
        Returns:
            GormanDate corresponding to the ordinal
        """
        from dateutil_gorman.conversion import gregorian_to_gorman
        gregorian = date.fromordinal(ordinal)
        result = gregorian_to_gorman(gregorian)
        if not isinstance(result, GormanDate):
            raise ValueError(f"Ordinal {ordinal} corresponds to an intermission day, not a Gorman date")
        return result


@dataclass(frozen=True)
class Intermission:
    """Represents one intermission day (not in any month or week).

    Each instance is exactly one 24-hour day. In leap years there are two
    separate intermission days: Intermission 1 and Intermission 2 (never
    modeled as a single 48-hour day).
    """

    year: int
    day: int  # 1 or 2 (2 only in leap years); each is a separate 24h day
    time: Optional[time] = None  # Optional time component if converted from datetime

    def replace(
        self,
        *,
        year: Optional[int] = None,
        day: Optional[int] = None,
        time: Optional[_Time] = None,
    ) -> "Intermission":
        """Return a new Intermission with the given fields replaced (immutable update)."""
        return Intermission(
            year=year if year is not None else self.year,
            day=day if day is not None else self.day,
            time=time if time is not None else self.time,
        )

    @classmethod
    def fromordinal(cls, ordinal: int) -> "Intermission":
        """Return the Intermission corresponding to the proleptic Gregorian ordinal.

        Raises ValueError if the ordinal corresponds to a Gorman date (not intermission).
        """
        from dateutil_gorman.conversion import gregorian_to_gorman
        gregorian = date.fromordinal(ordinal)
        result = gregorian_to_gorman(gregorian)
        if not isinstance(result, Intermission):
            raise ValueError(f"Ordinal {ordinal} corresponds to a Gorman date, not an intermission day")
        return result

    def __str__(self) -> str:
        """Return human-readable string representation, e.g. 'Intermission 1 2024'."""
        return f"Intermission {self.day} {self.year}"

    def __lt__(self, other: object) -> bool:
        if type(other) not in (GormanDate, Intermission):
            return NotImplemented
        return self.toordinal() < cast(Union[GormanDate, Intermission], other).toordinal()

    def __le__(self, other: object) -> bool:
        if type(other) not in (GormanDate, Intermission):
            return NotImplemented
        return self.toordinal() <= cast(Union[GormanDate, Intermission], other).toordinal()

    def __gt__(self, other: object) -> bool:
        if type(other) not in (GormanDate, Intermission):
            return NotImplemented
        return self.toordinal() > cast(Union[GormanDate, Intermission], other).toordinal()

    def __ge__(self, other: object) -> bool:
        if type(other) not in (GormanDate, Intermission):
            return NotImplemented
        return self.toordinal() >= cast(Union[GormanDate, Intermission], other).toordinal()

    def to_gregorian(self) -> date:
        """Convert this intermission day to a Gregorian date."""
        from dateutil_gorman.conversion import intermission_to_gregorian
        return intermission_to_gregorian(self.year, self.day)
    
    def to_gregorian_datetime(self) -> datetime:
        """Convert this intermission day to a Gregorian datetime.
        
        If time was preserved from the original datetime, it will be included.
        Otherwise, returns midnight (00:00:00).
        """
        gregorian_date = self.to_gregorian()
        time_component = self.time if self.time is not None else time.min
        return datetime.combine(gregorian_date, time_component)
    
    def weekday(self) -> int:
        """Raise ValueError; Intermission has no weekday—it is not part of the Monday–Sunday week."""
        raise ValueError("Intermission has no weekday; it is not part of the Monday–Sunday week")

    def isoweekday(self) -> int:
        """Raise ValueError; Intermission has no weekday—it is not part of the Monday–Sunday week."""
        raise ValueError("Intermission has no weekday; it is not part of the Monday–Sunday week")

    def isocalendar(self) -> tuple[int, int, int]:
        """Raise ValueError; Intermission has no week or weekday—it is not part of any week."""
        raise ValueError("Intermission has no week or weekday; it is not part of any week")
    
    def week_of_month(self) -> int:
        """Raise ValueError; intermission days are not part of any month or week."""
        raise ValueError("Intermission days are not part of any Gorman month or week")
    
    def week_of_year(self) -> int:
        """Raise ValueError; intermission days are not part of any month or week."""
        raise ValueError("Intermission days are not part of any Gorman month or week")
    
    def toordinal(self) -> int:
        """Return the proleptic Gregorian ordinal of the date.
        
        The ordinal is the number of days since January 1 of year 1.
        This uses the same ordinal system as Python's date.toordinal().
        
        Returns:
            Integer representing the ordinal
        """
        return self.to_gregorian().toordinal()
