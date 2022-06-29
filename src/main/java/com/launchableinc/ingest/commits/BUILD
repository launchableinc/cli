java_library(
    name = "commits",
    srcs = glob(["*.java"]),
    visibility = ["//visibility:public"],
    deps = [
        "@maven//:args4j_args4j",
        "@maven//:ch_qos_logback_logback_classic",
        "@maven//:com_fasterxml_jackson_core_jackson_annotations",
        "@maven//:com_fasterxml_jackson_core_jackson_core",
        "@maven//:com_fasterxml_jackson_core_jackson_databind",
        "@maven//:com_google_guava_guava",
        "@maven//:org_apache_httpcomponents_httpclient",
        "@maven//:org_apache_httpcomponents_httpcore",
        "@maven//:org_eclipse_jgit_org_eclipse_jgit",
        "@maven//:org_slf4j_slf4j_api",
    ],
)

java_binary(
    name = "exe",
    main_class = "com.launchableinc.ingest.commits.CommitIngester",
    runtime_deps = [":commits"],
)
