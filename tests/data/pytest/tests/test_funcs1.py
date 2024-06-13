import pytest  # type: ignore


@pytest.mark.foo
def test_func1():
    assert 1 == True  # noqa: E712


@pytest.mark.bar
def test_func2():
    assert 1 == False  # noqa: E712


# Borrowed from https://docs.pytest.org/en/stable/how-to/parametrize.html#parametrizemark.


@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_foo(x, y):
    assert x == 1
