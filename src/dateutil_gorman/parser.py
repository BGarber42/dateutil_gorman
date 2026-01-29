"""Parser for Gorman calendar date strings."""

import re
from datetime import datetime, time
from dateutil_gorman.constants import GORMAN_MONTHS
from dateutil_gorman.conversion import gorman_to_gregorian, intermission_to_gregorian, _is_leap_year


def parse_gorman(date_string: str) -> datetime:
    """Parse a Gorman calendar date string and return a Gregorian datetime.
    
    Supported formats:
    - "1 March 2024"
    - "28 Gormanuary 2024"
    - "Intermission 1 2024"
    - "Intermission 2 2024"
    
    Args:
        date_string: Gorman date string to parse
    
    Returns:
        Gregorian datetime corresponding to the Gorman date
    
    Raises:
        ValueError: If the date string is invalid or cannot be parsed
    """
    date_string = date_string.strip()
    
    intermission_match = re.match(r"Intermission\s+(\d+)\s+(\d{4})", date_string, re.IGNORECASE)
    if intermission_match:
        day = int(intermission_match.group(1))
        year = int(intermission_match.group(2))
        
        if day not in (1, 2):
            raise ValueError(f"Intermission day must be 1 or 2, got {day}")
        
        if day == 2 and not _is_leap_year(year):
            raise ValueError(f"Intermission day 2 is only valid in leap years, {year} is not a leap year")
        
        gregorian_date = intermission_to_gregorian(year, day)
        return datetime.combine(gregorian_date, datetime.min.time())
    
    month_pattern = "|".join(re.escape(month) for month in GORMAN_MONTHS)
    month_pattern = f"({month_pattern})"
    
    time_pattern = r"(?:\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?"
    
    pattern1 = rf"(\d{{1,2}})\s+{month_pattern}\s+(\d{{4}}){time_pattern}"
    match = re.match(pattern1, date_string, re.IGNORECASE)
    if match:
        groups = match.groups()
        day = int(groups[0])
        month_name = groups[1]
        year = int(groups[2])
        hour = int(groups[3]) if groups[3] else 0
        minute = int(groups[4]) if groups[4] else 0
        second = int(groups[5]) if groups[5] else 0
    else:
        pattern2 = rf"{month_pattern}\s+(\d{{1,2}})[,\s]+\s*(\d{{4}}){time_pattern}"
        match = re.match(pattern2, date_string, re.IGNORECASE)
        if match:
            groups = match.groups()
            month_name = groups[0]
            day = int(groups[1])
            year = int(groups[2])
            hour = int(groups[3]) if groups[3] else 0
            minute = int(groups[4]) if groups[4] else 0
            second = int(groups[5]) if groups[5] else 0
        else:
            raise ValueError(f"Could not parse Gorman date string: {date_string}")
    
    month_name_lower = month_name.lower()
    month_index = None
    for i, gorman_month in enumerate(GORMAN_MONTHS):
        if gorman_month.lower() == month_name_lower:
            month_index = i + 1
            break
    
    if month_index is None:
        raise ValueError(f"Unknown month name: {month_name}. Valid months are: {', '.join(GORMAN_MONTHS)}")
    
    if day < 1 or day > 28:
        raise ValueError(f"Day must be between 1 and 28 for Gorman months, got {day}")
    
    gregorian_date = gorman_to_gregorian(year, month_index, day)
    return datetime.combine(gregorian_date, time(hour, minute, second))
    
    raise ValueError(f"Could not parse Gorman date string: {date_string}")
