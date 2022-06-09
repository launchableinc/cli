# Supported test frameworks

The Launchable CLI includes built-in integrations for test runners and build tools that execute tests built using various frameworks, including:

* [Appium](appium.md)
* [Cucumber](../integrations/cucumber.md)
* [JUnit](junit.md)
* [GoogleTest](../integrations/googletest.md)
* [Jest](../integrations/jest.md)
* [minitest](../integrations/minitest.md)
* [nose](../integrations/nose.md)
* [NUnit](../integrations/nunit.md)
* [Robot](../integrations/robot.md)
* [RSpec](../integrations/rspec.md)
* [Selenium](selenium.md)
* [TestNG](testng.md)

Note that the primary integration point for Launchable is your team's build tool or test runner (i.e. whatever CLI you invoke to actually kick off your tests), not the test framework itself. However, some frameworks have their own test runners. You can see the full list at [Integrations](../integrations/).