from copy import deepcopy
from datetime import date
from random import choice

from exceptions import WeekPlannerInitException
from models.api_models import DayMenuInfo, DaySettings, MenuInfo, WeekPlannerResult, WeekPlannerSettings


class WeekMenuPlanner:
    """Automatically plans a week's menu based on the provided settings and available menus

    Parameters
    ----------
    menus : list[MenuInfo]
        A list of available menus to choose from when planning the week's menu
    week_planner_settings : WeekPlannerSettings
        The settings for the week planner, including the year, week number, protein goal,
        and daily menu settings (effort level, to take away, etc.)
    used_menu_ids : set[int]
        A set of menu IDs that have already been used in previous weeks,
        to avoid repeating the same menus too frequently

    Raises
    ------
    WeekPlannerInitException
        If there are no menus available to initialize the WeekMenuPlanner
    """

    def __init__(
        self, menus: list[MenuInfo], week_planner_settings: WeekPlannerSettings, used_menu_ids: set[int]
    ) -> None:
        if not menus:
            raise WeekPlannerInitException("No menus available to initialize the WeekMenuPlanner.")
        self._menus = menus
        self._week_planner_settings = week_planner_settings
        self._season_number = self._calculate_season_number(
            self._week_planner_settings.year, self._week_planner_settings.week_number
        )
        self._used_menu_ids = used_menu_ids
        self._days_of_the_week_to_plan: list[DaySettings] = []
        self._planning_result: WeekPlannerResult | None = None
        self._multiple_solution_set: set[frozenset[int]] = set()

    def plan_week_menus(self) -> WeekPlannerResult | None:
        """Plans the week's menu based on the provided settings and available menus

        Returns
        -------
        WeekPlannerResult | None
            A WeekPlannerResult object containing the planned menu for the week, or None if planning is not possible.
        """
        self._initialise_planning()

        if not self._plan_day_menu():
            return None

        if self._planning_result:
            self._planning_result.daily_menus.sort(key=lambda day_menu: day_menu.week_day_number)

        return self._planning_result

    def _plan_day_menu(self) -> bool:
        # If the result object is not initialized, return False
        if not self._planning_result:
            return False

        day_settings = self._days_of_the_week_to_plan.pop(0)
        menu_to_choose_from = self._menu_filter(day_settings)

        if not menu_to_choose_from:
            return False

        menu_chosen = choice(menu_to_choose_from)
        self._planning_result.daily_menus.append(
            DayMenuInfo(
                week_day_number=day_settings.week_day_number,
                menu=menu_chosen,
                effort_level_id=day_settings.effort_level_id,
                to_take_away=day_settings.to_take_away,
            )
        )

        if self._days_of_the_week_to_plan:
            return self._plan_day_menu()

        menu_id_set = frozenset(day_menu.menu.id for day_menu in self._planning_result.daily_menus if day_menu.menu.id)

        if menu_id_set in self._multiple_solution_set:
            self._initialise_planning()
            return self._plan_day_menu()

        if self._protein_goal_achieved():
            self._multiple_solution_set.add(menu_id_set)
            return True

        self._initialise_planning()
        return self._plan_day_menu()

    def _menu_filter(self, day_settings: DaySettings) -> list[MenuInfo]:
        menu_to_choose_from = [menu for menu in self._menus if menu.id and menu.id not in self._used_menu_ids]
        menu_to_choose_from = [
            menu for menu in menu_to_choose_from if menu.effort_level_id == day_settings.effort_level_id
        ]
        menu_to_choose_from = [menu for menu in menu_to_choose_from if self._season_number in menu.season_ids]
        if day_settings.to_take_away:
            menu_to_choose_from = [menu for menu in menu_to_choose_from if menu.to_take_away]
        if self._planning_result:
            menu_to_choose_from = [
                menu
                for menu in menu_to_choose_from
                if menu.category_id not in [day_menu.menu.category_id for day_menu in self._planning_result.daily_menus]
            ]
        return menu_to_choose_from

    def _get_protein_total(self) -> float:
        if not self._planning_result:
            return 0.0
        return sum((day_menu.menu.protein for day_menu in self._planning_result.daily_menus), 0.0)

    def _protein_goal_achieved(self) -> bool:
        protein_goal = self._week_planner_settings.protein_goal
        total_protein = self._get_protein_total()
        return protein_goal * 0.9 <= total_protein <= protein_goal * 1.1

    def _initialise_planning(self) -> None:
        self._days_of_the_week_to_plan = deepcopy(self._week_planner_settings.daily_menus)
        self._days_of_the_week_to_plan.sort(key=self._sort_by_available_menus)
        self._planning_result = WeekPlannerResult(
            year=self._week_planner_settings.year, week_number=self._week_planner_settings.week_number, daily_menus=[]
        )

    def _sort_by_available_menus(self, day_settings: DaySettings) -> int:
        return len(self._menu_filter(day_settings))

    @staticmethod
    def _calculate_season_number(year: int, week_number: int) -> int:
        first_day_of_week_date = date.fromisocalendar(year, week_number, 1)
        if first_day_of_week_date.month in (12, 1, 2):
            return 4  # Winter
        elif first_day_of_week_date.month in (3, 4, 5):
            return 1  # Spring
        elif first_day_of_week_date.month in (6, 7, 8):
            return 2  # Summer
        elif first_day_of_week_date.month in (9, 10, 11):
            return 3  # Autumn
        else:
            raise ValueError("Invalid month in date calculation")
