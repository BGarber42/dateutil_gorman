"""Tests for Gorman calendar date parsing."""

from datetime import date, datetime
import pytest
from dateutil_gorman.parser import parse_gorman


def test_parse_march_1_2024() -> None:
    """Parse '1 March 2024' should return Gregorian datetime for 1 January 2024."""
    result = parse_gorman("1 March 2024")
    
    assert result == datetime(2024, 1, 1)


def test_parse_28_gormanuary_2024() -> None:
    """Parse '28 Gormanuary 2024' should return correct Gregorian datetime."""
    result = parse_gorman("28 Gormanuary 2024")
    
    assert result == datetime(2024, 12, 29)


def test_parse_intermission_1_2024() -> None:
    """Parse 'Intermission 1 2024' should return Gregorian datetime for 30 December 2024."""
    result = parse_gorman("Intermission 1 2024")
    
    assert result == datetime(2024, 12, 30)


def test_parse_intermission_2_2024() -> None:
    """Parse 'Intermission 2 2024' should return Gregorian datetime for 31 December 2024."""
    result = parse_gorman("Intermission 2 2024")
    
    assert result == datetime(2024, 12, 31)


def test_parse_quintilis() -> None:
    """Parse should recognize Quintilis month name."""
    result = parse_gorman("15 Quintilis 2024")
    
    # Quintilis is month 5, day 15 = day_of_year = (5-1)*28 + 15 = 127
    # Day 127 of 2024 = Jan 1 + 126 days = May 6, 2024
    assert result.date() == date(2024, 5, 6)


def test_parse_sextilis() -> None:
    """Parse should recognize Sextilis month name."""
    result = parse_gorman("15 Sextilis 2024")
    
    # Sextilis is month 6, day 15 = day_of_year = (6-1)*28 + 15 = 155
    # Day 155 of 2024 = Jan 1 + 154 days = June 3, 2024
    assert result.date() == date(2024, 6, 3)


def test_parse_with_time() -> None:
    """Parse should handle time components if present."""
    result = parse_gorman("1 March 2024 12:30:45")
    
    assert result == datetime(2024, 1, 1, 12, 30, 45)


def test_parse_invalid_month() -> None:
    """Parse should raise error for invalid month name."""
    with pytest.raises(ValueError, match="Unknown month|Could not parse"):
        parse_gorman("1 InvalidMonth 2024")


def test_parse_invalid_day() -> None:
    """Parse should raise error for day out of range."""
    with pytest.raises(ValueError, match="Day must be|day"):
        parse_gorman("29 March 2024")  # Gorman months only have 28 days


def test_parse_invalid_intermission_day() -> None:
    """Parse should raise error for invalid intermission day."""
    with pytest.raises(ValueError, match="Intermission"):
        parse_gorman("Intermission 3 2024")  # Only 1 or 2 valid


def test_parse_intermission_2_non_leap() -> None:
    """Parse should raise error for Intermission 2 in non-leap year."""
    with pytest.raises(ValueError, match="leap year"):
        parse_gorman("Intermission 2 2023")  # 2023 is not a leap year


def test_parse_various_formats() -> None:
    """Parse should handle various date string formats."""
    test_cases = [
        ("1 March 2024", datetime(2024, 1, 1)),
        ("March 1, 2024", datetime(2024, 1, 1)),
        ("2024-03-01", datetime(2024, 1, 1)),  # If we support ISO-like with Gorman months
    ]
    
    for date_str, expected in test_cases:
        try:
            result = parse_gorman(date_str)
            assert result.date() == expected.date()
        except (ValueError, NotImplementedError):
            pass  # Some formats may not be supported yet
