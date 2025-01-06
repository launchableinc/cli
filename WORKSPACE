load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# https://github.com/bazelbuild/rules_jvm_external
http_archive(
    name = "rules_jvm_external",
    sha256 = "ec60d258e6f55a1014368e40ca52058b1a645a3d455ca471c4edb7c03f4b8d88",
    strip_prefix = "rules_jvm_external-6.6",
    url = "https://github.com/bazelbuild/rules_jvm_external/archive/6.6.zip",
)

load("@rules_jvm_external//:repositories.bzl", "rules_jvm_external_deps")
rules_jvm_external_deps()

load("@rules_jvm_external//:setup.bzl", "rules_jvm_external_setup")
rules_jvm_external_setup()

load("@rules_jvm_external//:defs.bzl", "maven_install")
load("@rules_jvm_external//:specs.bzl", "maven")

# "bazel run @unpinned_maven//:pin" to apply these changes
maven_install(
    artifacts = [
        "args4j:args4j:2.33",  # can't go higher so long as we stay on Java 8
        "com.fasterxml.jackson.core:jackson-annotations:2.18.2",
        "com.fasterxml.jackson.core:jackson-core:2.18.2",
        "com.fasterxml.jackson.core:jackson-databind:2.18.2",
        "com.google.guava:guava:33.3.1-jre",
        "org.apache.httpcomponents:httpclient:4.5.14",
        # This is the last release that produce Java 8 class files.
        "org.eclipse.jgit:org.eclipse.jgit:5.13.3.202401111512-r",
        "org.slf4j:slf4j-api:2.0.12",
        "org.slf4j:slf4j-jdk14:2.0.12",
        "org.jvnet:animal-sniffer:1.2",
        "junit:junit:4.13.2",
        maven.artifact(
            testonly = 1,
            artifact = "mockserver-junit-rule-no-dependencies",
            group = "org.mock-server",
            version = "5.15.0",
        ),
        maven.artifact(
            testonly = 1,
            artifact = "truth",
            group = "com.google.truth",
            version = "1.4.4",
        ),
    ],
    maven_install_json = "//src:maven_install.json",
    repositories = ["https://repo1.maven.org/maven2"],
    version_conflict_policy = "pinned",
    fetch_sources = True,
)

load("@maven//:defs.bzl", "pinned_maven_install")

pinned_maven_install()
