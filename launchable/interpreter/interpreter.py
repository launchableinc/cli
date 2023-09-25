from typing import Dict
from launchable.interpreter.evaluator import Evaluator
from launchable.interpreter.lexer import Lexer
from launchable.interpreter.parser import Parser


def interpret(string: str) -> Dict[str, str]:
    lexer = Lexer(string=string)
    parser = Parser(lexer=lexer)
    expression = parser.parse()
    evaluator = Evaluator(expression=expression)
    return evaluator.evaluate() # type: ignore
