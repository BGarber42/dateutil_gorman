"""Tests for Gorman calendar types."""

from datetime import date, datetime, time
import pytest
from dateutil_gorman.types import GormanDate, Intermission


def test_gorman_date_to_gregorian() -> None:
    """GormanDate.to_gregorian() should convert to Gregorian date."""
    gorman = GormanDate(year=2024, month=1, day=1)
    result = gorman.to_gregorian()
    
    assert result == date(2024, 1, 1)


def test_gorman_date_to_gregorian_datetime() -> None:
    """GormanDate.to_gregorian_datetime() should convert to Gregorian datetime."""
    gorman = GormanDate(year=2024, month=1, day=1)
    result = gorman.to_gregorian_datetime()
    
    assert result == datetime(2024, 1, 1, 0, 0, 0)


def test_gorman_date_with_time_to_gregorian_datetime() -> None:
    """GormanDate with time should preserve time when converting to datetime."""
    gorman = GormanDate(year=2024, month=1, day=1, time=time(12, 30, 45))
    result = gorman.to_gregorian_datetime()
    
    assert result == datetime(2024, 1, 1, 12, 30, 45)


def test_intermission_to_gregorian() -> None:
    """Intermission.to_gregorian() should convert to Gregorian date."""
    intermission = Intermission(year=2024, day=1)
    result = intermission.to_gregorian()
    
    assert result == date(2024, 12, 30)


def test_intermission_to_gregorian_datetime() -> None:
    """Intermission.to_gregorian_datetime() should convert to Gregorian datetime."""
    intermission = Intermission(year=2024, day=1)
    result = intermission.to_gregorian_datetime()
    
    assert result == datetime(2024, 12, 30, 0, 0, 0)


def test_intermission_with_time_to_gregorian_datetime() -> None:
    """Intermission with time should preserve time when converting to datetime."""
    intermission = Intermission(year=2024, day=1, time=time(15, 30, 0))
    result = intermission.to_gregorian_datetime()
    
    assert result == datetime(2024, 12, 30, 15, 30, 0)


def test_gorman_date_is_immutable() -> None:
    """GormanDate should be immutable (frozen dataclass)."""
    gorman = GormanDate(year=2024, month=1, day=1)
    
    with pytest.raises(Exception):  # dataclass.FrozenInstanceError
        gorman.year = 2025


def test_intermission_is_immutable() -> None:
    """Intermission should be immutable (frozen dataclass)."""
    intermission = Intermission(year=2024, day=1)
    
    with pytest.raises(Exception):  # dataclass.FrozenInstanceError
        intermission.year = 2025


def test_gorman_date_str() -> None:
    """GormanDate.__str__() should return human-readable format."""
    g = GormanDate(year=2024, month=1, day=15)
    assert str(g) == "15 March 2024"
    
    g2 = GormanDate(year=2024, month=13, day=28)
    assert str(g2) == "28 Gormanuary 2024"
    
    g3 = GormanDate(year=2024, month=5, day=1)
    assert str(g3) == "1 Quintilis 2024"


def test_intermission_str() -> None:
    """Intermission.__str__() should return human-readable format."""
    i = Intermission(year=2024, day=1)
    assert str(i) == "Intermission 1 2024"
    
    i2 = Intermission(year=2024, day=2)
    assert str(i2) == "Intermission 2 2024"
    
    i3 = Intermission(year=2023, day=1)
    assert str(i3) == "Intermission 1 2023"
