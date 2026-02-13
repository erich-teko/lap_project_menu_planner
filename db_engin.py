from sqlmodel import Session, SQLModel, create_engine, select

from models.menu_planner import *

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
