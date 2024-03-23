from shapes.shape import Shape
from shapely import Geometry, Polygon


class Triangle(Shape):
    @staticmethod
    def first_guess(minx, miny, maxx, maxy):
        width = maxx - minx
        height = maxy - miny
        return [
            minx - width / 2,
            miny,
            minx + width / 2,
            miny,
            minx + width / 2,
            maxy + height,
        ]

    @staticmethod
    def get_bounds(minx, miny, maxx, maxy):
        width = maxx - minx
        height = maxy - miny
        return [
            (minx - width, minx + width),
            (miny - height, maxy + height),
            (minx - width, minx + width),
            (miny - height, maxy + height),
            (minx - width, minx + width),
            (miny - height, maxy + height),
        ]

    @staticmethod
    def from_parameters(parameters) -> Geometry:
        a_x, a_y, b_x, b_y, c_x, c_y = parameters
        vertices = (
            (a_x, a_y),
            (b_x, b_y),
            (c_x, c_y),
        )
        return Polygon(vertices)
