import datetime
from datetime import timezone
from typing import Sequence, Tuple
from unittest import TestCase

import click
from click.testing import CliRunner
from dateutil.tz import tzlocal

from launchable.utils.click import DATETIME_WITH_TZ, KEY_VALUE, convert_to_seconds


class DurationTypeTest(TestCase):
    def test_convert_to_seconds(self):
        self.assertEqual(convert_to_seconds('30s'), 30)
        self.assertEqual(convert_to_seconds('5m'), 300)
        self.assertEqual(convert_to_seconds('1h30m'), 5400)
        self.assertEqual(convert_to_seconds('1d10h15m'), 123300)
        self.assertEqual(convert_to_seconds('15m 1d 10h'), 123300)

        with self.assertRaises(ValueError):
            convert_to_seconds('1h30k')


class KeyValueTypeTest(TestCase):
    def test_conversion(self):
        def scenario(expected: Sequence[Tuple[str, str]], *args):
            actual: Sequence[Tuple[str, str]] = []

            @click.command()
            @click.option(
                '-f',
                'args',
                multiple=True,
                type=KEY_VALUE,
            )
            def hello(args: Sequence[Tuple[str, str]]):
                nonlocal actual
                actual = args

            result = CliRunner().invoke(hello, args)
            self.assertEqual(0, result.exit_code, result.stdout)
            self.assertSequenceEqual(expected, actual)

        scenario([])
        scenario([('bar', 'zot')], '-f', 'bar=zot')
        scenario([('bar', 'zot'), ('a', 'b')], '-f', 'bar=zot', '-f', 'a=b')


class TimestampTypeTest(TestCase):
    def test_conversion(self):
        def scenario(expected: str, *args):
            actual: datetime.datetime = datetime.datetime.now()

            @click.command()
            @click.option(
                '-t',
                'timestamp',
                type=DATETIME_WITH_TZ,
            )
            def time(timestamp: datetime.datetime):
                nonlocal actual
                actual = timestamp

            result = CliRunner().invoke(time, args)

            self.assertEqual(0, result.exit_code, result.stdout)
            self.assertEqual(expected, actual)

        scenario(datetime.datetime(2023, 10, 1, 12, 0, 0, tzinfo=tzlocal()), '-t', '2023-10-01 12:00:00')
        scenario(datetime.datetime(2023, 10, 1, 20, 0, 0, tzinfo=timezone.utc), '-t', '2023-10-01 20:00:00+00:00')
        scenario(datetime.datetime(2023, 10, 1, 20, 0, 0, tzinfo=timezone.utc), '-t', '2023-10-01T20:00:00Z')
