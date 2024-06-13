import pytest  # type: ignore


@pytest.mark.foo
def test_func3():
    assert True == True  # noqa: E712


@pytest.mark.bar
def test_func4():
    assert False == False  # noqa: E712
