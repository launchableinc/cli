from typing import Optional
from launchable.interpreter.token import TOKEN_KIND, Token

RESERVED_WORDS = {
    'subsetByDuration': TOKEN_KIND.FUNCTION.SUBSET_BY_DURATION,
    'subsetByConfidence': TOKEN_KIND.FUNCTION.SUBSET_BY_CONFIDENCE,
    'sortByMostImportant': TOKEN_KIND.FUNCTION.SORT_BY_MOST_IMPORTANT,
    'ignoreFlakyTestsAbove': TOKEN_KIND.FUNCTION.IGNORE_FLAKY_TESTS_ABOVE,
    'selectMappedTests': TOKEN_KIND.FUNCTION.SELECT_MAPPED_TESTS,
    'contact': TOKEN_KIND.FUNCTION.CONCAT,
    'allTests': TOKEN_KIND.CONST.ALL_TESTS
}

WHITE_SPACE_CHARS = [' ', '\t', '\r', '\n']

class Lexer:
    def __init__(self, string: str) -> None:
        self.string = string
        self.current_cursor = 0

    def has_next(self) -> bool:
        return self.current_cursor != len(self.string) - 1

    def next(self) -> Token:
        target_char = self.string[self.current_cursor]
        while target_char in WHITE_SPACE_CHARS:
            target_char = self._read_next_char()

        if target_char is None:
            return Token(kind=TOKEN_KIND.OTHER.INVALID, literal='')
        token = Token(kind=TOKEN_KIND.OTHER.INVALID, literal=target_char)
        if self._isInteger(target_char):
            literal = target_char
            next_char = self._read_next_char()
            while next_char == '.' or self._isInteger(next_char):
                literal += self.string[self.current_cursor]
                next_char = self._read_next_char()
            if next_char == '%':
                literal += next_char
                self._read_next_char()
                token = Token(kind=TOKEN_KIND.LITERAL.PERCENTAGE, literal=literal)
            else:
                token = Token(kind=TOKEN_KIND.LITERAL.FLOAT, literal=literal)
            return token
        elif target_char == '(':
            token = Token(kind=TOKEN_KIND.OTHER.LEFT_PARENTHESIS, literal=target_char)
        elif target_char == ')':
            token = Token(kind=TOKEN_KIND.OTHER.RIGHT_PARENTHESIS, literal=target_char)
        elif target_char == ',':
            token = Token(kind=TOKEN_KIND.DELIMITER.COMMA, literal=target_char)
        else:
            if self._isAlphabet(target_char):
                literal = target_char
                next_char = self._read_next_char()
                while self._isAlphabet(next_char):
                    literal += self.string[self.current_cursor]
                    next_char = self._read_next_char()
                kind = RESERVED_WORDS.get(literal)
                if kind:
                    token = Token(kind=kind, literal=literal)
                return token
        self._read_next_char()
        return token
    
    def _read_next_char(self):
        if not self.has_next():
            return None
        self.current_cursor += 1
        return self.string[self.current_cursor]
    
    def _peek_next_char(self):
        if not self.has_next():
            return None
        return self.string[self.current_cursor]
    
    def _isInteger(self, char: Optional[str]):
        return char and '0' <= char and char <= '9'
    
    def _isAlphabet(self, char: Optional[str]):
        return char and ('a' <= char and char <= 'z' or 'A' <= char and char <= 'Z')
