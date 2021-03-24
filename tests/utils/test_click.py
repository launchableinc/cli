from unittest import TestCase
from launchable.utils.click import convert_to_seconds


class DurationTypeTest(TestCase):
    def test_convert_to_seconds(self):
        self.assertEqual(convert_to_seconds('30s'), 30)
        self.assertEqual(convert_to_seconds('5m'), 300)
        self.assertEqual(convert_to_seconds('1h30m'), 5400)
        self.assertEqual(convert_to_seconds('1d10h15m'), 123300)
        self.assertEqual(convert_to_seconds('15m 1d 10h'), 123300)

        with self.assertRaises(ValueError):
            convert_to_seconds('1h30k')
