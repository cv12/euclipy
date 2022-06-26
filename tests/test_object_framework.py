import sys
sys.path.append('../')

import pytest
import networkx
import numpy as np

from euclipy.core import *
from euclipy.measure import *
from euclipy.polygon import *
from euclipy.tools import *
from euclipy.exceptions import *

def test_basic_geometric_object_framework():
    assert(Point('A') is Point('A'))
    assert(Segment('B A') is Segment('A B'))
    assert(Angle('A B C') is Angle('A B C'))
    assert(Angle('A B C') is not Angle('C A B'))
    assert(Triangle('A B C') is Triangle('C A B'))

def test_basic_measure_framework():
    Segment('A B').measure = 1
    Segment('A C').measure = Segment('A B').measure
    assert(Segment('A B').measure is Segment('A C').measure)
    assert(Segment('A B').measure.measured_objects == Segment('A C').measure.measured_objects)
    # TODO: Fix for none

def test_theorem_framework():
    pass

def test_theorem_application():
    Triangle("A B C").triangle_sum_theorem()
    Triangle('A B C').angles[0].measure = 30
    Triangle('A B C').angles[1].measure = 60
    Triangle('A B C').solver.solve()
    Triangle("A B C").pythagorean_theorem()
    assert(Triangle('A B C').angles[2].measure.value == 90)
    assert(Triangle('A B C').is_right_triangle())
    SOLVER.proof_record(Triangle('A B C').angles[2].measure - 90)


test_theorem_application()