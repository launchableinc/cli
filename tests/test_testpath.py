from launchable.testpath import FilePathNormalizer

import subprocess
import tempfile
import unittest
import pathlib


class TestFilePathNormalizer(unittest.TestCase):
    def test_relative_path(self):
        n = FilePathNormalizer()
        self.assertEqual('some/relative/path',
                         n.relativize('some/relative/path'))

    def test_base_path(self):
        n = FilePathNormalizer(base_path='/some')
        self.assertEqual('relative/path', n.relativize('relative/path'))
        self.assertEqual('absolute/path', n.relativize('/some/absolute/path'))

    def test_normalize_path(self):
        n = FilePathNormalizer()
        self.assertEqual('some/relative/path',
                         n.relativize('some/relative/omit/../path'))

    def test_no_base_path_inference(self):
        n = FilePathNormalizer(no_base_path_inference=True)
        self.assertEqual('some/relative/path',
                         n.relativize('some/relative/path'))
        self.assertEqual('/some/absolute/path',
                         n.relativize('/some/absolute/path'))

        n = FilePathNormalizer(base_path='/some', no_base_path_inference=True)
        self.assertEqual('relative/path', n.relativize('relative/path'))
        self.assertEqual('absolute/path', n.relativize('/some/absolute/path'))

    def test_inference_git(self):
        with tempfile.TemporaryDirectory() as tempdirname:
            temppath = pathlib.PurePath(tempdirname)
            self._run_command(
                ['git', 'init',
                 str(temppath.joinpath("gitrepo"))])

            n = FilePathNormalizer()
            self.assertEqual(
                'some/relative/path',
                n.relativize(
                    str(temppath.joinpath('gitrepo', 'some/relative/path'))))

    def test_inference_git_submodule(self):
        with tempfile.TemporaryDirectory() as tempdirname:
            temppath = pathlib.PurePath(tempdirname)
            self._run_command(
                ['git', 'init',
                 str(temppath.joinpath("submod"))])
            self._run_command(
                ['git', 'commit', '--allow-empty', '--message', 'test commit'],
                cwd=str(temppath.joinpath("submod")))

            self._run_command(
                ['git', 'init',
                 str(temppath.joinpath("gitrepo"))])
            self._run_command([
                'git', 'submodule', 'add',
                str(temppath.joinpath("submod")), 'submod'
            ],
                              cwd=str(temppath.joinpath("gitrepo")))

            n = FilePathNormalizer()
            self.assertEqual(
                'submod/some/relative/path',
                n.relativize(
                    str(
                        temppath.joinpath('gitrepo',
                                          'submod/some/relative/path'))))

    def _run_command(self, args, cwd=None):
        # Use check_output here to capture stderr for a better error message.
        try:
            subprocess.check_output(args,
                                    cwd=cwd,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True,
                                    env={
                                        "GIT_AUTHOR_NAME":
                                        "Test User <user@example.com>",
                                        "GIT_COMMITTER_NAME":
                                        "Test User <user@example.com>",
                                    })
        except subprocess.CalledProcessError as e:
            self.fail(
                "Failed to execute a command: {}\nSTDOUT: {}\nSTDERR: {}\n".
                format(e, e.stdout, e.stderr))


if __name__ == '__main__':
    unittest.main()
