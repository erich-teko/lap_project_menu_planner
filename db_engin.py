import json

from pydantic import TypeAdapter
from sqlmodel import Session, SQLModel, create_engine, select

from exceptions import WeekPlannerSaveException
from models.api_models import MenuInfo, WeekPlannerResult
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
        return list(effort_levels)


def get_all_menu_categories() -> list[MenuCategory]:
    with Session(engine) as session:
        menu_categories = session.exec(select(MenuCategory).order_by(MenuCategory.name)).all()
        return list(menu_categories)


def get_all_seasons() -> list[Season]:
    with Session(engine) as session:
        seasons = session.exec(select(Season).order_by(Season.season_number)).all()
        return list(seasons)


def get_all_week_days() -> list[WeekDay]:
    with Session(engine) as session:
        week_days = session.exec(select(WeekDay).order_by(WeekDay.week_day_number)).all()
        return list(week_days)


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


def get_last_weeks_menus(number_of_weeks: int) -> set[int]:
    with Session(engine) as session:
        menus = session.exec(
            select(DayMenuResult, WeekPlanningResult)
            .join(WeekPlanningResult)
            .order_by(WeekPlanningResult.year.desc(), WeekPlanningResult.week_number.desc())
            .limit(number_of_weeks * 7)
        )
        print(type(menus))
        return {menu.DayMenuResult.menu_id for menu in menus}


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


def import_example_menu_collection(json_file_path: str) -> int:
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
    with Session(engine) as session:
        existing_menus = session.exec(select(Menu)).all()
        menu_record_collection = []
        for menu in menu_collection:
            if any(existing_menu.name == menu.name for existing_menu in existing_menus):
                continue  # Skip if menu with the same name already exists
            menu_record = Menu(
                name=menu.name,
                description=menu.description,
                category_id=menu.category_id,
                effort_level_id=menu.effort_level_id,
                protein=menu.protein,
                to_take_away=menu.to_take_away,
                imported=True,
            )
            session.add(menu_record)
            menu_record_collection.append((menu_record, menu.season_ids))
        session.commit()

        for menu_record, season_ids in menu_record_collection:
            if menu_record.id:
                for season_id in season_ids:
                    menu_season_link = MenuSeasonLink(menu_id=menu_record.id, season_id=season_id)
                    session.add(menu_season_link)
            session.commit()

    return len(menu_record_collection)


def save_week_planner_result(week_planner_result: WeekPlannerResult):
    with Session(engine) as session:
        if session.exec(
            select(WeekPlanningResult).where(
                (WeekPlanningResult.year == week_planner_result.year)
                & (WeekPlanningResult.week_number == week_planner_result.week_number)
            )
        ).first():
            raise WeekPlannerSaveException(
                "A week planner result for the specified year and week number already exists."
            )
        week_days = session.exec(select(WeekDay)).all()
        week_day_number_to_id = {week_day.week_day_number: week_day.id for week_day in week_days}
        week_planning_result_record = WeekPlanningResult(
            year=week_planner_result.year, week_number=week_planner_result.week_number
        )
        session.add(week_planning_result_record)
        session.commit()

        if week_planning_result_record.id:
            for daily_menu_result in week_planner_result.daily_menus:
                daily_menu_result_record = DayMenuResult(
                    week_planning_result_id=week_planning_result_record.id,
                    week_day_id=week_day_number_to_id[daily_menu_result.week_day_number],
                    menu_id=daily_menu_result.menu.id,
                    effort_level_id=daily_menu_result.effort_level_id,
                    to_take_away=daily_menu_result.to_take_away,
                )
                session.add(daily_menu_result_record)
            session.commit()
