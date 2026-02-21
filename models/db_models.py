from sqlmodel import Field, SQLModel, UniqueConstraint


class EffortLevel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    effort_level_number: int = Field(unique=True)
    description: str | None = None


class MenuCategory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str | None = None


class Season(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    season_number: int = Field(unique=True)
    description: str | None = None


class Menu(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str | None = None
    category_id: int = Field(foreign_key="menucategory.id")
    effort_level_id: int = Field(foreign_key="effortlevel.id")
    protein: float
    to_take_away: bool = False
    imported: bool = False


class MenuSeasonLink(SQLModel, table=True):
    menu_id: int = Field(foreign_key="menu.id", primary_key=True)
    season_id: int = Field(foreign_key="season.id", primary_key=True)


class WeekDay(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    week_day_number: int = Field(unique=True)
    icon: str | None = None

class WeekPlanningResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    year: int = Field(index=True)
    week_number: int = Field(index=True)
    __table_args__ = (
        UniqueConstraint("year", "week_number", name="unique_year_week"),
    )

class DayMenuResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    week_planning_result_id: int = Field(foreign_key="weekplanningresult.id")
    week_day_id: int = Field(foreign_key="weekday.id")
    menu_id: int = Field(foreign_key="menu.id")
    effort_level_id: int = Field(foreign_key="effortlevel.id")
    to_take_away: bool = False
