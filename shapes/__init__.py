import importlib


def get_shape(name):
    """
    Import the class of the shape `name` (in snake_case)
    """
    print("shapes", name)
    shape_module = importlib.import_module(f"shapes.{name}")
    pascal_case_name = name.title().replace("_", "")
    return getattr(shape_module, pascal_case_name)
