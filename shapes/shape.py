from abc import ABC, abstractmethod
from shapely import Geometry


class Shape(ABC):
    @classmethod
    @abstractmethod
    def first_guess(cls, minx, miny, maxx, maxy):
        """
        Returns a first guess for the parameters of the shape that fits in the given bounding box.
        """

    @staticmethod
    @abstractmethod
    def from_parameters(cls, parameters) -> Geometry:
        """
        Returns a geometry of the shape with the given parameters.
        """
