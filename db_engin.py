from sqlmodel import Session, SQLModel, create_engine, select

from models.api_models import MenuInfo
from models.db_models import *

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_all_effort_levels() -> list[EffortLevel]:
    with Session(engine) as session:
        effort_levels = session.exec(select(EffortLevel).order_by(EffortLevel.id)).all()
        return effort_levels


def get_all_menu_categories() -> list[MenuCategory]:
    with Session(engine) as session:
        menu_categories = session.exec(select(MenuCategory).order_by(MenuCategory.name)).all()
        return menu_categories


def get_all_seasons() -> list[Season]:
    with Session(engine) as session:
        seasons = session.exec(select(Season).order_by(Season.season_number)).all()
        return seasons


def get_all_week_days() -> list[WeekDay]:
    with Session(engine) as session:
        week_days = session.exec(select(WeekDay).order_by(WeekDay.week_day_number)).all()
        return week_days


def get_menu_collection() -> list[MenuInfo]:
    with Session(engine) as session:
        menus = session.exec(select(Menu)).all()
        menu_seasons = session.exec(select(MenuSeasonLink)).all()
        menu_collection = []
        for menu in menus:
            season_ids = [season.season_id for season in menu_seasons if season.menu_id == menu.id]
            menu_info = MenuInfo(
                id=menu.id,
                name=menu.name,
                category_id=menu.category_id,
                effort_level_id=menu.effort_level_id,
                to_take_away=menu.to_take_away,
                protein=menu.protein,
                season_ids=season_ids,
            )
            menu_collection.append(menu_info)
        return menu_collection


def get_menues(limit: int = 20) -> list[Menu]:
    with Session(engine) as session:
        menues = session.exec(select(Menu).order_by(Menu.name).limit(limit)).all()
        return menues


def create_menu(menu: Menu, season_ids: list[int]) -> Menu:
    with Session(engine) as session:
        session.add(menu)
        session.commit()

        if menu.id:
            for season_id in season_ids:
                menu_season_link = MenuSeasonLink(menu_id=menu.id, season_id=season_id)
                session.add(menu_season_link)
            session.commit()
        session.refresh(menu)
        return menu


def get_menus_with_details() -> list[dict]:
    """Get all menus with their related category, effort level, and season information."""
    with Session(engine) as session:
        menus = session.exec(select(Menu).order_by(Menu.name)).all()
        result = []

        for menu in menus:
            # Get category name
            category_name = None
            if menu.category_id:
                category = session.get(MenuCategory, menu.category_id)
                if category:
                    category_name = category.name

            # Get effort level name
            effort_name = None
            if menu.effort_level_id:
                effort = session.get(EffortLevel, menu.effort_level_id)
                if effort:
                    effort_name = effort.name

            # Get season names
            season_links = session.exec(select(MenuSeasonLink).where(MenuSeasonLink.menu_id == menu.id)).all()
            season_names = []
            for link in season_links:
                season = session.get(Season, link.season_id)
                if season:
                    season_names.append(season.name)

            result.append(
                {
                    "id": menu.id,
                    "name": menu.name,
                    "description": menu.description,
                    "category_name": category_name,
                    "effort_name": effort_name,
                    "protein": menu.protein,
                    "to_take_away": menu.to_take_away,
                    "season_names": ", ".join(season_names) if season_names else None,
                }
            )

        return result
