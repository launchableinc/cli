load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# https://github.com/bazelbuild/rules_jvm_external
http_archive(
    name = "rules_jvm_external",
    sha256 = "cd1a77b7b02e8e008439ca76fd34f5b07aecb8c752961f9640dea15e9e5ba1ca",
    strip_prefix = "rules_jvm_external-4.2",
    url = "https://github.com/bazelbuild/rules_jvm_external/archive/4.2.zip",
)

load("@rules_jvm_external//:defs.bzl", "maven_install")
load("@rules_jvm_external//:specs.bzl", "maven")

maven_install(
    artifacts = [
        "args4j:args4j:2.33",
        "ch.qos.logback:logback-classic:1.2.11",
        "com.fasterxml.jackson.core:jackson-annotations:2.13.3",
        "com.fasterxml.jackson.core:jackson-core:2.13.3",
        "com.fasterxml.jackson.core:jackson-databind:2.13.3",
        "com.google.guava:guava:31.1-jre",
        "org.apache.httpcomponents:httpclient:4.5.13",
        # This is the last release that produce Java 8 class files.
        "org.eclipse.jgit:org.eclipse.jgit:5.13.1.202206130422-r",
        "org.slf4j:slf4j-api:1.7.36",
        maven.artifact(
            testonly = 1,
            artifact = "mockserver-junit-rule-no-dependencies",
            group = "org.mock-server",
            version = "5.13.2",
        ),
        maven.artifact(
            testonly = 1,
            artifact = "junit",
            group = "junit",
            version = "4.13.2",
        ),
        maven.artifact(
            testonly = 1,
            artifact = "truth",
            group = "com.google.truth",
            version = "1.1.3",
        ),
    ],
    maven_install_json = "//src:maven_install.json",
    repositories = ["https://repo1.maven.org/maven2"],
    version_conflict_policy = "pinned",
)

load("@maven//:defs.bzl", "pinned_maven_install")

pinned_maven_install()
