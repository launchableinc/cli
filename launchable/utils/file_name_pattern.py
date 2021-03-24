import re

jvm_test_pattern = re.compile(r'^.*Test(?:Case|s)?\.(?:java|scala|kt)$')
