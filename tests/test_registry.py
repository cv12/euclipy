import sys
sys.path.append('../')
import pytest

from euclipy.core import *
from euclipy.measure import *
from euclipy.polygon import *
from euclipy.theorems import *
from euclipy.tools import *
from euclipy.registry import *

def test_registry_entries():
    try:
        del Registry.instance
    except AttributeError:
        pass
    Segment([Point("A"), Point("B")]).measure.value = 1
    assert len(Registry().entries['SegmentMeasure']) == 1