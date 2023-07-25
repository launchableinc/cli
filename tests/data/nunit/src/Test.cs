using System.Collections;
using NUnit.Framework;

namespace calc
{
    public class Tests1
    {
        [Test]
        public void Test1()
        {
            Assert.Pass();
        }

        [Test]
        public void Test2()
        {
            Assert.Fail();
        }
    }
}

namespace calc.sub
{
    public class Tests2
    {
        [Test]
        [Category("sub")]
        public void Foo() {}
    }
}


namespace ParameterizedTests
{
    [TestFixture]
    public class MyTests
    {
        [TestCaseSource(typeof(MyDataClass), nameof(MyDataClass.TestCases))]
        public int DivideTest(int n, int d)
        {
            return n / d;
        }
    }

    public class MyDataClass
    {
        public static IEnumerable TestCases
        {
            get
            {
                yield return new TestCaseData(12, 3).Returns(4);
                yield return new TestCaseData(12, 2).Returns(6);
                yield return new TestCaseData(12, 4).Returns(3);
            }
        }
    }
}


public class BaseClass
{
  public virtual int Add(int a, int b)
  {
    return a + b;
  }
}

public class SubAClass : BaseClass
{
  public override int Add(int a, int b)
  {
    return base.Add(a, b) + 1;
  }
}

public class SubBClass : BaseClass
{
  public override int Add(int a, int b)
  {
    return base.Add(a, b) + 2;
  }
}


namespace subclass.test
{
    [TestFixture]
    public class BaseClassTest {
        public class SubAClassTest : BaseClassTest {
            [TestCase(2, 2, 5)] // Because the SubAClass adds an extra 1.
            [TestCase(4, 2, 7)]
            public void AddTestA(int a, int b, int expected) {
                Assert.AreEqual(expected, new SubAClass().Add(a, b));
            }
        }

        public class SubBClassTest : BaseClassTest {
            [TestCase(2, 3, 7)] // Because the SubAClass adds an extra 1.
            [TestCase(4, 7, 13)]
            public void AddTestB(int a, int b, int expected) {
                Assert.AreEqual(expected, new SubBClass().Add(a, b));
            }
        }
    }
}
