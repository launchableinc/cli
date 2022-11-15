from pathlib import Path
from unittest import TestCase

from dateutil.parser import parse

from launchable.utils.git_log_parser import ChangedFile, GitCommit, parse_git_log


class GitLogParserTest(TestCase):
    test_file_path = Path(__file__).parent.joinpath('../data/git_log_ingest/sample.out').resolve()

    def test_parse(self):
        with self.test_file_path.open('r') as fp:
            commits = parse_git_log(fp)

        self.maxDiff = None
        self.assertEqual(commits, [
            GitCommit(
                commit_hash="1f0c18ea3df6575b4132b311d52a339af34c90ba",
                parents=["b068a8a515e6cbbb2d6673ddb2c421939bd618b7"],
                author_email="example1@example.com",
                author_time=parse("2022-09-21T15:59:21-07:00"),
                committer_email="example1@example.com",
                committer_time=parse("2022-09-21T16:34:35-07:00"),
                changed_files=[
                    ChangedFile(
                        path="launchable/commands/subset.py",
                                added=24,
                                deleted=4),
                    ChangedFile(
                        path="launchable/test_runners/gradle.py",
                        added=24,
                        deleted=0),
                    ChangedFile(
                        path="tests/test_runners/test_gradle.py",
                        added=62,
                        deleted=0),
                ],
            ),
            GitCommit(
                commit_hash="b068a8a515e6cbbb2d6673ddb2c421939bd618b7",
                parents=["cb1d1b797726fe16e661d8377bd807f2508e9df4"],
                author_email="example2@example.com",
                author_time=parse("2022-09-16T17:03:52+00:00"),
                committer_email="example3@example.com",
                committer_time=parse("2022-09-16T17:03:52+00:00"),
                changed_files=[
                    ChangedFile(path="docs/README.md", added=1, deleted=1),
                    ChangedFile(path="docs/SUMMARY.md", added=1, deleted=0),
                    ChangedFile(
                        path="docs/features/predictive-test-selection/requesting-and-running-a-subset-of-tests/README.md",
                        added=1,
                        deleted=1),
                    ChangedFile(
                        path="docs/features/predictive-test-selection/requesting-and-running-a-subset-of-tests/"
                             "zero-input-subsetting.md",
                        added=26,
                        deleted=0),
                    ChangedFile(
                        path="docs/sending-data-to-launchable/README.md",
                        added=1,
                        deleted=1),
                ],
            ),
            GitCommit(
                commit_hash="cb1d1b797726fe16e661d8377bd807f2508e9df4",
                parents=[
                    "fba956e638a7d91a6a89a40132d7d1c8f5f40d71",
                    "f22ea479d9c088d0da4109118b25c3f5b1b7b96e"
                ],
                author_email="example4@example.com",
                author_time=parse("2022-09-15T14:51:22-04:00"),
                committer_email="example5@example.com",
                committer_time=parse("2022-09-15T14:51:22-04:00"),
                changed_files=[],
            ),
            GitCommit(
                commit_hash="f22ea479d9c088d0da4109118b25c3f5b1b7b96e",
                parents=["38d92db01c0603978aab3a7bd43fbb5f5957c8f3"],
                author_email="example4@example.com",
                author_time=parse("2022-09-15T14:51:14-04:00"),
                committer_email="example5@example.com",
                committer_time=parse("2022-09-15T14:51:14-04:00"),
                changed_files=[
                    ChangedFile(
                        path="docs/features/insights/flaky-tests.md",
                                added=2,
                                deleted=2),
                ],
            ),
            GitCommit(
                commit_hash="38d92db01c0603978aab3a7bd43fbb5f5957c8f3",
                parents=["fba956e638a7d91a6a89a40132d7d1c8f5f40d71"],
                author_email="example1@example.com",
                author_time=parse("2022-09-15T11:29:45-07:00"),
                committer_email="example1@example.com",
                committer_time=parse("2022-09-15T11:29:45-07:00"),
                changed_files=[
                    ChangedFile(
                        path="docs/features/insights/flaky-tests.md",
                                added=3,
                                deleted=3),
                ],
            ),
            GitCommit(
                commit_hash="fba956e638a7d91a6a89a40132d7d1c8f5f40d71",
                parents=[
                    "a08f6ab9cb534a6818998883f8712aedddd459ae",
                    "039f5f6f7874836739ec7cbfe2bf9d0ffea0f8d3",
                ],
                author_email="example2@example.com",
                author_time=parse("2022-09-13T13:28:45-04:00"),
                committer_email="example2@example.com",
                committer_time=parse("2022-09-13T13:28:45-04:00"),
                changed_files=[],
            ),
            GitCommit(
                commit_hash="039f5f6f7874836739ec7cbfe2bf9d0ffea0f8d3",
                parents=[
                    "de1076e9a6c4efd28339496ac10906693e980ce3",
                    "8a7cb5c8cef17b9d5323c0338dce9d7b8639c85b",
                ],
                author_email="example6@example.com",
                author_time=parse("2022-09-14T02:24:32+09:00"),
                committer_email="example5@example.com",
                committer_time=parse("2022-09-14T02:24:32+09:00"),
                changed_files=[],
            ),
            GitCommit(
                commit_hash="8a7cb5c8cef17b9d5323c0338dce9d7b8639c85b",
                parents=["de1076e9a6c4efd28339496ac10906693e980ce3"],
                author_email="example6@example.com",
                author_time=parse("2022-09-13T09:43:59-07:00"),
                committer_email="example6@example.com",
                committer_time=parse("2022-09-13T09:43:59-07:00"),
                changed_files=[
                    ChangedFile(
                        path="docs/resources/integrations/maven.md",
                                added=3,
                                deleted=1),
                ],
            ),
            GitCommit(
                commit_hash="a08f6ab9cb534a6818998883f8712aedddd459ae",
                parents=["de1076e9a6c4efd28339496ac10906693e980ce3"],
                author_email="example2@example.com",
                author_time=parse("2022-09-13T14:43:41+00:00"),
                committer_email="example3@example.com",
                committer_time=parse("2022-09-13T14:43:41+00:00"),
                changed_files=[
                    ChangedFile(
                        path="docs/concepts/subset.md", added=1, deleted=1),
                ],
            ),
        ])
