from sympy import Symbol

class Measure(Symbol):
    """
    A class to represent a measure of a geometric object.

    ...

    Attributes
    ----------
    label : str
        the label of the point
    measured_objects : list
        the geometric objects measured by the measure
    value : int
        the value of the measure

    Methods
    -------
    add_measured_object(self, geometric_object) -> None
        adds a geometric object to the list of measured objects

    Inherits from
    -------------
    Symbol
    """
    label = 1
    defined_measures = dict()
    def __new__(cls):
        name = 'M' + str(cls.label)
        cls.label += 1
        instance = super().__new__(cls, name)
        instance.measured_objects = []
        instance.value = None
        return instance

    def add_measured_object(self, measured_object):
        self.measured_objects.append(measured_object)