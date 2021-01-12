# MIT License, from https://github.com/leetreveil/gengzip
import time
import zlib
import struct
from builtins import int


def write32u(value):
    return struct.pack('<L', value)


def write_gzip_header():
    header = b''
    header += b'\037\213'  # magic header (0x1f, 0x8b)
    header += b'\010'  # compression method (deflate)
    header += b'\000'  # flags (not set)
    header += write32u(int(time.time()))  # file modification time
    header += b'\002'  # extra flags (maximum compression)
    header += b'\377'  # os type (unknown)
    return header


def write_gzip_footer(crc, size):
    footer = b''
    footer += write32u(crc)
    footer += write32u(size & 0xffffffff)
    return footer


def compress(d, compresslevel=6):
    """
    Takes a generator 'd' that provides streaem of data, then returns a wrapper generator
    that yields compressed gzip data stream
    """
    crc = zlib.crc32(b'') & 0xffffffff
    size = 0
    yield write_gzip_header()
    compress = zlib.compressobj(
        compresslevel, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
    for data in d:
        crc = zlib.crc32(data, crc) & 0xffffffff
        size += len(data)
        compressed = compress.compress(data)
        if len(compressed) > 0:
            yield compressed
    yield compress.flush() + write_gzip_footer(crc, size)
