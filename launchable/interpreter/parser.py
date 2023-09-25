from typing import List
from launchable.interpreter.lexer import Lexer
from launchable.interpreter.token import TOKEN_KIND, Token

class Statement:
    def __init__(self, token: Token) -> None:
        self.token = token

class PercentageLiteral:
    def __init__(self, value: float) -> None:
        self.value = value

class FloatLiteral:
    def __init__(self, token: Token, value: float) -> None:
        self.token = token
        self.value = value

class Expression:
    def __init__(self, token: Token) -> None:
        self.token = token

class SubsetByDuraitonExpression(Expression):
    def __init__(self, token: Token, goal: PercentageLiteral, list: Expression) -> None:
        self.token = token
        self.goal = goal
        self.list = list

class IgnoreFlakyTestsAbove(Expression):
    def __init__(self, token: Token, goal: FloatLiteral, list: Expression) -> None:
        self.token = token
        self.goal = goal
        self.list = list

class AllTestsExpression(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token

class SortByMostImportantExpression(Expression):
    def __init__(self, token: Token, list: Expression) -> None:
        self.token = token
        self.list = list

class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer


    def parse(self) -> Expression:
        expression = None
        while self.lexer.has_next():
            target_token = self.lexer.next()
            if target_token.kind == TOKEN_KIND.FUNCTION.SUBSET_BY_DURATION:
                if self.lexer.next().kind != TOKEN_KIND.OTHER.LEFT_PARENTHESIS:
                    raise
                percentage_token = self.lexer.next()
                if percentage_token.kind != TOKEN_KIND.LITERAL.PERCENTAGE:
                    raise
                if self.lexer.next().kind != TOKEN_KIND.DELIMITER.COMMA:
                    raise
                list = self.parse()
                percentage = float(percentage_token.literal.strip('%')) / 100.0
                expression = SubsetByDuraitonExpression(token=target_token, goal=PercentageLiteral(percentage), list=list)
                if self.lexer.next().kind != TOKEN_KIND.OTHER.RIGHT_PARENTHESIS:
                    raise
            elif target_token.kind == TOKEN_KIND.FUNCTION.SORT_BY_MOST_IMPORTANT:
                if self.lexer.next().kind != TOKEN_KIND.OTHER.LEFT_PARENTHESIS:
                    raise
                list = self.parse()
                expression = SortByMostImportantExpression(token=target_token, list=list)
                if self.lexer.next().kind != TOKEN_KIND.OTHER.RIGHT_PARENTHESIS:
                    raise
            elif target_token.kind == TOKEN_KIND.FUNCTION.IGNORE_FLAKY_TESTS_ABOVE:
                if self.lexer.next().kind != TOKEN_KIND.OTHER.LEFT_PARENTHESIS:
                    raise
                float_token = self.lexer.next()
                if float_token.kind != TOKEN_KIND.LITERAL.FLOAT:
                    raise
                goal = FloatLiteral(token=float_token, value=float(float_token.literal))
                if self.lexer.next().kind != TOKEN_KIND.DELIMITER.COMMA:
                    raise
                list = self.parse()
                expression = IgnoreFlakyTestsAbove(token=target_token, goal=goal, list=list)
                if self.lexer.next().kind != TOKEN_KIND.OTHER.RIGHT_PARENTHESIS:
                    raise
            elif target_token.kind == TOKEN_KIND.CONST.ALL_TESTS:
                expression = AllTestsExpression(token=target_token)

        return expression # type: ignore
