from launchable.testpath import FilePathNormalizer

import subprocess
import tempfile
import unittest
import pathlib
import os.path


class TestFilePathNormalizer(unittest.TestCase):
    def test_relative_path(self):
        n = FilePathNormalizer()
        relpath = os.path.join('foo', 'bar', 'baz')
        self.assertEqual(relpath, n.relativize(relpath))

    def test_base_path(self):
        base = os.path.abspath('base')
        relpath = os.path.join('foo', 'bar', 'baz')
        abspath = os.path.join(base, 'foo', 'bar', 'baz')

        n = FilePathNormalizer(base_path=base)
        self.assertEqual(relpath, n.relativize(relpath))
        self.assertEqual(relpath, n.relativize(abspath))

    def test_normalize_path(self):
        relpath = os.path.join('foo', 'bar', 'baz')
        non_normalized = os.path.join('foo', 'bar', 'omit', '..', 'baz')

        n = FilePathNormalizer()
        self.assertEqual(relpath, n.relativize(non_normalized))

    def test_no_base_path_inference(self):
        base = os.path.abspath('base')
        relpath = os.path.join('foo', 'bar', 'baz')
        abspath = os.path.join(base, 'foo', 'bar', 'baz')

        n = FilePathNormalizer(no_base_path_inference=True)
        self.assertEqual(relpath, n.relativize(relpath))
        self.assertEqual(abspath, n.relativize(abspath))

        n = FilePathNormalizer(base_path=base, no_base_path_inference=True)
        self.assertEqual(relpath, n.relativize(relpath))
        self.assertEqual(relpath, n.relativize(abspath))

    def test_inference_git(self):
        with tempfile.TemporaryDirectory() as tempdirname:
            temppath = pathlib.PurePath(tempdirname)
            base = str(temppath.joinpath("gitrepo"))
            relpath = os.path.join('foo', 'bar', 'baz')
            abspath = os.path.join(base, 'foo', 'bar', 'baz')

            self._run_command(['git', 'init', base])

            n = FilePathNormalizer()
            self.assertEqual(relpath, n.relativize(abspath))

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

            base = str(temppath.joinpath("gitrepo"))
            relpath = os.path.join('submod', 'foo', 'bar', 'baz')
            abspath = os.path.join(base, 'submod', 'foo', 'bar', 'baz')

            n = FilePathNormalizer()
            self.assertEqual(relpath, n.relativize(abspath))

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
