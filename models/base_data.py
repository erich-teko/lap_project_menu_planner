from sqlmodel import Session, select

from db_engin import engine
from models.menu_planner import EffortLevel, MenuCategory, Season, WeekDay


def create_effort_levels():
    with Session(engine) as session:
        if session.exec(select(EffortLevel)).first():
            return  # Effort levels already exist, no need to create them again
        effort_levels = [
            ("schnell", "Aufwand bis zu 30 Minuten", 1),
            ("mittel", "Aufwand über 30 bis zu 60 Minuten", 2),
            ("aufwendig", "Aufwand über 60 Minuten", 3),
        ]
        for name, description, effort_level_number in effort_levels:
            effort_level = EffortLevel(name=name, description=description, effort_level_number=effort_level_number)
            session.add(effort_level)
        session.commit()


def create_recipe_categories():
    with Session(engine) as session:
        if session.exec(select(MenuCategory)).first():
            return  # Recipe categories already exist, no need to create them again
        categories = [
            "Pastagericht",
            "Reisgericht",
            "Salat",
            "Suppen",
            "Eintopf",
            "Fleischgericht",
            "Vegetarisch",
            "Vegan",
        ]
        for name in categories:
            category = MenuCategory(name=name)
            session.add(category)
        session.commit()


def create_seasons():
    with Session(engine) as session:
        if session.exec(select(Season)).first():
            return  # Seasons already exist, no need to create them again
        # Meteorological seasons in the northern hemisphere
        seasons = [
            ("Frühling", 1, "März bis Mai"),
            ("Sommer", 2, "Juni bis August"),
            ("Herbst", 3, "September bis November"),
            ("Winter", 4, "Dezember bis Februar"),
        ]
        for name, season_number, description in seasons:
            season = Season(name=name, season_number=season_number, description=description)
            session.add(season)
        session.commit()


def create_week_days():
    with Session(engine) as session:
        if session.exec(select(WeekDay)).first():
            return  # Week days already exist, no need to create them again
        week_days = [
            ("Montag", 1),
            ("Dienstag", 2),
            ("Mittwoch", 3),
            ("Donnerstag", 4),
            ("Freitag", 5),
            ("Samstag", 6),
            ("Sonntag", 7),
        ]
        for name, week_day_number in week_days:
            week_day = WeekDay(name=name, week_day_number=week_day_number)
            session.add(week_day)
        session.commit()


def initialize_database():
    create_effort_levels()
    create_recipe_categories()
    create_seasons()
    create_week_days()
