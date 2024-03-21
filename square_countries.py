import json
import scipy
import geojson
from shapely.geometry import shape
from shapely.plotting import plot_polygon
import matplotlib.pyplot as plt
from alive_progress import alive_it

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
    iterations = 10
    target_function = make_target_function(country_shape)
    first_guess = Square.first_guess(*country_shape.bounds)

    optimal_parameters = scipy.optimize.basinhopping(
        target_function, first_guess, niter_success=iterations
    )

    return optimal_parameters.x, optimal_parameters.fun


def calculate_scores(target_countries=list(geometric_shapes.keys())):
    scores = []
    bar = alive_it(target_countries)

    for country_name in bar:
        shape = geometric_shapes[country_name]
        bar.text = country_name
        optimal_square, score = optimize(geometric_shapes[country_name])
        scores.append(
            {
                "country": country_name,
                "parameters": list(optimal_square),
                "score": score,
            }
        )

    scores.sort(key=lambda x: x["score"])
    return scores


target_countries = list(geometric_shapes.keys())[:10]
scores = calculate_scores(target_countries)
for item in scores:
    country = item["country"]
    plot_polygon(geometric_shapes[country], add_points=False)
    square = Square.from_parameters(item["parameters"])
    plot_polygon(square, color="red", add_points=False)
    plt.show()
print(json.dumps(scores))
