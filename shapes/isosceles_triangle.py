from shapes.shape import Shape
from shapely import Geometry, Polygon
from shapely.affinity import rotate


class IsoscelesTriangle(Shape):
    @staticmethod
    def first_guess(minx, miny, maxx, maxy):
        width = maxx - minx
        height = maxy - miny
        midx = (minx + maxx) / 2
        return [midx, maxy, 2 * width, 2 * height, 0]

    @staticmethod
    def get_bounds(minx, miny, maxx, maxy):
        width = maxx - minx
        height = maxy - miny
        return [
            (minx - max(width, height), maxx + max(width, height)),
            (miny - max(width, height), maxy + max(width, height)),
            (0, 2 * max(width, height)),
            (0, 2 * max(width, height)),
            (0, 360),
        ]

    @staticmethod
    def from_parameters(parameters) -> Geometry:
        midpoint_x, midpoint_y, width, height, rotation = parameters
        vertices = (
            (midpoint_x - width / 2, midpoint_y - height / 2),
            (midpoint_x + width / 2, midpoint_y - height / 2),
            (midpoint_x, midpoint_y + height / 2),
        )
        triangle = Polygon(vertices)
        return rotate(triangle, rotation, origin=(midpoint_x, midpoint_y))
