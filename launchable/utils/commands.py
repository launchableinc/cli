from enum import Enum


class Command(Enum):
    VERIFY = 'VERIFY'
    RECORD_TESTS = 'RECORD_TESTS'
    RECORD_BUILD = 'RECORD_BUILD'
    RECORD_SESSION = 'RECORD_SESSION'
    SUBSET = 'SUBSET'
    COMMIT = 'COMMIT'

    def human_readable(self):
        # Convert the enum value to lowercase and replace underscores with spaces
        return self.value.lower().replace('_', ' ')
