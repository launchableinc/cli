from unittest import TestCase
from launchable.interpreter.lexer import Lexer

from launchable.interpreter.parser import Parser

class ParserTest(TestCase):
    def test_parse(self):
        input = 'subsetByDuration(50%,  sortByMostImportant(allTests))'
        lexer = Lexer(input) 
        parser = Parser(lexer)
        expression = parser.parse()
        self.assertEqual(expression.token.literal, 'subsetByDuration')
        self.assertEqual(expression.goal.token.literal, '50%')
        self.assertEqual(expression.list.token.literal, 'sortByMostImportant')
        self.assertEqual(expression.list.list.token.literal, 'allTests')

    def test_parse2(self):
        input = 'subsetByDuration(50%, ignoreFlakyTestsAbove(0.5, sortByMostImportant(allTests)))'
        lexer = Lexer(input) 
        parser = Parser(lexer)
        expression = parser.parse()
        self.assertEqual(expression.token.literal, 'subsetByDuration')
        self.assertEqual(expression.goal.token.literal, '50%')
        self.assertEqual(expression.list.token.literal, 'ignoreFlakyTestsAbove')
        self.assertEqual(expression.list.goal.token.literal, '0.5')
        self.assertEqual(expression.list.list.token.literal, 'sortByMostImportant')
        self.assertEqual(expression.list.list.list.token.literal, 'allTests')
