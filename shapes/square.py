from shapes.shape import Shape
from shapely import Geometry, Polygon
from shapely.affinity import rotate


class Square(Shape):
    @staticmethod
    def first_guess(minx, miny, maxx, maxy):
        return [minx, miny, max(maxx - minx, maxy - miny), 0]

    @staticmethod
    def get_bounds(minx, miny, maxx, maxy):
        return [
            (minx, maxx),
            (miny, maxy),
            (0, max(maxx - minx, maxy - miny)),
            (0, 360),
        ]

    @staticmethod
    def from_parameters(parameters) -> Geometry:
        bottom_left_x, bottom_left_y, side_length, rotation = parameters
        vertices = (
            (bottom_left_x, bottom_left_y),
            (bottom_left_x + side_length, bottom_left_y),
            (bottom_left_x + side_length, bottom_left_y + side_length),
            (bottom_left_x, bottom_left_y + side_length),
        )
        square = Polygon(vertices)
        midpoint = (bottom_left_x + side_length / 2, bottom_left_y + side_length / 2)
        return rotate(square, rotation, origin=midpoint)
