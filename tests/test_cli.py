import pytest

def dummy(x):
    return (x + 17) * 2

def test_dummy():
    assert dummy(4) == 42
