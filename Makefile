BAZEL_SRC=third_party/github.com/bazelbuild/bazel

# Prerequisite: install protoc (e.g. `brew install protobuf`)
protoc:
	protoc -I=$(BAZEL_SRC) --python_out=$(BAZEL_SRC) \
	$(BAZEL_SRC)/src/main/java/com/google/devtools/build/lib/buildeventstream/proto/build_event_stream.proto \
	$(BAZEL_SRC)/src/main/protobuf/*.proto
