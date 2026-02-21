import pytest
from unit_test_base_functions import load_week_planner_settings_from_json

from exceptions import WeekPlannerInitException
from models.api_models import WeekPlannerSettings
from planner.week_planner import WeekMenuPlanner


def test_season_calculation():
    # Test case for a date in February (should be Winter)
    year, week_number = 2026, 9  # This corresponds to a date in February
    assert WeekMenuPlanner._calculate_season_number(year, week_number) == 4

    # Test case for a date in March (should be Spring)
    year, week_number = 2026, 10  # This corresponds to a date in March
    assert WeekMenuPlanner._calculate_season_number(year, week_number) == 1

    # Test case for a date in May (should be Spring)
    year, week_number = 2026, 22  # This corresponds to a date in May
    assert WeekMenuPlanner._calculate_season_number(year, week_number) == 1

    # Test case for a date in June (should be Summer)
    year, week_number = 2026, 23  # This corresponds to a date in June
    assert WeekMenuPlanner._calculate_season_number(year, week_number) == 2

    # Test case for a date in August (should be Summer)
    year, week_number = 2026, 36  # This corresponds to a date in August
    assert WeekMenuPlanner._calculate_season_number(year, week_number) == 2

    # Test case for a date in September (should be Autumn)
    year, week_number = 2026, 37  # This corresponds to a date in September
    assert WeekMenuPlanner._calculate_season_number(year, week_number) == 3

    # Test case for a date in November (should be Autumn)
    year, week_number = 2026, 49  # This corresponds to a date in November
    assert WeekMenuPlanner._calculate_season_number(year, week_number) == 3

    # Test case for a date in December (should be Winter)
    year, week_number = 2026, 53  # This corresponds to a date in December
    assert WeekMenuPlanner._calculate_season_number(year, week_number) == 4


def test_week_planner_with_no_menus():
    menus = []  # No menus available
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_spring.json")
    used_menu_ids = set()
    with pytest.raises(WeekPlannerInitException, match="No menus available to initialize the WeekMenuPlanner."):
        WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
