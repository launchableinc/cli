from typing import Union
from enum import Enum, auto

class TOKEN_KIND:
    class FUNCTION(Enum):        
        SUBSET_BY_DURATION = auto()
        SUBSET_BY_CONFIDENCE = auto()
        SORT_BY_MOST_IMPORTANT = auto()
        IGNORE_FLAKY_TESTS_ABOVE = auto()
        SELECT_MAPPED_TESTS = auto()
        CONCAT = auto()
    
    class LITERAL(Enum):
        FLOAT = auto()
        PERCENTAGE = auto()

    class CONST(Enum):
        ALL_TESTS = auto()

    class DELIMITER(Enum):
        COMMA = auto()

    class OTHER(Enum):
        LEFT_PARENTHESIS = auto()
        RIGHT_PARENTHESIS = auto()
        INVALID = auto()


class Token:
    def __init__(self, kind: Union[TOKEN_KIND.FUNCTION, TOKEN_KIND.LITERAL, TOKEN_KIND.CONST, TOKEN_KIND.OTHER, TOKEN_KIND.DELIMITER], literal: str) -> None:
        self.kind = kind
        self.literal = literal

