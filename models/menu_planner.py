from typing import Optional

from sqlmodel import Field, SQLModel


class EffortLevel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None


class MenuCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None


class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    season_number: int = Field(unique=True)
    description: Optional[str] = None


class Menu(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="menucategory.id")
    effort_level_id: Optional[int] = Field(default=None, foreign_key="effortlevel.id")
    to_take_away: bool = False
    protein: float


class MenuSeasonLink(SQLModel, table=True):
    menu_id: Optional[int] = Field(default=None, foreign_key="menu.id", primary_key=True)
    season_id: Optional[int] = Field(default=None, foreign_key="season.id", primary_key=True)
