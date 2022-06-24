from collections import namedtuple, defaultdict
from functools import wraps
import inspect
import sympy

from euclipy.exceptions import InformationError
from .tools import euclicache
from .measure import Measure

LABEL_DELIMITER = ' '

SubstitutionRecord = namedtuple('SubstitutionRecord', ['symbol', 'substituted_by', 'in_expression', 'result'])

class TracedExpression:
    def __init__(self, expr, from_bound_method, **kwargs):
        """from_bound_method is a @theorem-docorated bound method of a GeometricObject instance which is giving rise to expr (an expression which is a sympy.Expr instance)."""
        self.original_expr = expr # Original expression (when istantiated and inserted into the Solver); will not be modified
        self.expr = expr # Expressions may evolve during the solving process through substitutions; self.expr holds the current expression
        self.from_bound_method = from_bound_method
        self.obj = from_bound_method.__self__ # The GeometricObject instance whose bound @theorem-decorated method is giving rise to expr
        self.theorem = from_bound_method.__name__ # The name of the @theorem-decorated method
        self.params = kwargs # Dictionary of parameters that the @theorem-decorated method has used along with its self to create the expression
        self.title = from_bound_method._title # The title of the @theorem-decorated method
        self.doc = from_bound_method.__doc__ # The docstring of the @theorem-decorated method, used to describe the theorem
        self.substitutions = [] # List of SubstitutionRecords describing substitutions performed on the expression (from original_expr to expr)
        self.solved = False # Whether the expression evaluates to zero

    def substitute(self, x, y):
        """Substitute x for y in the expression (self.expr).
        Return a SubstitutionRecord describing the substitution if the substitution chaneged the expression (i.e. the free symbol being substituted was in the expression).
        Return None if the substitution did not change the expression (i.e. the free symbol being substituted was not in the expression)."""
        result = self.expr.subs(x, y)
        if result != self.expr: # i.e. substitution changed the expression
            # Keep track of ther performed substitution
            substitution_record = SubstitutionRecord(x, y, self.expr, result)
            self.substitutions.append(substitution_record)
            # Update the expression
            self.expr = result
            # Mark expression as solved if it evaluates to zero
            if result == 0:
                self.solved = True
            elif len(result.free_symbols) == 0:
                raise InformationError('One or more given facts are untrue.')
            return substitution_record

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr}, original_expr={self.original_expr}, obj={self.obj}, theorem='{self.theorem}', params={self.params}, substitutions={self.substitutions})"

class Solver:
    def __init__(self):
        self.expressions = [] # List of TracedExpressions
        self.substitutions = [] # List of SubstitutionRecords

    def __repr__(self):
        str = ''
        for expression in self.expressions:
            str += f'Original Expression: {expression.original_expr} \nCurrent Expression: {expression.expr} \nObject: {expression.obj} \nTheorem: {expression.theorem} \nSubstitutions:'
            for substitution in expression.substitutions:
                str += f'\n\t{substitution}'
            str += '\n'
        return str[:-1]

    def add_expression(self, expr, from_bound_method, **kwargs):
        assert isinstance(expr, sympy.Expr)
        self.expressions.append(TracedExpression(expr, from_bound_method, **kwargs))

    def substitute(self, x, y):
        for expr in self.expressions:
            substitution_record = expr.substitute(x, y)
            if substitution_record:
                self.substitutions.append(substitution_record)

    def solve(self):
        """Solve expressions for positive values.
        Raise exception if any variable has a unique non-positive solution.
        Raise an exception if any variable with non-unique solutions has zero or more than one positive solutions."""
        # Substitute values for measures with known values
        for tracedexpr in self.expressions:
            for measure in tracedexpr.expr.free_symbols:
                if measure.value is not None:
                    self.substitute(measure, measure.value)
        solutions = sympy.solve([tracedexpr.expr for tracedexpr in self.expressions], dict=True)
        uniques = set.intersection(*[set(sol.items()) for sol in solutions])
        non_uniques = [set(sol.items()) - uniques for sol in solutions]
        uniques = dict(uniques)
        non_uniques = [dict(non_unique) for non_unique in non_uniques] # list of dicts with common keys
        uniques_without_free_symbols = {k:v for k,v in uniques.items() if not v.free_symbols}
        if not all(e > 0 for e in uniques_without_free_symbols.values()):
            raise InformationError('The given facts create an impossible solution(s).')
        non_uniques_without_free_symbols = [{k:v for k, v in sol.items() if not v.free_symbols} for sol in non_uniques]
        solution_sets = defaultdict(set)
        for d in non_uniques_without_free_symbols:
            for k, v in d.items():
                solution_sets[k].add(v)
        non_uniques_solution_candidate = {k: {e for e in v if e > 0} for k, v in solution_sets.items()}
        assert all(len(v) == 1 for v in non_uniques_solution_candidate.values()), "All variables must have exactly one positive solution"
        non_uniques_solution = {k: v.pop() for k, v in non_uniques_solution_candidate.items()}
        valid_solutions = uniques_without_free_symbols | non_uniques_solution
        # Substitute valid_solutions for variables in expressions
        for sym, val in valid_solutions.items():
            self.substitute(sym, val)
            sym.value = val
                
SOLVER = Solver()

def has_theorems(cls):
    cls._theorems = [method for method in [getattr(cls, methodname) for methodname in dir(cls)] if hasattr(method, '_is_theorem')]
    cls.solver = SOLVER
    return cls

def theorem(title):
    def function_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        wrapper._is_theorem = True
        wrapper._title = title
        return wrapper
    return function_decorator

class Point:
    """
    A class to represent a point.

    ...

    Attributes
    ----------
    label : str
        the label of the point

    Methods
    -------
    None

    Inherits from
    -------------
    None
    """

    @euclicache
    def __new__(cls, label) -> object:
        cls.instance = super().__new__(cls)
        cls.instance.label = label
        return cls.instance
    
    def __repr__(self) -> str:
        return f'Point({self.label})'

    @staticmethod
    def canonical_label(label) -> str:
        return label

class GeometricObject:
    """
    A class to represent a geometric object.

    ...

    Attributes
    ----------
    measure : Measure
        the measure of the geometric object
    value : int
        the value of the measure of the geometric object

    Methods
    -------
    None

    Inherits from
    -------------
    None
    """
    @staticmethod
    def points_from_label(label: str) -> list[Point]:
        return [Point(point_label) for point_label in label.split(LABEL_DELIMITER)]

    @staticmethod
    def label_from_points(points: list[Point]) -> str:
        return LABEL_DELIMITER.join([point.label for point in points])

    @classmethod
    def from_points(cls, points: list) -> 'GeometricObject':
        return cls.__new__(cls, cls.label_from_points(points))

    def add_expression(self, expr, **kwargs):
        from_bound_method = getattr(self, inspect.getframeinfo(inspect.currentframe().f_back).function)
        self.solver.add_expression(expr, from_bound_method, **kwargs)
    
    def apply_all_theorems(self):
        for theorem in self._theorems:
            theorem(self)

    @property
    def measure(self) -> Measure:
        try:
            return self._measure
        except AttributeError:
            self._measure = Measure()
            self.measure.measured_class = self.__class__
            self._measure.add_measured_object(self)
            return self._measure

    @measure.setter
    def measure(self, other_measure_or_value) -> None:
        if isinstance(other_measure_or_value, Measure):
            # Setting measure equal to another measure
            other_measure = other_measure_or_value
            try:
                if self._measure is not other_measure:
                    # Merge self.measured_objects into other_measure.measured_objects and set self's measure to the other measure.
                    other_measure.measured_objects += self._measure.measured_objects
                    self._measure = other_measure
            except AttributeError:
                # Measure has not been defined for self. Assign self's measure to other_measure.
                self._measure = other_measure
                other_measure.add_measured_object(self)
        else:
            # Setting measure equal to a value
            value = other_measure_or_value
            try:
                self._measure.value = value
            except AttributeError:
                self._measure = Measure()
                self._measure.measured_class = self.__class__
                self._measure.add_measured_object(self)
                self._measure.value = value
            finally:
                existing_measure_matching_value = self._measure.defined_measures.get(self._measure.value)
                if existing_measure_matching_value is not None:
                    self._measure = existing_measure_matching_value
                else:
                    self._measure.defined_measures[self._measure.value] = self._measure

    @property
    def value(self) -> int:
        try:
            return self._measure.value
        except AttributeError:
            self._measure = Measure()
            self._measure.add_measured_object(self)
            return self._measure.value

    @classmethod
    def canonical_label(cls, label) -> str:
        return label

class Segment(GeometricObject):
    """
    A class to represent a line segment.

    ...

    Attributes
    ----------
    label : str
        the label of the segment
    endpoints : list
        the endpoints of the segment

    Methods
    -------
    None

    Inherits from
    -------------
    GeometricObject
    """

    _vertical_angles = []

    @euclicache
    def __new__(cls, label: str) -> object:
        cls.instance = super().__new__(cls)
        cls.instance.label = cls.canonical_label(label)
        cls.instance.endpoints = cls.points_from_label(label)
        cls.instance.intersections = []
        return cls.instance

    def __repr__(self) -> str:
        return f'Segment({self.label} | {self.measure})'

    @classmethod
    def canonical_label(cls, label) -> str:
        '''Sorts a point labels in Segment labels alphabetically.'''
        return cls.label_from_points(sorted(cls.points_from_label(label), key=lambda point: point.label))

    def intersects(self, segment, point: str) -> None:
        self.intersections.append((segment, Point(point)))
        segment.intersections.append((self, Point(point)))

class Angle(GeometricObject):
    """
    A class to represent an angle.

    ...

    Attributes
    ----------
    label : str
        the label of the angle

    Methods
    -------
    None

    Inherits from
    -------------
    GeometricObject
    """
    @euclicache
    def __new__(cls, label: str) -> object:
        cls.instance = super().__new__(cls)
        cls.instance.vertices = cls.points_from_label(label)
        cls.instance.label = cls.canonical_label(label)
        return cls.instance

    def __repr__(self) -> str:
        return f'Angle({self.label} | {self.measure})'