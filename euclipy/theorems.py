from sympy.core.function import _coeff_isneg
from sympy import solve
from .tools import euclicache

class Theorem():
    """
    A singleton class to represent a list of information created by theorems.

    ...

    Attributes
    ----------
    expressions : list
        a list of expressions created by theorems

    Methods
    -------
    solve(self) -> None
        solves all expressions in Theorem.expressions
    triangle_sum_theorem(self, triangle: Triangle) -> None
        adds an expression representing the triangle sum theorem to Theorem.expressions

    Inherits from
    -------------
    None
    """
    
    expressions = []
    expressions_in_order = []

    @euclicache
    def __new__(cls) -> object:
        cls.instance = super().__new__(cls)
        return cls.instance

    def __repr__(self) -> str:
        str = 'Expressions: [\n'
        for expression in self.expressions:
            str += f'{expression} = 0,\n'
        str += ']'
        return str

    def solve(self) -> None:
        for expression in self.expressions:
            _expression_to_remove = expression
            free_measure = []
            known_measures = []
            for measure in expression.free_symbols:
                if measure.value is None:
                    free_measure.append(measure)
                else:
                    known_measures.append(measure)
            if len(free_measure) == 1:
                self.expressions_in_order.append(expression)
                for known in known_measures:
                    expression = expression.subs(known, known.value)
                for solution in solve(expression, free_measure[0]):
                    if _coeff_isneg(solution):
                        continue
                    else:
                        free_measure[0].value = solution
                        self.expressions.remove(_expression_to_remove)
                        break
            else:
                continue
            
    def print_order(self):
        print(self.expressions_in_order)