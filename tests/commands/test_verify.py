from nose.tools import eq_
from launchable.commands.verify import *

def test_compare_version():
    def sign(x):
        if x<0:
            return -1
        if x>0:
            return 1
        return 0

    def f(expected, a,b):
        """Ensure symmetry on two sides"""
        eq_(sign(compare_version(a,b)), expected)
        eq_(sign(compare_version(b,a)), -expected)

    f(0, [1, 1, 0], [1, 1])     # 1.1.0 = 1.1
    f(1, [1, 1], [1, 0])        # 1.1 > 1.0
    f(1, [1, 0, 1], [1])        # 1.0.1 > 1

def test_java_version():
    assert compare_java_version(
"""
java version "1.8.0_144"
Java(TM) SE Runtime Environment (build 1.8.0_144-b01)
Java HotSpot(TM) 64-Bit Server VM (build 25.144-b01, mixed mode)
"""
    ) >= 0

    assert compare_java_version(
"""
java version "1.5.0_22"
Java(TM) 2 Runtime Environment, Standard Edition (build 1.5.0_22-b03)
Java HotSpot(TM) 64-Bit Server VM (build 1.5.0_22-b03, mixed mode)
"""
    ) < 0
