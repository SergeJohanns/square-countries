from abc import ABC, abstractmethod
from shapely import Geometry


class Shape(ABC):
    @staticmethod
    @abstractmethod
    def first_guess(minx, miny, maxx, maxy):
        """
        Returns a first guess for the parameters of the shape that fits in the given bounding box.
        """

    @staticmethod
    @abstractmethod
    def get_bounds(minx, miny, maxx, maxy):
        """
        Return bounds on the parameters of the shape according to the given bounding box.
        """

    @staticmethod
    @abstractmethod
    def from_parameters(parameters) -> Geometry:
        """
        Returns a geometry of the shape with the given parameters.
        """
