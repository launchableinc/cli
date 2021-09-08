from unittest import TestCase

from launchable.utils.file_name_pattern import jvm_test_pattern


class FileNameHeuristicTest(TestCase):
    def test_jvm_file_name(self):
        file_names = [
            'LaunchableTest.java',
            'LaunchableTests.java',
            'LaunchableTestCase.java'
        ]
        for file_name in file_names:
            self.assertTrue(jvm_test_pattern.match(file_name))

        file_names = [
            'LaunchableTest2.java',
            'LaunchableTests2.java',
            'LaunchableTestCase2.java'
            'LaunchableTestUtil.java',
            'LaunchableTestss.java',
            'LaunchableTest2Case.java'
        ]
        for file_name in file_names:
            self.assertFalse(jvm_test_pattern.match(file_name))
