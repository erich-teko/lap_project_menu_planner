from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


class EffortLevel(IntEnum):
    QUICK = 1
    MEDIUM = 2
    COMPLICATED = 3


@dataclass
class DayMenu:
    week_day_number: int  # 1=Monday, 7=Sunday
    effort_level: EffortLevel | None = None
    to_take_away: bool = False
    menu_id: int | None = None


@dataclass
class WeekPlanner:
    year: int
    week_number: int
    protein_goal: float
    daily_menus: list[DayMenu]  # List of 7 DayMenu objects, one for each day of the week


def create_default_week_planner() -> WeekPlanner:
    now = datetime.now()
    current_year, current_week, _ = now.isocalendar()
    return WeekPlanner(
        year=current_year,
        week_number=current_week + 1,
        protein_goal=25.0 * 7,  # Default to 25g protein per day for a week
        daily_menus=[DayMenu(week_day_number=i) for i in range(1, 8)],
    )
