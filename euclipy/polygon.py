from .tools import euclicache, pairs_in_iterable
from .core import Segment, Angle, GeometricObject, theorem, has_theorems
from sympy import pi, asin, acos

@has_theorems
class Triangle(GeometricObject):
    """
    A class to represent a triangle.

    ...

    Attributes
    ----------
    label : str
        the label of the triangle
    vertices : list
        the vertices of the triangle
    edges : list
        the edges of the triangle
    angles : list
        the angles of the triangle

    Methods
    -------
    None

    Inherits from
    -------------
    None
    """
    # TODO: Add way to impliment inconsistent triangles
    @euclicache
    def __new__(cls, label: str) -> object:
        cls.instance = super().__new__(cls)
        cls.instance.label = cls.canonical_label(label)
        cls.instance.vertices = cls.points_from_label(cls.instance.label)
        cls.instance.edges = [Segment.from_points(pair) for pair in pairs_in_iterable(cls.instance.vertices)]
        cls.instance.angles = [Angle.from_points(triple) for triple in [list(reversed(cls.instance.vertices * 2))[i:i+3] for i in range(3)]]
        return cls.instance
    
    def __repr__(self) -> str:
        return f'Triangle({self.label})'

    @classmethod
    def canonical_label(cls, label) -> str:
        '''Returns a string such that the 0th element is the lexically first element of the string, and all subsequent elements follow a cycled order based on the 0th element.'''
        points = cls.points_from_label(label)
        lexical_min_index = points.index(min(points, key=lambda point: point.label))
        return cls.label_from_points(points[lexical_min_index:] + points[:lexical_min_index])

    def edge_opposite_angle(self, angle) -> Segment:
        assert angle in self.angles, 'Angle not in triangle'
        p1, _, p2 = angle.vertices
        return Segment.from_points([p1, p2])

    def angle_opposite_segment(self, segment) -> Angle:
        assert segment in self.edges, 'Segment not among edges of triangle'
        endpoints = set(segment.endpoints)
        for angle in self.angles:
            p1, _, p2 = angle.vertices
            if set([p1, p2]) == endpoints:
                return angle

    def is_right_triangle(self) -> bool:
        try:
            self.right_angle = [angle for angle in self.angles if angle.measure.value == 90][0]
        except IndexError:
            return False
        else:
            self.hypotenuse = self.edge_opposite_angle(self.right_angle)
            self.legs = [edge for edge in self.edges if edge is not self.hypotenuse]
            return True

    def right_triangle_components(self) -> list:
        if self.is_right_triangle():
            components = []
            for angle in self.angles:
                if angle.measure.value == 90:
                    components.append(Segment(f'{angle.label[0]} {angle.label[4]}'))
                else:
                    components = [Segment(f'{angle.label[0]} {angle.label[4]}'), *components]
            return components
        else:
            raise Exception('Not a right triangle')

    @theorem('Triangle Angle Sum Theorm')
    def triangle_sum_theorem(self) -> None:
        self.add_expression(self.angles[0].measure + self.angles[1].measure + self.angles[2].measure - 180)

    @theorem('Pythagorean Theorem')
    def pythagorean_theorem(self) -> None:
        if self.is_right_triangle():
            (l1, l2), hyp = self.legs, self.hypotenuse
            self.add_expression(l1.measure ** 2 + l2.measure ** 2 - hyp.measure ** 2)

    @theorem('Sine Definitions')
    def sine_definitions(self) -> None:
        if self.is_right_triangle():
            (l1, l2), hyp = self.legs, self.hypotenuse
            self.add_expression(asin(l1.measure / hyp.measure) / pi * 180 - self.angle_opposite_segment(l1).measure)
            self.add_expression(asin(l2.measure / hyp.measure) / pi * 180 - self.angle_opposite_segment(l2).measure)

    @theorem('Cosine Definitions')
    def cosine_definitions(self) -> None:
        if self.is_right_triangle():
            (l1, l2), hyp = self.legs, self.hypotenuse
            self.add_expression(acos(l1.measure / hyp.measure) / pi * 180 - self.angle_opposite_segment(l2).measure)
            self.add_expression(acos(l2.measure / hyp.measure) / pi * 180 - self.angle_opposite_segment(l1).measure)