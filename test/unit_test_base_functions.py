import json

from pydantic import TypeAdapter

from models.api_models import MenuInfo, WeekPlannerSettings


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


def load_week_planner_settings_from_json(json_file_path: str) -> WeekPlannerSettings:
    """Loads week planner settings from a JSON file and returns a WeekPlannerSettings object

    Parameters
    ----------
    json_file_path : str
        The file path to the JSON file containing the week planner settings data

    Returns
    -------
    WeekPlannerSettings
        A WeekPlannerSettings object loaded from the JSON file

    Raises
    ------
    ValueError
        If the JSON file is empty or does not contain valid week planner settings data
    """

    try:
        with open(json_file_path, "r") as file:
            week_planner_settings_py = json.load(file)
    except FileNotFoundError:
        raise ValueError(f"JSON file not found at {json_file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file at {json_file_path}")

    if not week_planner_settings_py:
        raise ValueError(f"No week planner settings found in the JSON file at {json_file_path}")

    type_adapter = TypeAdapter(WeekPlannerSettings)
    return type_adapter.validate_python(week_planner_settings_py)
