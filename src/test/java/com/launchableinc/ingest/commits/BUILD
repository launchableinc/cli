java_test(
    name = "CommitGraphCollectorTest",
    srcs = ["CommitGraphCollectorTest.java"],
    deps = [
        "//src/main/java/com/launchableinc/ingest/commits",
        "@maven//:com_google_truth_truth",
        "@maven//:junit_junit",
        "@maven//:org_eclipse_jgit_org_eclipse_jgit",
    ],
)

java_test(
    name = "CommitIngesterTest",
    srcs = ["CommitIngesterTest.java"],
    deps = [
        "//src/main/java/com/launchableinc/ingest/commits",
        "@maven//:junit_junit",
        "@maven//:org_eclipse_jgit_org_eclipse_jgit",
        "@maven//:org_mock_server_mockserver_junit_rule_no_dependencies",
    ],
)
