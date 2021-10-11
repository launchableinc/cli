import re

# find *Test, *Tests, *TestCase + .java, .scala, .kt
jvm_test_pattern = re.compile(r'^.*Test(?:Case|s)?\.(?:java|scala|kt)$')
