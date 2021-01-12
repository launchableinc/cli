from launchable.utils.gzipgen import compress
import gzip

def test_compress():
    """Basic sanity test of """
    encoded=b''.join(compress([b'Hello',b' ',b'world']))
    msg = gzip.decompress(encoded)
    print(msg)
    assert msg==b'Hello world'
