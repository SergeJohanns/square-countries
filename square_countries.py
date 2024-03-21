import scipy
import geojson
from shapely.geometry import shape
from shapely.plotting import plot_polygon
import matplotlib.pyplot as plt
from alive_progress import alive_bar

from shapes.square import Square

SHAPES_FILE = "country_shapes.geojson"

with open(SHAPES_FILE) as f:
    geometric_shapes = {
        geo_shape["properties"]["cntry_name"]: shape(geo_shape["geometry"])
        for geo_shape in geojson.load(f)["features"]
    }


def error_function(target_shape, country_shape):
    """
    Return the Jaccard distance between the two shapes.
    """
    return (
        target_shape.symmetric_difference(country_shape).area
        / target_shape.union(country_shape).area
    )


def make_target_function(country_shape):
    def target_function(target_shape_parameters):
        target_shape = Square.from_parameters(target_shape_parameters)
        return error_function(target_shape, country_shape)

    return target_function


def optimize(country_shape):
    iterations = 20
    target_function = make_target_function(country_shape)
    first_guess = Square.first_guess(*country_shape.bounds)

    optimal_parameters = scipy.optimize.basinhopping(
        target_function, first_guess, niter_success=iterations, disp=True
    )

    return optimal_parameters.x, optimal_parameters.fun


TARGET_COUNTRY = "Netherlands"
plot_polygon(geometric_shapes[TARGET_COUNTRY], add_points=False)
optimal_square, score = optimize(geometric_shapes[TARGET_COUNTRY])
print(score)
plot_polygon(Square.from_parameters(optimal_square), add_points=False, color="red")
plt.show()
quit()
