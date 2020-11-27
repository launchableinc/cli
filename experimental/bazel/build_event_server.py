from concurrent import futures
import logging
import sys
import os

import grpc

from google.protobuf import empty_pb2

# Hacky quick way to get this code importable.
# We might want to change the codegen location and package names to make it more idiomatic.
sys.path.append(os.path.dirname(__file__) + '/../../third_party/github.com/bazelbuild/bazel')
sys.path.append(os.path.dirname(__file__) + '/../../third_party/github.com/googleapis/googleapis')
import google.devtools.build.v1.publish_build_event_pb2 as publish_build_event_pb2
import google.devtools.build.v1.publish_build_event_pb2_grpc as publish_build_event_pb2_grpc
import src.main.java.com.google.devtools.build.lib.buildeventstream.proto.build_event_stream_pb2 as build_event_stream_pb2

class HandleEvent(publish_build_event_pb2_grpc.PublishBuildEventServicer):
    def HandleBazelEvent(self, bazel_event):
        # Bazel event is a serialized proto
        if (bazel_event.type_url != "type.googleapis.com/build_event_stream.BuildEvent"):
            raise Exception("Don't know how to handle bazel_event of type " + bazel_event.type_url)
        build_event = build_event_stream_pb2.BuildEvent()
        build_event.ParseFromString(bazel_event.value) 
        if (build_event.WhichOneof("payload") == "test_result"):
            print("Test Result", build_event.test_result)
        

    def PublishLifecycleEvent(self, request, context):
        # Currently don't care about BuildStarted events
        return empty_pb2.Empty()

    def PublishBuildToolEventStream(self, request_iterator, context):
        for request in request_iterator:
            event_kind = request.ordered_build_event.event.WhichOneof("event")
            if (event_kind == "bazel_event"):
                self.HandleBazelEvent(request.ordered_build_event.event.bazel_event)
            else:
                print("[ Ignoring event kind", event_kind, "]")
            # Just ACK every message
            yield publish_build_event_pb2.PublishBuildToolEventStreamResponse(
                stream_id = request.ordered_build_event.stream_id,
                sequence_number = request.ordered_build_event.sequence_number,
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    publish_build_event_pb2_grpc.add_PublishBuildEventServicer_to_server(HandleEvent(), server)
    server.add_insecure_port('[::]:50002')
    server.start()
    print("SERVER listening for build events grpc connection on localhost:50002")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
