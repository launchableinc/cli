import re

# find *Test, *Tests, *TestCase, *Spec + .java, .scala, .kt, .groovy
jvm_test_pattern = re.compile(r'^.*(?:Test(?:Case|s)?|Spec)\.(?:java|scala|kt|groovy)$')
