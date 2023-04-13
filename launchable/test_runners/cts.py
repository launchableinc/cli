from xml.etree import ElementTree as ET

import click

from launchable.commands.record.case_event import CaseEvent

from . import launchable

# https://source.android.com/docs/compatibility/cts/command-console-v2
include_option = "--include-filter"
exclude_option = "--exclude-filter"


def parse_func(p: str):
    """  # noqa: E501
    # sample report format
    success case:
    <Module name="CtsAbiOverrideHostTestCases" abi="arm64-v8a" runtime="1171" done="true" pass="1" total_tests="1">
      <TestCase name="android.abioverride.cts.AbiOverrideTest">
        <Test result="pass" name="testAbiIs32bit" />
      </TestCase>
    </Module>

    failure case:
    <Module name="CtsAccountManagerTestCases" abi="arm64-v8a" runtime="13414" done="false" pass="2" total_tests="151">
      <Reason message="Instrumentation run failed due to 'Process crashed.'" error_name="INSTRUMENTATION_CRASH" error_code="520200" />
      <TestCase name="android.accounts.cts.AbstractAuthenticatorTests">
        <Test result="fail" name="testFinishSessionAndStartAddAccountSessionDefaultImpl">
          <Failure message="android.accounts.OperationCanceledException&#13;">
            <StackTrace>android.accounts.OperationCanceledException
          at android.accounts.AccountManager$AmsTask.internalGetResult(AccountManager.java:2393)
          at android.accounts.AccountManager$AmsTask.getResult(AccountManager.java:2422)
          at android.accounts.AccountManager$AmsTask.getResult(AccountManager.java:2337)
          at android.accounts.cts.AbstractAuthenticatorTests.testFinishSessionAndStartAddAccountSessionDefaultImpl(AbstractAuthenticatorTests.java:165)
            </StackTrace>
          </Failure>
        </Test>
      </TestCase>
    </Module>
    """
    class TestResult:
        def __init__(self, test_case_name: str, test_name: str, result: str, stdout: str, stderr: str):
            self.test_case_name = test_case_name
            self.test_name = test_name
            self.result = result
            self.stdout = stdout
            self.stderr = stderr

        def case_event_status(self):
            if self.result == "fail":
                return CaseEvent.TEST_FAILED
            elif self.result == "ASSUMPTION_FAILURE" or self.result == "IGNORED":
                return CaseEvent.TEST_SKIPPED

            return CaseEvent.TEST_PASSED

    def build_record_test_path(module: str, test_case: str, test: str):
        return [
            {"type": "Module", "name": module},
            {"type": "TestCase", "name": test_case},
            {"type": "Test", "name": test},
        ]

    events = []
    tree = ET.parse(p)

    for module in tree.iter('Module'):
        test_results = []
        total_duration = module.get("runtime", "0")
        module_name = module.get("name", "")

        for test_case in module.iter("TestCase"):
            test_case_name = test_case.get('name', "")

            for test in test_case.iter("Test"):
                result = test.get('result', "")
                test_name = test.get("name", "")
                stdout = ""
                stderr = ""

                failure = test.find('Failure')
                if failure:
                    stack_trace = ""
                    stack_trace_element = failure.find("StackTrace")
                    if stack_trace_element is not None:
                        stack_trace = str(stack_trace_element.text)

                    stdout = failure.get("message", "")
                    stderr = stack_trace

                test_results.append(TestResult(
                    test_case_name=test_case_name,
                    test_name=test_name,
                    result=result,
                    stdout=stdout,
                    stderr=stderr))

        if len(test_results) == 0:
            continue

        test_duration_msec_per_test = int(total_duration) / len(test_results)

        for test_result in test_results:  # type: TestResult
            if module_name == "" or test_result.test_case_name == "" or test_result.test_name == "":
                continue

            events.append(CaseEvent.create(
                test_path=build_record_test_path(module_name, test_result.test_case_name, test_result.test_name),
                duration_secs=float(test_duration_msec_per_test / 1000),
                status=test_result.case_event_status(),
                stdout=test_result.stdout,
                stderr=test_result.stderr,
            ))

    return (x for x in events)


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    """
    Beta: Report test result that Compatibility Test Suite (CTS) produced. Supports only CTS v2
    """
    for r in reports:
        client.report(r)

    client.parse_func = parse_func
    client.run()


@launchable.subset
def subset(client):
    """
    Beta: Produces test list from previous test sessions for Compatibility Test Suite (CTS). Supports only CTS v2
    """
    start_module = False

    """ # noqa: E501
    # This is sample output of `cts-tradefed list modules`
    ==================
    Notice:
    We collect anonymous usage statistics in accordance with our Content Licenses (https://source.android.com/setup/start/licenses), Contributor License Agreement (https://opensource.google.com/docs/cla/), Privacy Policy (https://policies.google.com/privacy) and Terms of Service (https://policies.google.com/terms).
    ==================
    Android Compatibility Test Suite 12.1_r5 (9566553)
    Use "help" or "help all" to get more information on running commands.
    Non-interactive mode: Running initial command then exiting.
    Using commandline arguments as starting command: [list, modules]
    arm64-v8a CtsAbiOverrideHostTestCases[instant]
    arm64-v8a CtsAbiOverrideHostTestCases[secondary_user]
    arm64-v8a CtsAbiOverrideHostTestCases
    armeabi-v7a CtsAbiOverrideHostTestCases
    """

    for t in client.stdin():
        if "starting command" in t:
            start_module = True
            continue

        if not start_module:
            continue

        # e.g) armeabi-v7a CtsAbiOverrideHostTestCases
        device_and_module = t.rstrip("\n").split()
        if len(device_and_module) != 2:
            click.echo(
                click.style(
                    "Warning: {line} is not expected Module format and skipped".format(
                        line=t),
                    fg="yellow"),
                err=True)
            continue

        client.test_path([{"type": "Module", "name": device_and_module[1]}])

    option = include_option
    if client.is_output_exclusion_rules:
        option = exclude_option

    client.formatter = lambda x: "{option} \"{module}\"".format(option=option, module=x[0]['name'])
    client.run()
