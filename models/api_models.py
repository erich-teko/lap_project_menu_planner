from datetime import datetime

from pydantic import BaseModel


class DaySettings(BaseModel):
    week_day_number: int  # 1=Monday, 7=Sunday
    effort_level_id: int | None = None
    to_take_away: bool = False


class WeekPlannerSettings(BaseModel):
    year: int
    week_number: int
    protein_goal: float
    daily_menus: list[DaySettings]  # List of 7 DaySettings objects, one for each day of the week


def create_default_week_planner() -> WeekPlannerSettings:
    now = datetime.now()
    current_year, current_week, _ = now.isocalendar()
    return WeekPlannerSettings(
        year=current_year,
        week_number=current_week + 1,
        protein_goal=25.0 * 7,  # Default to 25g protein per day for a week
        daily_menus=[DaySettings(week_day_number=i) for i in range(1, 8)],
    )


class MenuInfo(BaseModel):
    name: str
    category_id: int
    effort_level_id: int
    protein: float
    season_ids: list[int]
    to_take_away: bool = False
    description: str | None = None
    id: int | None = None  # Optional ID field for existing menus


class DayMenuInfo(BaseModel):
    week_day_number: int  # 1=Monday, 7=Sunday
    menu: MenuInfo
    effort_level_id: int
    to_take_away: bool = False


class WeekPlannerResult(BaseModel):
    year: int
    week_number: int
    protein_goal: float
    daily_menus: list[DayMenuInfo]  # List of 7 DayMenuInfo objects
