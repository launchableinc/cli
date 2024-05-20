from .cli_test_case import CliTestCase


class TestCliTestCase(CliTestCase):
    def test_assert_json_orderless_equal(self):
        # simple case
        self.assert_json_orderless_equal({"a": 1, "b": 2}, {"b": 2, "a": 1})

        # has array field
        self.assert_json_orderless_equal(
            {"array": [1, 2, 3], "b": 2}, {"b": 2, "array": [1, 2, 3]}
        )

        # has dict field
        self.assert_json_orderless_equal(
            {"dict": {"a": 1, "b": 2, "c": 3}, "b": 2},
            {"b": 2, "dict": {"b": 2, "c": 3, "a": 1}},
        )
        # compare with array that some object have have fields that None
        self.assert_json_orderless_equal(
            {
                "array": [
                    {"name": "a", "data": {"value": 1}},
                    {"data": None, "name": "b"},
                    {"name": "c", "data": {"value": 2}},
                ],
                "b": 2,
            },
            {
                "b": 2,
                "array": [
                    {"data": None, "name": "b"},
                    {"data": {"value": 2}, "name": "c"},
                    {"data": {"value": 1}, "name": "a"},
                ],
            },
        )

    def test_extract_all_test_paths_do_not_throw_exception_when_correct_input(self):
        self.assert_test_path_orderly_equal(
            {
                "events": [
                    {
                        "type": "case",
                        "testPath": [
                            {"type": "class", "name": "com.launchable.HelloWorldTest"},
                            {"type": "testcase", "name": "test1"},
                        ],
                    }
                ],
            },
            {
                "events": [
                    {
                        "type": "case",
                        "testPath": [
                            {"type": "class", "name": "com.launchable.HelloWorldTest"},
                            {"type": "testcase", "name": "test1"},
                        ],
                    }
                ]
            },
        )

        self.assert_test_path_orderly_equal(
            {
                "events": [
                    {
                        "type": "case",
                        "testPath": [
                            {"type": "class", "name": "com.launchable.HelloWorldTest"},
                            {"type": "testcase", "name": "test1"},
                        ],
                    },
                    {
                        "type": "case",
                        "testPath": [
                            {"type": "class", "name": "com.launchable.HelloWorldTest"},
                            {"type": "testcase", "name": "test2"},
                        ],
                    },
                ],
            },
            {
                "events": [
                    {
                        "type": "case",
                        "testPath": [
                            {"type": "class", "name": "com.launchable.HelloWorldTest"},
                            {"type": "testcase", "name": "test1"},
                        ],
                    },
                    {
                        "type": "case",
                        "testPath": [
                            {"type": "class", "name": "com.launchable.HelloWorldTest"},
                            {"type": "testcase", "name": "test2"},
                        ],
                    },
                ]
            },
        )

    def test_extract_all_test_paths_throw_exception_when_element_size_does_not_match(
        self,
    ):
        with self.assertRaises(AssertionError):
            self.assert_test_path_orderly_equal(
                {
                    "events": [
                        {
                            "type": "case",
                            "testPath": [
                                {
                                    "type": "class",
                                    "name": "com.launchable.HelloWorldTest",
                                },
                                {"type": "testcase", "name": "test1"},
                            ],
                        },
                        {
                            "type": "case",
                            "testPath": [
                                {
                                    "type": "class",
                                    "name": "com.launchable.HelloWorldTest",
                                },
                                {"type": "testcase", "name": "test2"},
                            ],
                        },
                    ],
                },
                {
                    "events": [
                        {
                            "type": "case",
                            "testPath": [
                                {
                                    "type": "class",
                                    "name": "com.launchable.HelloWorldTest",
                                },
                                {"type": "testcase", "name": "test1"},
                            ],
                        }
                    ]
                },
            )

        with self.assertRaises(AssertionError):
            self.assert_test_path_orderly_equal(
                {
                    "events": [
                        {
                            "type": "case",
                            "testPath": [
                                {
                                    "type": "class",
                                    "name": "com.launchable.HelloWorldTest",
                                },
                                {"type": "testcase", "name": "test1"},
                            ],
                        }
                    ],
                },
                {
                    "events": [
                        {
                            "type": "case",
                            "testPath": [
                                {
                                    "type": "class",
                                    "name": "com.launchable.HelloWorldTest",
                                },
                                {"type": "testcase", "name": "test1"},
                            ],
                        },
                        {
                            "type": "case",
                            "testPath": [
                                {
                                    "type": "class",
                                    "name": "com.launchable.HelloWorldTest",
                                },
                                {"type": "testcase", "name": "test2"},
                            ],
                        },
                    ]
                },
            )

    def test_extract_all_test_paths_throw_exception_when_the_events_order_does_not_match(
        self,
    ):
        self.assert_test_path_orderly_equal(
            {
                "events": [
                    {
                        "type": "case",
                        "testPath": [
                            {
                                "type": "class",
                                "name": "com.launchable.HelloWorldTest",
                            },
                            {"type": "testcase", "name": "test2"},
                        ],
                    },
                    {
                        "type": "case",
                        "testPath": [
                            {
                                "type": "class",
                                "name": "com.launchable.HelloWorldTest",
                            },
                            {"type": "testcase", "name": "test1"},
                        ],
                    },
                ],
            },
            {
                "events": [
                    {
                        "type": "case",
                        "testPath": [
                            {
                                "type": "class",
                                "name": "com.launchable.HelloWorldTest",
                            },
                            {"type": "testcase", "name": "test1"},
                        ],
                    },
                    {
                        "type": "case",
                        "testPath": [
                            {
                                "type": "class",
                                "name": "com.launchable.HelloWorldTest",
                            },
                            {"type": "testcase", "name": "test2"},
                        ],
                    },
                ]
            },
        )
