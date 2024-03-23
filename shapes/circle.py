from math import sqrt
from shapes.shape import Shape
from shapely import Geometry, Point


class Circle(Shape):
    @staticmethod
    def first_guess(minx, miny, maxx, maxy):
        width = maxx - minx
        height = maxy - miny
        midx, midy = (minx + maxx) / 2, (miny + maxy) / 2
        return [midx, midy, sqrt((width / 2) ** 2 + (height / 2) ** 2)]

    @staticmethod
    def get_bounds(minx, miny, maxx, maxy):
        width = maxx - minx
        height = maxy - miny
        return [
            (minx, maxx),
            (miny, maxy),
            (0, sqrt((width / 2) ** 2 + (height / 2) ** 2)),
        ]

    @staticmethod
    def from_parameters(parameters) -> Geometry:
        midpoint_x, midpoint_y, radius = parameters
        return Point(midpoint_x, midpoint_y).buffer(radius)
