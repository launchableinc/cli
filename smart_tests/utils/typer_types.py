import datetime
import re
import sys
from typing import Annotated, Tuple

import dateutil.parser
import typer
from dateutil.tz import tzlocal


def validate_percentage(value: str) -> float:
    """Convert percentage string to float (0.0-1.0)"""
    try:
        if value.endswith('%'):
            x = float(value[:-1]) / 100
            if 0 <= x <= 100:
                return x
    except ValueError:
        pass

    raise typer.BadParameter(f"Expected percentage like 50% but got '{value}'")


def validate_duration(value: str) -> float:
    """Convert duration string to seconds"""
    try:
        return convert_to_seconds(value)
    except ValueError:
        raise typer.BadParameter(f"Expected duration like 3600, 30m, 1h15m but got '{value}'")


def validate_key_value(value: str) -> Tuple[str, str]:
    """Parse key=value or key:value pairs"""
    if value is None:
        return "", ""

    for delimiter in ['=', ':']:
        if delimiter in value:
            kv = value.split(delimiter, 1)
            if len(kv) == 2:
                return kv[0].strip(), kv[1].strip()

    raise typer.BadParameter(f"Expected a key-value pair formatted as key=value, but got '{value}'")


def validate_fraction(value: str) -> Tuple[int, int]:
    """Parse fraction like 1/2"""
    try:
        v = value.strip().split('/')
        if len(v) == 2:
            n = int(v[0])
            d = int(v[1])
            return (n, d)
    except ValueError:
        pass

    raise typer.BadParameter(f"Expected fraction like 1/2 but got '{value}'")


def validate_datetime_with_tz(value: str) -> datetime.datetime:
    """Parse datetime string and ensure timezone is set"""
    if value is None:
        return None

    try:
        dt = dateutil.parser.parse(value)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=tzlocal())
        return dt
    except ValueError:
        raise typer.BadParameter(f"Expected datetime like 2023-10-01T12:00:00 but got '{value}'")


def validate_past_datetime(value: datetime.datetime) -> datetime.datetime:
    """Validate that the provided datetime is in the past"""
    if value is None:
        return value

    if not isinstance(value, datetime.datetime):
        raise typer.BadParameter("Expected a datetime object.")

    now = datetime.datetime.now(tz=tzlocal())
    if value >= now:
        raise typer.BadParameter(f"The provided datetime must be in the past. But the value is {value}")

    return value


def convert_to_seconds(s: str) -> float:
    """Convert duration string to seconds"""
    units = {'s': 1, 'm': 60, 'h': 60 * 60, 'd': 60 * 60 * 24, 'w': 60 * 60 * 24 * 7}

    if s.isdigit():
        return float(s)

    duration = 0
    for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdw]?)', s, flags=re.I):
        val = m.group('val')
        unit = m.group('unit')

        if val is None or unit is None:
            raise ValueError(f"unable to parse: {s}")

        u = units.get(unit)
        if u is None:
            raise ValueError(f"unable to parse: {s}")

        duration += int(val) * u

    return float(duration)


# Can the output deal with Unicode emojis?
try:
    '\U0001f389'.encode(sys.stdout.encoding or "ascii")
    # If stdout encoding is unavailable, such as in case of pipe, err on the safe side (EMOJI=False)
    # This is a judgement call, but given that emojis do not serve functional purposes and purely decorative
    # erring on the safe side seems like a reasonable call.
    EMOJI = True
except UnicodeEncodeError:
    EMOJI = False


def emoji(s: str, fallback: str = '') -> str:
    """
    Used to safely use Emoji where we can.

    Returns 's' in an environment where stdout can deal with emojis, but 'fallback' otherwise.
    """
    return s if EMOJI else fallback


def ignorable_error(e: Exception) -> str:
    return "An error occurred on Smart Tests CLI. You can ignore this message since the process will continue. " \
           f"Error: {e}"


# Typer Type Parser Classes
class PercentageType:
    """Typer type parser for percentage values like '50%'"""
    name = "percentage"
    __name__ = "PercentageType"

    def __call__(self, value: str) -> float:
        return validate_percentage(value)

    def __repr__(self):
        return "PercentageType()"


class DurationType:
    """Typer type parser for duration values like '30s', '5m', '1h30m'"""
    name = "duration"
    __name__ = "DurationType"

    def __call__(self, value: str) -> float:
        return validate_duration(value)

    def __repr__(self):
        return "DurationType()"


class KeyValueType:
    """Typer type parser for key=value or key:value pairs"""
    name = "key_value"
    __name__ = "KeyValueType"

    def __call__(self, value: str) -> Tuple[str, str]:
        return validate_key_value(value)

    def __repr__(self):
        return "KeyValueType()"


class FractionType:
    """Typer type parser for fraction values like '1/2'"""
    name = "fraction"
    __name__ = "FractionType"

    def __call__(self, value: str) -> Tuple[int, int]:
        return validate_fraction(value)

    def __repr__(self):
        return "FractionType()"


class DateTimeWithTimezoneType:
    """Typer type parser for datetime values with timezone support"""
    name = "datetime_with_tz"
    __name__ = "DateTimeWithTimezoneType"

    def __call__(self, value: str) -> datetime.datetime:
        return validate_datetime_with_tz(value)

    def __repr__(self):
        return "DateTimeWithTimezoneType()"


# Type parser instances for use in type annotations
PERCENTAGE = PercentageType()
DURATION = DurationType()
KEY_VALUE = KeyValueType()
FRACTION = FractionType()
DATETIME_WITH_TZ = DateTimeWithTimezoneType()


# Type annotations for common parameter types
PercentageOption = Annotated[float, typer.Option(parser=validate_percentage)]
DurationOption = Annotated[float, typer.Option(parser=validate_duration)]
KeyValueOption = Annotated[Tuple[str, str], typer.Option(parser=validate_key_value)]
FractionOption = Annotated[Tuple[int, int], typer.Option(parser=validate_fraction)]
DateTimeWithTzOption = Annotated[datetime.datetime, typer.Option(parser=validate_datetime_with_tz)]

# Simplified validators for direct use


def parse_key_value_list(values: list) -> list:
    """Parse a list of key-value strings into tuples"""
    return [validate_key_value(v) for v in values]
