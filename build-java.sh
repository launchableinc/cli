#!/bin/bash -ex
bazelisk build //src/main/java/com/launchableinc/ingest/commits:exe_deploy.jar
bazelisk test //...
cp bazel-bin/src/main/java/com/launchableinc/ingest/commits/exe_deploy.jar smart_tests/jar/exe_deploy.jar
