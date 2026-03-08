import json

import pytest
from unit_test_base_functions import (
    load_expected_week_planner_result_from_json,
    load_menus_from_json,
    load_week_planner_settings_from_json,
)

from exceptions import WeekPlannerInitException
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


def test_week_planner_with_too_few_menus():
    menus = load_menus_from_json("example/menu_collection.json")[:6]  # Only 6 menus available
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_spring.json")
    used_menu_ids = set()
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    week_planner_result = planner.plan_week_menus()
    assert week_planner_result is None


def test_week_planner_in_spring_season():
    menus = load_menus_from_json("example/menu_collection.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_spring.json")
    used_menu_ids = set()
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    assert planner._season_number == 1  # Spring season should be calculated as 1
    week_planner_result = planner.plan_week_menus()
    assert week_planner_result.year == week_planner_settings.year
    assert week_planner_result.week_number == week_planner_settings.week_number
    assert len(week_planner_result.daily_menus) == 7  # Should have 7 daily menus planned for the week
    for day_menu in week_planner_result.daily_menus:
        assert (
            day_menu.menu.season_ids and planner._season_number in day_menu.menu.season_ids
        )  # Ensure all planned menus are suitable for Spring
    for day_menu in week_planner_result.daily_menus:
        assert day_menu.menu.id not in used_menu_ids  # Ensure no used menus are included
    for day_menu in week_planner_result.daily_menus:
        day_setting = next(
            (
                setting
                for setting in week_planner_settings.daily_menus
                if setting.week_day_number == day_menu.week_day_number
            ),
            None,
        )
        assert day_menu.menu.effort_level_id == day_setting.effort_level_id
        assert day_menu.to_take_away == day_setting.to_take_away if day_setting.to_take_away else True


def test_week_planner_in_summer_season():
    menus = load_menus_from_json("example/menu_collection.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_summer.json")
    used_menu_ids = set()
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    assert planner._season_number == 2  # Summer season should be calculated as 2
    week_planner_result = planner.plan_week_menus()
    assert week_planner_result.year == week_planner_settings.year
    assert week_planner_result.week_number == week_planner_settings.week_number
    assert len(week_planner_result.daily_menus) == 7  # Should have 7 daily menus planned for the week
    for day_menu in week_planner_result.daily_menus:
        assert (
            day_menu.menu.season_ids and planner._season_number in day_menu.menu.season_ids
        )  # Ensure all planned menus are suitable for Summer
    for day_menu in week_planner_result.daily_menus:
        assert day_menu.menu.id not in used_menu_ids  # Ensure no used menus are included
    for day_menu in week_planner_result.daily_menus:
        day_setting = next(
            (
                setting
                for setting in week_planner_settings.daily_menus
                if setting.week_day_number == day_menu.week_day_number
            ),
            None,
        )
        assert day_menu.menu.effort_level_id == day_setting.effort_level_id
        assert day_menu.to_take_away == day_setting.to_take_away if day_setting.to_take_away else True


def test_week_planner_in_autumn_season():
    menus = load_menus_from_json("example/menu_collection.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_autum.json")
    used_menu_ids = {293, 15, 158, 63, 122, 45, 78}  # Example of some used menu IDs
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    assert planner._season_number == 3  # Autumn season should be calculated as 3
    week_planner_result = planner.plan_week_menus()
    assert week_planner_result.year == week_planner_settings.year
    assert week_planner_result.week_number == week_planner_settings.week_number
    assert len(week_planner_result.daily_menus) == 7  # Should have 7 daily menus planned for the week
    for day_menu in week_planner_result.daily_menus:
        assert (
            day_menu.menu.season_ids and planner._season_number in day_menu.menu.season_ids
        )  # Ensure all planned menus are suitable for Autumn
    for day_menu in week_planner_result.daily_menus:
        assert day_menu.menu.id not in used_menu_ids  # Ensure no used menus are included
    for day_menu in week_planner_result.daily_menus:
        day_setting = next(
            (
                setting
                for setting in week_planner_settings.daily_menus
                if setting.week_day_number == day_menu.week_day_number
            ),
            None,
        )
        assert day_menu.menu.effort_level_id == day_setting.effort_level_id
        assert day_menu.to_take_away == day_setting.to_take_away if day_setting.to_take_away else True


def test_week_planner_in_winter_season():
    menus = load_menus_from_json("example/menu_collection.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_winter.json")
    used_menu_ids = {1, 15, 32, 56, 123}  # Example of some used menu IDs
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    assert planner._season_number == 4  # Winter season should be calculated as 4
    week_planner_result = planner.plan_week_menus()
    assert week_planner_result.year == week_planner_settings.year
    assert week_planner_result.week_number == week_planner_settings.week_number
    assert len(week_planner_result.daily_menus) == 7  # Should have 7 daily menus planned for the week
    for day_menu in week_planner_result.daily_menus:
        assert (
            day_menu.menu.season_ids and planner._season_number in day_menu.menu.season_ids
        )  # Ensure all planned menus are suitable for Winter
    for day_menu in week_planner_result.daily_menus:
        assert day_menu.menu.id not in used_menu_ids  # Ensure no used menus are included
    for day_menu in week_planner_result.daily_menus:
        day_setting = next(
            (
                setting
                for setting in week_planner_settings.daily_menus
                if setting.week_day_number == day_menu.week_day_number
            ),
            None,
        )
        assert day_menu.menu.effort_level_id == day_setting.effort_level_id
        assert day_menu.to_take_away == day_setting.to_take_away if day_setting.to_take_away else True


def test_week_planner_single_solution():
    menus = load_menus_from_json("example/menu_collection_minimal.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_minimal.json")
    used_menu_ids = set()
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    week_planner_result = planner.plan_week_menus()
    expected_solution = load_expected_week_planner_result_from_json(
        "test/expected_week_planner_result_single_solution.json"
    )
    assert week_planner_result == expected_solution


def test_week_planner_multiple_solutions_with_different_results():
    menus = load_menus_from_json("example/menu_collection.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_spring.json")
    used_menu_ids = set()
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    result_list = set()
    number_of_iterations = 50
    for i in range(number_of_iterations):  # Run the planner multiple times to check for different solutions
        week_planner_result = planner.plan_week_menus()
        menus_in_result = {day_menu.menu.id for day_menu in week_planner_result.daily_menus}
        result_list.add(frozenset(menus_in_result))  # Serialize result for comparison
    assert (
        len(result_list) == number_of_iterations
    )  # Expecting 10 different solutions due to randomness in menu selection


def test_week_planner_enough_menus_but_already_in_use_no_solution():
    menus = load_menus_from_json("example/menu_collection_small.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_spring.json")
    # First round with no used menus to find a valid plan
    used_menu_ids = set()
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    assert planner.plan_week_menus() is not None  # Expecting a valid plan to be found
    # Assuming these IDs correspond to the only menus that would fit the settings,
    # making it impossible to find a valid plan
    used_menu_ids = {1, 2, 3}
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    assert planner.plan_week_menus() is None  # Expecting no solution to be found


def test_week_planner_protein_too_small():
    menus = load_menus_from_json("example/menu_collection.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_spring.json")
    week_planner_settings.protein_goal = 10  # Set an unrealistically low protein goal to force no solution
    used_menu_ids = set()
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    assert planner.plan_week_menus() is None  # Expecting no solution to be found due to low protein goal


def test_week_planner_protein_too_high():
    menus = load_menus_from_json("example/menu_collection.json")
    week_planner_settings = load_week_planner_settings_from_json("example/week_planner_settings_spring.json")
    week_planner_settings.protein_goal = 1000  # Set an unrealistically high protein goal to force no solution
    used_menu_ids = set()
    planner = WeekMenuPlanner(menus, week_planner_settings, used_menu_ids)
    assert planner.plan_week_menus() is None  # Expecting no solution to be found due to low protein goal
