BAZEL_SRC=third_party/github.com/bazelbuild/bazel
GOOGLE_API_SRC=third_party/github.com/googleapis/googleapis

# Prerequisite: install protoc (e.g. `brew install protobuf`)
protoc:
	protoc -I=$(BAZEL_SRC) --python_out=$(BAZEL_SRC) \
	$(BAZEL_SRC)/src/main/java/com/google/devtools/build/lib/buildeventstream/proto/build_event_stream.proto \
	$(BAZEL_SRC)/src/main/protobuf/*.proto
	python3 -m grpc.tools.protoc -I=$(GOOGLE_API_SRC) --python_out=$(GOOGLE_API_SRC) --grpc_python_out=$(GOOGLE_API_SRC) \
	$(GOOGLE_API_SRC)/google/devtools/build/v1/*.proto \
	$(GOOGLE_API_SRC)/google/api/*.proto
	
