from typing import Sequence, Tuple
from unittest import TestCase

import click
from click.testing import CliRunner

from launchable.utils.click import KEY_VALUE, convert_to_seconds


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
