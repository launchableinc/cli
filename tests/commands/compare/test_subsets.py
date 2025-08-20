import os
from unittest import mock

from tests.cli_test_case import CliTestCase


class SubsetsTest(CliTestCase):

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subsets(self):
        # Create subset-before.txt
        with open("subset-before.txt", "w") as f:
            f.write("\n".join([
                "src/test/java/example/DivTest.java",
                "src/test/java/example/DB1Test.java",
                "src/test/java/example/MulTest.java",
                "src/test/java/example/Add2Test.java",
                "src/test/java/example/File1Test.java",
                "src/test/java/example/File0Test.java",
                "src/test/java/example/SubTest.java",
                "src/test/java/example/DB0Test.java",
                "src/test/java/example/AddTest.java",
            ]))

        # Create subset-after.txt
        with open("subset-after.txt", "w") as f:
            f.write("\n".join([
                "src/test/java/example/Add2Test.java",
                "src/test/java/example/MulTest.java",
                "src/test/java/example/AddTest.java",
                "src/test/java/example/File1Test.java",
                "src/test/java/example/DivTest.java",
                "src/test/java/example/File0Test.java",
                "src/test/java/example/DB1Test.java",
                "src/test/java/example/DB0Test.java",
                "src/test/java/example/SubTest.java",
            ]))

        result = self.cli('compare', 'subsets', "subset-before.txt", "subset-after.txt", mix_stderr=False)
        expect = """|   Before |   After |   After - Before | Test                                 |
|----------|---------|------------------|--------------------------------------|
|        9 |       3 |               -6 | src/test/java/example/AddTest.java   |
|        4 |       1 |               -3 | src/test/java/example/Add2Test.java  |
|        3 |       2 |               -1 | src/test/java/example/MulTest.java   |
|        5 |       4 |               -1 | src/test/java/example/File1Test.java |
|        6 |       6 |               +0 | src/test/java/example/File0Test.java |
|        8 |       8 |               +0 | src/test/java/example/DB0Test.java   |
|        7 |       9 |               +2 | src/test/java/example/SubTest.java   |
|        1 |       5 |               +4 | src/test/java/example/DivTest.java   |
|        2 |       7 |               +5 | src/test/java/example/DB1Test.java   |
"""

        self.assertEqual(result.stdout, expect)

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subsets_when_new_tests(self):
        # Create subset-before.txt
        with open("subset-before.txt", "w") as f:
            f.write("\n".join([
                "src/test/java/example/SubTest.java",
                "src/test/java/example/DivTest.java",
                "src/test/java/example/Add2Test.java",
                "src/test/java/example/File0Test.java",
                "src/test/java/example/AddTest.java",
                "src/test/java/example/File1Test.java",
                "src/test/java/example/MulTest.java",
                "src/test/java/example/DB0Test.java",
                "src/test/java/example/DB1Test.java"
            ]))

        # Create subset-after.txt (which includes additional test path NewTest.java)
        with open("subset-after.txt", "w") as f:
            f.write("\n".join([
                "src/test/java/example/NewTest.java",
                "src/test/java/example/SubTest.java",
                "src/test/java/example/File0Test.java",
                "src/test/java/example/DB1Test.java",
                "src/test/java/example/DivTest.java",
                "src/test/java/example/MulTest.java",
                "src/test/java/example/File1Test.java",
                "src/test/java/example/DB0Test.java",
                "src/test/java/example/Add2Test.java",
                "src/test/java/example/AddTest.java"
            ]))

        result = self.cli('compare', 'subsets', "subset-before.txt", "subset-after.txt", mix_stderr=False)
        expect = """| Before   |   After | After - Before   | Test                                 |
|----------|---------|------------------|--------------------------------------|
| -        |       1 | NEW              | src/test/java/example/NewTest.java   |
| 9        |       4 | -5               | src/test/java/example/DB1Test.java   |
| 4        |       3 | -1               | src/test/java/example/File0Test.java |
| 7        |       6 | -1               | src/test/java/example/MulTest.java   |
| 8        |       8 | +0               | src/test/java/example/DB0Test.java   |
| 1        |       2 | +1               | src/test/java/example/SubTest.java   |
| 6        |       7 | +1               | src/test/java/example/File1Test.java |
| 2        |       5 | +3               | src/test/java/example/DivTest.java   |
| 5        |      10 | +5               | src/test/java/example/AddTest.java   |
| 3        |       9 | +6               | src/test/java/example/Add2Test.java  |
"""

        self.assertEqual(result.stdout, expect)

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subsets_when_deleted_tests(self):
        # Create subset-before.txt
        with open("subset-before.txt", "w") as f:
            f.write("\n".join([
                "src/test/java/example/NewTest.java",
                "src/test/java/example/SubTest.java",
                "src/test/java/example/File0Test.java",
                "src/test/java/example/DB1Test.java",
                "src/test/java/example/DivTest.java",
                "src/test/java/example/MulTest.java",
                "src/test/java/example/File1Test.java",
                "src/test/java/example/DB0Test.java",
                "src/test/java/example/Add2Test.java",
                "src/test/java/example/AddTest.java"
            ]))

        # Create subset-after.txt (which doesn't include NewTest.java)
        with open("subset-after.txt", "w") as f:
            f.write("\n".join([
                "src/test/java/example/DB1Test.java",
                "src/test/java/example/DB0Test.java",
                "src/test/java/example/File1Test.java",
                "src/test/java/example/SubTest.java",
                "src/test/java/example/AddTest.java",
                "src/test/java/example/MulTest.java",
                "src/test/java/example/File0Test.java",
                "src/test/java/example/Add2Test.java",
                "src/test/java/example/DivTest.java"
            ]))

        result = self.cli('compare', 'subsets', "subset-before.txt", "subset-after.txt", mix_stderr=False)
        expect = """|   Before | After   | After - Before   | Test                                 |
|----------|---------|------------------|--------------------------------------|
|        1 | -       | DELETED          | src/test/java/example/NewTest.java   |
|        8 | 2       | -6               | src/test/java/example/DB0Test.java   |
|       10 | 5       | -5               | src/test/java/example/AddTest.java   |
|        7 | 3       | -4               | src/test/java/example/File1Test.java |
|        4 | 1       | -3               | src/test/java/example/DB1Test.java   |
|        9 | 8       | -1               | src/test/java/example/Add2Test.java  |
|        6 | 6       | +0               | src/test/java/example/MulTest.java   |
|        2 | 4       | +2               | src/test/java/example/SubTest.java   |
|        3 | 7       | +4               | src/test/java/example/File0Test.java |
|        5 | 9       | +4               | src/test/java/example/DivTest.java   |
"""

        self.assertEqual(result.stdout, expect)

    def tearDown(self):
        if os.path.exists("subset-before.txt"):
            os.remove("subset-before.txt")
        if os.path.exists("subset-after.txt"):
            os.remove("subset-after.txt")
