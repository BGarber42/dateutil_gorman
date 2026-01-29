# dateutil-gorman

A Python library for the **Gorman Calendar**: a 13-month calendar where each month has 28 days, plus one or two intermission days at the end of the year.

- **13 months** of 28 days each (364 days)
- **Intermission**: 1 day in common years, 2 days in leap years (Intermission 1 and Intermission 2), each a separate 24-hour day
- **Month names**: March, April, May, June, Quintilis, Sextilis, September, October, November, December, January, February, Gormanuary

Requires Python 3.10+.

## Installation

```bash
pip install dateutil-gorman
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add dateutil-gorman
```

## Quick start

```python
from datetime import date
from dateutil_gorman import GormanDate, gregorian_to_gorman, gorman_to_gregorian, parse_gorman

# Gregorian → Gorman
g = gregorian_to_gorman(date(2024, 6, 15))
print(g)  # 15 June 2024

# Gorman → Gregorian
d = gorman_to_gregorian(2024, 6, 15)
print(d)  # 2024-06-15

# Parse a Gorman date string
dt = parse_gorman("28 Gormanuary 2024")
print(dt)  # 2024-02-28 00:00:00
```

## Examples

### Intermission days

The last day(s) of the Gregorian year are intermission in Gorman: one day in common years, two in leap years.

```python
from datetime import date
from dateutil_gorman import gregorian_to_gorman, Intermission

# Common year: Dec 31 is Intermission 1
g = gregorian_to_gorman(date(2023, 12, 31))
print(g)                    # Intermission 1 2023
print(type(g).__name__)     # Intermission
print(g.to_gregorian())     # 2023-12-31

# Leap year: Dec 30 = Intermission 1, Dec 31 = Intermission 2
g1 = gregorian_to_gorman(date(2024, 12, 30))
g2 = gregorian_to_gorman(date(2024, 12, 31))
print(g1)   # Intermission 1 2024
print(g2)   # Intermission 2 2024
```

### From ISO and ordinal

```python
from dateutil_gorman import GormanDate

# Parse a Gregorian ISO date (YYYY-MM-DD) and convert to Gorman
g = GormanDate.fromisoformat("2024-07-04")
print(g)  # 4 Quintilis 2024

# From proleptic Gregorian ordinal (same as datetime.date)
g = GormanDate.fromordinal(738000)
print(g.to_gregorian())  # 2024-01-15
```

### Gorman week calendar

Each Gorman month has 4 weeks; the year has 52 weeks (intermission days are outside any week).

```python
from dateutil_gorman import GormanDate

g = GormanDate(2024, 6, 15)
year, week, weekday = g.gorman_week_calendar()
print(f"Year {year}, week {week}, weekday {weekday}")  # Year 2024, week 21, weekday 6

# Week of month (1–4) and week of year (1–52)
print(g.week_of_month())   # 3
print(g.week_of_year())    # 21

# Build a GormanDate from (year, week, weekday)
g2 = GormanDate.from_gorman_week_calendar(2024, 21, 6)
print(g2)  # 15 June 2024
```

### Immutable updates with replace

```python
from dateutil_gorman import GormanDate

g = GormanDate(2024, 6, 15)
g2 = g.replace(day=1)
print(g2)  # 1 June 2024
# g is unchanged
print(g)   # 15 June 2024
```

### Parsing Gorman date strings

```python
from dateutil_gorman import parse_gorman

# Day month year
parse_gorman("15 June 2024")           # 2024-06-15 00:00:00

# Month day, year
parse_gorman("June 15, 2024")          # 2024-06-15 00:00:00

# With time
parse_gorman("15 June 2024 14:30")     # 2024-06-15 14:30:00
parse_gorman("15 June 2024 14:30:45") # 2024-06-15 14:30:45

# Intermission
parse_gorman("Intermission 1 2024")    # 2024-12-30 00:00:00 (leap year)
parse_gorman("Intermission 2 2024")    # 2024-12-31 00:00:00 (leap year only)
```

### Preserving time with datetime

When you convert a `datetime`, the time is stored on the Gorman value and restored when converting back.

```python
from datetime import datetime
from dateutil_gorman import gregorian_to_gorman

dt = datetime(2024, 6, 15, 14, 30, 0)
g = gregorian_to_gorman(dt)
print(g.time)           # 14:30:00
print(g.to_gregorian_datetime())  # 2024-06-15 14:30:00
```

## API overview

### Types

- **`GormanDate`** — A date within a Gorman month (`year`, `month` 1–13, `day` 1–28, optional `time`). Immutable. Methods include:
  - `to_gregorian()` / `to_gregorian_datetime()` — convert to Gregorian
  - `fromisoformat(s)` — parse ISO date string (YYYY-MM-DD) and convert to Gorman
  - `fromordinal(ordinal)` — from proleptic Gregorian ordinal
  - `from_gorman_week_calendar(year, week, weekday)` — from (year, week 1–52, weekday 1–7)
  - `gorman_week_calendar()` — returns `(year, week, weekday)`
  - `replace(...)` — return a new instance with fields updated
  - `weekday()`, `isoweekday()`, `week_of_month()`, `week_of_year()`, `toordinal()`
  - `__str__` — e.g. `"15 June 2024"`

- **`Intermission`** — One intermission day (`year`, `day` 1 or 2, optional `time`). Immutable. Methods include:
  - `to_gregorian()` / `to_gregorian_datetime()`
  - `fromordinal(ordinal)`
  - `replace(...)`

### Conversion

- **`gregorian_to_gorman(d)`** — `date` or `datetime` → `GormanDate` or `Intermission` (preserves time when given a datetime).
- **`gorman_to_gregorian(year, month, day)`** — Gorman (year, month, day) → `date`.
- **`intermission_to_gregorian(year, day)`** — Intermission (year, day 1 or 2) → `date`.

### Parsing

- **`parse_gorman(date_string)`** — Parse a Gorman date string and return a Gregorian `datetime`. Supports:
  - `"15 June 2024"`, `"June 15, 2024"`
  - Optional time: `"15 June 2024 14:30"`
  - `"Intermission 1 2024"`, `"Intermission 2 2024"` (leap years only for day 2)

### Constants

- **`GORMAN_MONTHS`** — Tuple of 13 month name strings (March … Gormanuary).

## Development

```bash
git clone https://github.com/BGarber42/dateutil_gorman.git
cd dateutil_gorman
uv sync --all-extras
uv run pytest
uv run mypy src
uv run ruff check src tests
```

## License

MIT. See [LICENSE](LICENSE) for details.
