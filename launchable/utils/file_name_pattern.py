import re

# find *Test, *Tests, *TestCase, *Spec, *Suite + .java, .scala, .kt, .groovy
jvm_test_pattern = re.compile(r'^.*(?:Test(?:Case|s)?|Spec|Suite)\.(?:java|scala|kt|groovy)$')
