from unittest import TestCase

from launchable.utils.glob import compile


class GlobTest(TestCase):
    def check(self, glob: str, matches, not_matches):
        p = compile(glob)
        for m in matches:
            self.assertTrue(p.fullmatch(m), "%s is expected to match %s" % (glob, m))
        for m in not_matches:
            self.assertFalse(p.fullmatch(m), "%s is expected not to match %s" % (glob, m))

    def test_everything(self):
        self.check(
            glob='*.txt',
            matches=[
                "foo.txt",
                "bar.txt",
                "f.txt",
                ".txt"
            ],
            not_matches=[
                "dir/foo.txt",
                "foo.exe",
                "f_txt"
            ]
        )
        self.check(
            glob='???.txt',
            matches=[
                "foo.txt",
                "bar.txt",
            ],
            not_matches=[
                "dir/foo.txt",
                "f.txt",
                "food.txt",
                "foo.exe"
            ]
        )
        self.check(
            glob='**/*.txt',
            matches=[
                "foo.txt",
                "a/foo.txt",
                "a/b/foo.txt",
                "a\\b\\foo.txt"
            ],
            not_matches=[
                "b.exe",
                "footxt",
                "a/footxt"
            ]
        )
        self.check(
            glob='**/*$*.class',
            matches=[
                "f$f.class",
                "foo/bar$zot.class"
            ],
            not_matches=[
                "foo.class",
                "foo/bar.class"
            ]
        )
