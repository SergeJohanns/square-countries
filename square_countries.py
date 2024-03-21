import json
import argparse
import pathlib
import scipy
import geojson
from shapely.geometry import shape
from shapely.plotting import plot_polygon
import matplotlib.pyplot as plt
from alive_progress import alive_it

from shapes.square import Square


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


def calculate_scores(countries, target_countries=None):
    if target_countries is None:
        target_countries = countries.keys()
    scores = []
    bar = alive_it(target_countries)

    for country_name in bar:
        shape = countries[country_name]
        bar.text = country_name
        optimal_square, score = optimize(countries[country_name])
        scores.append(
            {
                "country": country_name,
                "parameters": list(optimal_square),
                "score": score,
            }
        )

    scores.sort(key=lambda x: x["score"])
    return scores


def get_country_shapes(file):
    with file as f:
        return {
            geo_shape["properties"]["cntry_name"]: shape(geo_shape["geometry"])
            for geo_shape in geojson.load(f)["features"]
        }


def country_to_filename(country_name):
    return f"{country_name.lower().replace(' ', '_')}.png"


def write_report(report_output, scores):
    report_output.mkdir(exist_ok=True, parents=True)
    for item in scores:
        country = item["country"]
        plot_polygon(countries[country], add_points=False)
        square = Square.from_parameters(item["parameters"])
        plot_polygon(square, color="red", add_points=False)
        plt.savefig(report_output / f"{country_to_filename(country)}")
        plt.clf()
    with open(args.report_output / "report.md", "w") as f:
        f.write("# Country Shape Tester\n")
        f.write("## Countries\n")
        f.write("The following countries were tested:\n")
        for item in scores:
            f.write(f"- {item['country']}\n")
        f.write("\n")
        f.write("## Results\n")
        f.write(
            "The following table shows the scores and optimal shape parameters for each country:\n"
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
        help="Path to write the markdown report to.",
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
        help="GeoJSON file containing the country shapes.",
        default="country_shapes.geojson",
        type=open,
    )
    args = parser.parse_args()

    countries = get_country_shapes(args.country_file)
    target_countries = list(countries.keys())[:10]
    scores = calculate_scores(countries, target_countries)

    write_report(args.report_output, scores)

    if args.json_output:
        with args.json_output as f:
            json.dump(scores, f, indent=4)
