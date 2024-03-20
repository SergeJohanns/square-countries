import matplotlib.pyplot as plt
import geojson
from shapely.geometry import shape
from shapely.plotting import plot_polygon

from shapes.square import Square

SHAPES_FILE = "country_shapes.geojson"

with open(SHAPES_FILE) as f:
    geometric_shapes = {
        geo_shape["properties"]["cntry_name"]: shape(geo_shape["geometry"])
        for geo_shape in geojson.load(f)["features"]
    }

plot_polygon(geometric_shapes["Netherlands"], add_points=False)
dutch_square = Square.first_guess(*geometric_shapes["Netherlands"].bounds)
plot_polygon(Square.from_parameters(dutch_square), add_points=False)
plt.show()
quit()
