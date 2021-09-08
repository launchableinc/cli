from launchable.utils.gzipgen import compress
import gzip
from unittest import TestCase


class GzippenTest(TestCase):
    def test_compress(self):
        """Basic sanity test of """
        encoded = b''.join(compress([b'Hello', b' ', b'world']))
        msg = gzip.decompress(encoded)
        print(msg)
        self.assertEqual(msg, b'Hello world')
