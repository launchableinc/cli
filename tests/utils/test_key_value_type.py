from unittest import TestCase

from launchable.utils.key_value_type import normalize_key_value_types


class NormalizeKeyValueTest(TestCase):
    def test_normalize_key_value_types(self):
        # <click8.0
        result = normalize_key_value_types((("os", "ubuntu"), ("python", "3.6")))
        self.assertEqual(result, [("os", "ubuntu"), ("python", "3.6")])

        # >=click8.0
        result = normalize_key_value_types(("('os', 'ubuntu')", "('python', '3.8')"))
        self.assertEqual(result, [("os", "ubuntu"), ("python", "3.8")])
