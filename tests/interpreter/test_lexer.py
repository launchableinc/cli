from unittest import TestCase
from launchable.interpreter.lexer import Lexer
from launchable.interpreter.token import TOKEN_KIND, Token

class LexerTest(TestCase):
    def test_tokenize(self):
        input = "50.5%"
        lexer = Lexer(input) 
        token = lexer.next()
        self.assertEqual(token.kind, TOKEN_KIND.LITERAL.PERCENTAGE)
        self.assertEqual(token.literal, '50.5%')
        self.assertEqual(lexer.has_next(), False)
    
    def test_tokenize2(self):
        input = """
subsetByDuration(
\t50.5%,\r\n
\tsortByMostImportant(allTests)
)
"""
        lexer = Lexer(input) 
        expects = [
            Token(TOKEN_KIND.FUNCTION.SUBSET_BY_DURATION, 'subsetByDuration'),
            Token(TOKEN_KIND.OTHER.LEFT_PARENTHESIS, '('),
            Token(TOKEN_KIND.LITERAL.PERCENTAGE, '50.5%'),
            Token(TOKEN_KIND.DELIMITER.COMMA, ','),
            Token(TOKEN_KIND.FUNCTION.SORT_BY_MOST_IMPORTANT, 'sortByMostImportant'),
            Token(TOKEN_KIND.OTHER.LEFT_PARENTHESIS, '('),
            Token(TOKEN_KIND.CONST.ALL_TESTS, 'allTests'),
            Token(TOKEN_KIND.OTHER.RIGHT_PARENTHESIS, ')'),
            Token(TOKEN_KIND.OTHER.RIGHT_PARENTHESIS, ')')
        ]
        for expect in expects:
            actual = lexer.next()
            self.assertEqual(expect.literal, actual.literal)
            self.assertEqual(expect.kind, actual.kind)
