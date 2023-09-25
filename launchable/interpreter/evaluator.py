import click
from launchable.interpreter.parser import AllTestsExpression, Expression, IgnoreFlakyTestsAbove, SortByMostImportantExpression, SubsetByDuraitonExpression


class Evaluator:
    def __init__(self, expression: Expression) -> None:
        self.expression = expression
        pass

    def evaluate(self):
        a = self._evaluate(self.expression)
        return a
    def _evaluate(self, expression: Expression):
        if isinstance(expression, SubsetByDuraitonExpression):
            list = self._evaluate(expression=expression.list)
            result = {}
            if isinstance(expression.list, SortByMostImportantExpression):
                result['target'] = expression.goal.value
            return {
                **result,
                **list
            }
        elif isinstance(expression, SortByMostImportantExpression):
            list = self._evaluate(expression=expression.list)
            return {
                **list
            }
        elif isinstance(expression, IgnoreFlakyTestsAbove):
            list = self._evaluate(expression=expression.list)
            return {
                'ignore_flaky_tests_above': expression.goal,
                **list
            }
        elif isinstance(expression, AllTestsExpression):
            return {}

