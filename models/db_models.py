from sqlmodel import Field, SQLModel


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
