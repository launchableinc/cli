from launchable.utils.gzipgen import compress
from nose.tools import eq_
import gzip

def test_compress():
    """Basic sanity test of """
    encoded=b''.join(compress([b'Hello',b' ',b'world']))
    msg = gzip.decompress(encoded)
    print(msg)
    eq_(msg,b'Hello world')
