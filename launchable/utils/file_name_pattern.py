import re

 # find *Test, *Tests, *TestCase + .java, .scala, .kt
jvm_test_pattern = re.compile(r'^.*Test(?:Case|s)?\.(?:java|scala|kt)$')

# find *_test.py, test_*.py without __init__.py and conftest.py
pytest_test_pattern = re.compile(r'.*_test\.py|test_.*\.py')
