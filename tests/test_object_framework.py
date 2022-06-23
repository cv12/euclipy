import sys
sys.path.append('../')

import pytest

from euclipy.core import *
from euclipy.measure import *
from euclipy.polygon import *
from euclipy.tools import *
from euclipy.exceptions import *

def test():
    assert(Point('A') is Point('A'))
    assert(Segment('B A') is Segment('A B'))
    assert(Triangle("C A B") is Triangle("A B C"))
    Segment('A B').measure = 1
    Segment('A C').measure = Segment('A B').measure
    assert(Segment('A B').measure is Segment('A C').measure)
    assert(Segment('A B').measure.measured_objects == Segment('A C').measure.measured_objects)
    #TODO: Fix for none
    assert(Theorem() is Theorem())
    Triangle("A B C").triangle_sum_theorem()
    Triangle('A B C').angles[0].measure = 30
    Triangle('A B C').angles[1].measure = 60
    Theorem().solve()
    assert(Triangle('A B C').angles[2].measure.value == 90)
    assert(Triangle('A B C').is_right_triangle())
    Segment('A B').measure = 5
    Triangle('A B C').pythagorean_theorem()
    Theorem().solve()
    print(Segment('B C').measure.value)
    Segment('A B').intersects(Segment('B C'), 'D')

#print(Triangle('A B C').angles[2].measure)
Triangle('A B C')
Angle("C B A").measure = 90
#print(Segment('C A').measure)
# Triangle('A B C').angles[2].measure = 30
Segment('B C').measure = 1
Segment('C A').measure = 2
Triangle('A B C').sine_definitions()
Triangle('A B C').solver.solve()
print(Segment("B C").measure.value)

# Theorem.print_order()
# #print(Angle("B A C").measure.value)