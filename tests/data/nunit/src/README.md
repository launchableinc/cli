# Dev environment
* [Install .NET SDK](https://dotnet.microsoft.com/download) on your platform of choice.
  Specifically, .NET Core 3.1
* Install NUnit console runner from [the zip page](https://github.com/nunit/nunit-console/releases/tag/v3.12)
  or other formats of your choice
* `dotnet build` will produce `bin/Debug/netcoreapp3.1/calc.dll` that contains all the code
* `dotnet $NUNIT/bin/netcoreapp3.1/nunit3-console.dll` to run NUnit3 console runner.
  More specifically, `dotnet $NUNIT/bin/netcoreapp3.1/nunit3-console.dll ./bin/Debug/netcoreapp3.1/calc.dll` will run tests
  and produce `TestResult.xml` that we capture as `../output.xml`.
* `--explore=list.xml` to produec the test list.
* Internal: See https://launchableinc.atlassian.net/l/c/RUoketE0 for more detailed notes.
