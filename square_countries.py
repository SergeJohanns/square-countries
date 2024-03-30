import json
import argparse
import pathlib
import scipy
import geojson
from shapely.geometry import shape
from shapely.plotting import plot_polygon
import matplotlib.pyplot as plt
from alive_progress import alive_it

from shapes import get_shape


def error_function(target_outline, country_outline):
    """
    Return the Jaccard distance between the two shapes.
    """
    return (
        target_outline.symmetric_difference(country_outline).area
        / target_outline.union(country_outline).area
    )


def make_target_function(country_outline, target_shape):
    def target_function(target_outline_parameters):
        target_outline = target_shape.from_parameters(target_outline_parameters)
        return error_function(target_outline, country_outline)

    return target_function


def basin_hop_optimize(country_outline, target_shape):
    iterations = 10
    target_function = make_target_function(country_outline)
    first_guess = target_shape.first_guess(*country_outline.bounds)

    optimal_parameters = scipy.optimize.basinhopping(
        target_function, first_guess, niter_success=iterations
    )

    return optimal_parameters.x, optimal_parameters.fun


def dual_annealing_optimize(country_outline, target_shape):
    target_function = make_target_function(country_outline, target_shape)
    bounds = target_shape.get_bounds(*country_outline.bounds)

    optimal_parameters = scipy.optimize.dual_annealing(target_function, bounds)

    return optimal_parameters.x, optimal_parameters.fun


def calculate_scores(countries, target_countries, target_shape, optimize):
    if target_countries is None:
        target_countries = countries.keys()
    scores = []
    bar = alive_it(target_countries)

    for country_name in bar:
        shape = countries[country_name]
        bar.text = country_name
        best_fit_parameters, score = optimize(countries[country_name], target_shape)
        scores.append(
            {
                "country": country_name,
                "parameters": list(best_fit_parameters),
                "score": score,
            }
        )

    scores.sort(key=lambda x: x["score"])
    return scores


def get_country_shapes(file, name_field):
    with file as f:
        return {
            geo_shape["properties"][name_field]: shape(geo_shape["geometry"]).buffer(0)
            # .buffer(0) fixes some invalid geometries, see https://stackoverflow.com/a/14094033/13511743
            for geo_shape in geojson.load(f)["features"]
        }


def simplify_country_shape(shape, tolerance):
    minx, miny, maxx, maxy = shape.bounds
    short_side = min(maxx - minx, maxy - miny)
    return shape.simplify(short_side * tolerance).buffer(0)


def country_to_filename(country_name):
    return f"images/{country_name.lower().replace(' ', '_')}.png"


def write_report(countries, report_output, scores, shape):
    image_output = report_output / "images"
    image_output.mkdir(exist_ok=True, parents=True)
    for item in scores:
        plt.axis("off")
        plt.tight_layout()
        country = item["country"]
        plot_polygon(countries[country], add_points=False)
        best_fit = shape.from_parameters(item["parameters"])
        plot_polygon(best_fit, color="red", add_points=False)
        plt.savefig(report_output / f"{country_to_filename(country)}")
        plt.clf()
    with open(args.report_output / "README.md", "w") as f:
        f.write("# Country Shape Test Results\n")
        f.write(
            "The following table shows the scores and optimal shape for each country:\n"
        )
        f.write("| Country | Error | Image |\n")
        f.write("|---------|-------|------------|\n")
        for item in scores:
            f.write(
                f"| {item['country']} | {item['score']:.2%} | ![{item['country']}]({country_to_filename(item['country'])}) |\n"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Country Shape Tester",
        description="Program to test which country is best approximated by a certain shape.",
    )
    parser.add_argument(
        "--report-output",
        help="Path to write the markdown report to. (default is 'report')",
        type=pathlib.Path,
        default="report",
    )
    parser.add_argument(
        "--json-output",
        help="File to write the resulting scores and optimal shape parameters to.",
        type=argparse.FileType("w", encoding="latin-1"),
    )
    parser.add_argument(
        "--country-file",
        help="GeoJSON file containing the country shapes. (default is 'country_shapes.geojson')",
        default="country_shapes.geojson",
        type=open,
    )
    parser.add_argument(
        "--country-name-field",
        help="Name of the GeoJSON property containing the country name. (default is 'cntry_name', see the file for the right field)",
        default="cntry_name",
    )
    parser.add_argument(
        "--target-countries",
        help="List of countries to test. (default is all countries in the file)",
        nargs="+",
        default=None,
    )
    parser.add_argument(
        "--shape",
        help="Name of shape to use, in snake_case. (default is 'square')",
        default="square",
    )
    parser.add_argument(
        "--method",
        help="Optimization method to use: Dual Annealing (default) or Basin-Hopping (faster).",
        choices=["basin-hop", "dual-annealing"],
        default="dual-annealing",
    )
    parser.add_argument(
        "--tolerance",
        help="Tolerance for simplifying the country shapes, as a portion of the minimum of the width and height. (default is 0.01, 0 for no simplification)",
        type=float,
        default=0.01,
    )
    args = parser.parse_args()

    countries = get_country_shapes(args.country_file, args.country_name_field)
    if args.tolerance != 0:
        simplified_countries = {
            country: simplify_country_shape(shape, args.tolerance)
            for country, shape in countries.items()
        }
    match args.method:
        case "basin-hop":
            optimize = basin_hop_optimize
        case "dual-annealing":
            optimize = dual_annealing_optimize
    target_shape = get_shape(args.shape)
    scores = calculate_scores(
        simplified_countries if args.tolerance != 0 else countries,
        args.target_countries,
        target_shape,
        optimize,
    )

    write_report(countries, args.report_output, scores, target_shape)

    if args.json_output:
        with args.json_output as f:
            json.dump(scores, f, indent=4)
