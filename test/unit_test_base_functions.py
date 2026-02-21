import json

from pydantic import TypeAdapter

from models.api_models import MenuInfo


def load_menus_from_json(json_file_path: str) -> list[MenuInfo]:
    """Loads menus from a JSON file and returns a list of MenuInfo objects

    Parameters
    ----------
    json_file_path : str
        The file path to the JSON file containing the menu data

    Returns
    -------
    list[MenuInfo]
        A list of MenuInfo objects loaded from the JSON file

    Raises
    ------
    ValueError
        If the JSON file is empty or does not contain valid menu data
    """

    try:
        with open(json_file_path, "r") as file:
            menu_collection_py = json.load(file)
    except FileNotFoundError:
        raise ValueError(f"JSON file not found at {json_file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file at {json_file_path}")

    if not menu_collection_py:
        raise ValueError(f"No menus found in the JSON file at {json_file_path}")

    type_adapter = TypeAdapter(list[MenuInfo])
    menu_collection = type_adapter.validate_python(menu_collection_py)
    for menu_id, menu in enumerate(menu_collection):
        menu.id = menu_id + 1  # Assign a unique ID to each menu based on its position in the list
    return menu_collection
