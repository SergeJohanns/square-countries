from shapes.shape import Shape
from shapely import Geometry, Polygon
from shapely.affinity import rotate


class Rectangle(Shape):
    @staticmethod
    def first_guess(minx, miny, maxx, maxy):
        return [minx, miny, maxx - minx, maxy - miny, 0]

    @staticmethod
    def get_bounds(minx, miny, maxx, maxy):
        return [
            (minx, maxx),
            (miny, maxy),
            (0, maxx - minx),
            (0, maxy - miny),
            (0, 360),
        ]

    @staticmethod
    def from_parameters(parameters) -> Geometry:
        bottom_left_x, bottom_left_y, width, height, rotation = parameters
        vertices = (
            (bottom_left_x, bottom_left_y),
            (bottom_left_x + width, bottom_left_y),
            (bottom_left_x + width, bottom_left_y + height),
            (bottom_left_x, bottom_left_y + height),
        )
        square = Polygon(vertices)
        midpoint = (bottom_left_x + width / 2, bottom_left_y + height / 2)
        return rotate(square, rotation, origin=midpoint)
