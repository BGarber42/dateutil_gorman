# dateutil-gorman

`dateutil-gorman` is a typed Python package for converting between Gregorian
dates and the Gorman calendar.

## Features

- `src/` layout with a small, explicit public API.
- Immutable value objects for regular Gorman dates and intermission days.
- Bidirectional Gregorian conversion helpers.
- String parsing for common Gorman date formats.
- No runtime dependencies outside the Python standard library.

## Installation

```bash
pip install dateutil-gorman
```

For local development with `uv`:

```bash
uv sync --extra dev
```

## Quick Start

```python
from datetime import date, datetime

from dateutil_gorman import (
    GormanDate,
    gregorian_to_gorman,
    gorman_to_gregorian,
    parse_gorman,
)

gorman_value = gregorian_to_gorman(date(2024, 1, 1))
assert str(gorman_value) == "1 March 2024"

gregorian_value = gorman_to_gregorian(2024, 6, 15)
assert gregorian_value.isoformat() == "2024-06-03"

parsed = parse_gorman("June 15, 2024 14:30")
assert parsed == datetime(2024, 4, 8, 14, 30)

same_day = GormanDate.fromisoformat("2024-06-10")
assert same_day.to_gregorian().isoformat() == "2024-06-10"
```

## Usage

### Convert Gregorian values

```python
from datetime import date

from dateutil_gorman import gregorian_to_gorman

assert str(gregorian_to_gorman(date(2024, 12, 30))) == "Intermission 1 2024"
assert str(gregorian_to_gorman(date(2024, 12, 31))) == "Intermission 2 2024"
```

### Work with immutable value objects

```python
from dateutil_gorman import GormanDate

gorman_date = GormanDate(year=2024, month=6, day=15)
updated = gorman_date.replace(day=1)

assert str(gorman_date) == "15 Sextilis 2024"
assert str(updated) == "1 Sextilis 2024"
```

### Parse Gorman strings

```python
from dateutil_gorman import parse_gorman

assert parse_gorman("15 June 2024").isoformat() == "2024-04-08T00:00:00"
assert parse_gorman("Intermission 1 2024 08:15").isoformat() == "2024-12-30T08:15:00"
```

## Public API

### Classes

- `GormanDate`: Immutable regular-month date with conversion, week-calendar,
  ordinal, and replacement helpers.
- `Intermission`: Immutable year-end intermission day with Gregorian
  conversion and replacement helpers.

### Functions

- `gregorian_to_gorman(d)`: Convert a Gregorian `date` or `datetime`.
- `gorman_to_gregorian(year, month, day)`: Convert a regular Gorman date.
- `intermission_to_gregorian(year, day)`: Convert an intermission day.
- `parse_gorman(date_string)`: Parse supported Gorman date strings into a
  Gregorian `datetime`.

### Constants

- `GORMAN_MONTHS`: Ordered tuple of month names used by the Gorman calendar.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src
```

## Contributing

1. Fork the repository and create a feature branch.
2. Keep the public API typed and documented with Google-style docstrings.
3. Add or update tests for behavior changes.
4. Run `uv run pytest`, `uv run ruff check .`, and `uv run mypy src` before opening a pull request.

## License

Released under the MIT License.
