import sys
import os

# Hacky quick way to get this code importable.
# We might want to change the codegen location and package names to make it more idiomatic.
sys.path.append(os.path.dirname(__file__) + '/../../third_party/github.com/bazelbuild/bazel')
from src.main.java.com.google.devtools.build.lib.buildeventstream.proto.build_event_stream_pb2 import BuildEvent

# Python has no readDelimitedFrom to use "recordio" files (length-delimited proto)
# so do a hack for now to see something working
# https://www.datadoghq.com/blog/engineering/protobuf-parsing-in-python/
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
with open(sys.argv[1], "rb") as f:
    buf = f.read()
    n = 0
    while n < len(buf):
        msg_len, new_pos = _DecodeVarint32(buf, n)
        n = new_pos
        msg_buf = buf[n:n+msg_len]
        n += msg_len
        event = BuildEvent()
        event.ParseFromString(msg_buf)
        if (event.WhichOneof("payload") == "test_result"):
            print("Test Result", event.test_result)
