import datetime
import re
import sys
from typing import Dict, Optional, Tuple

import click
import dateutil.parser
from click import ParamType
from dateutil.tz import tzlocal

# click.Group has the notion of hidden commands but it doesn't allow us to easily add
# the same command under multiple names and hide all but one.


class GroupWithAlias(click.Group):
    def __init__(self, name: Optional[str] = None, commands: Optional[Dict[str, click.Command]] = None, **attrs):
        super().__init__(name, commands, **attrs)
        self.aliases: Dict[str, str] = {}

    def get_command(self, ctx: click.core.Context, cmd_name: str):
        return super().get_command(ctx, cmd_name) or self.aliases.get(cmd_name)

    def add_alias(self, name: str, cmd: str):
        self.aliases[name] = cmd


class PercentageType(ParamType):
    name = "percentage"

    def convert(self, value: str, param: Optional[click.core.Parameter], ctx: Optional[click.core.Context]):
        try:
            if value.endswith('%'):
                x = float(value[:-1]) / 100
                if 0 <= x <= 100:
                    return x
        except ValueError:
            pass

        self.fail("Expected percentage like 50% but got '{}'".format(value), param, ctx)


class DurationType(ParamType):
    name = "duration"

    def convert(self, value: str, param: Optional[click.core.Parameter], ctx: Optional[click.core.Context]):
        try:
            return convert_to_seconds(value)

        except ValueError:
            pass

        self.fail("Expected duration like 3600, 30m, 1h15m but got '{}'".format(value), param, ctx)


class KeyValueType(ParamType):
    name = "key=value"

    '''
    Handles options that take key/value pairs.

    The preferred syntax is "--option key=value" and that's what we should be advertising in docs and help,
    but for compatibility (?) we accept "--option key:value"

    Typically, this is used with multiple=True to produce `Sequence[Tuple[str, str]]`.
    '''
    error_message = "Expected a key-value pair formatted as --option key=value, but got '{}'"

    def convert(
            self, value: str, param: Optional[click.core.Parameter], ctx: Optional[click.core.Context]
    ) -> Tuple[str, str]:

        for delimiter in ['=', ':']:
            if delimiter in value:
                kv = value.split(delimiter, 1)
                if len(kv) != 2:
                    self.fail(self.error_message.format(value))
                return kv[0].strip(), kv[1].strip()

        self.fail(self.error_message.format(value))


class FractionType(ParamType):
    name = "fraction"

    def convert(self, value: str, param: Optional[click.core.Parameter], ctx: Optional[click.core.Context]):
        try:
            v = value.strip().split('/')
            if len(v) == 2:
                n = int(v[0])
                d = int(v[1])

                return (n, d)

        except ValueError:
            pass

        self.fail("Expected fraction like 1/2 but got '{}'".format(value), param, ctx)


class DateTimeWithTimezoneType(ParamType):
    name = "datetime"

    def convert(self, value: str, param: Optional[click.core.Parameter], ctx: Optional[click.core.Context]):
        try:
            dt = dateutil.parser.parse(value)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=tzlocal())
            return dt
        except ValueError:
            self.fail("Expected datetime like 2023-10-01T12:00:00 but got '{}'".format(value), param, ctx)


PERCENTAGE = PercentageType()
DURATION = DurationType()
FRACTION = FractionType()
KEY_VALUE = KeyValueType()
DATETIME_WITH_TZ = DateTimeWithTimezoneType()

# Can the output deal with Unicode emojis?
try:
    '\U0001f389'.encode(sys.stdout.encoding or "ascii")
    # If stdout encoding is unavailable, such as in case of pipe, err on the safe side (EMOJI=False)
    # This is a judgement call, but given that emojis do not serve functional purposes and purely decorative
    # erring on the safe side seems like a reasonable call.
    EMOJI = True
except UnicodeEncodeError:
    EMOJI = False


def emoji(s: str, fallback: str = ''):
    """
    Used to safely use Emoji where we can.

    Returns 's' in an environment where stdout can deal with emojis, but 'fallback' otherwise.
    """
    return s if EMOJI else fallback


def convert_to_seconds(s: str):
    units = {'s': 1, 'm': 60, 'h': 60 * 60, 'd': 60 * 60 * 24, 'w': 60 * 60 * 24 * 7}

    if s.isdigit():
        return float(s)

    duration = 0
    for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdw]?)', s, flags=re.I):
        val = m.group('val')
        unit = m.group('unit')

        if val is None or unit is None:
            raise ValueError("unable to parse: {}".format(s))

        u = units.get(unit)
        if u is None:
            raise ValueError("unable to parse: {}".format(s))

        duration += int(val) * u

    return float(duration)


def ignorable_error(e: Exception):
    return "An error occurred on Launchable CLI. You can ignore this message since the process will continue. Error: {}".format(e)


def validate_past_datetime(ctx, param, value):
    """
    Validates that the provided datetime is in the past.
    """
    if value is None:
        return value

    if not isinstance(value, datetime.datetime):
        raise click.BadParameter("Expected a datetime object.")

    now = datetime.datetime.now(tz=tzlocal())
    if value >= now:
        raise click.BadParameter("The provided datetime must be in the past. But the value is {}".format(value))

    return value
