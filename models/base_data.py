from sqlmodel import Session, select

from db_engin import engine
from models.menu_planner import EffortLevel, RecipeCategory, Season


def create_effort_levels():
    with Session(engine) as session:
        if session.exec(select(EffortLevel)).first():
            return  # Effort levels already exist, no need to create them again
        effort_levels = [
            ("schnell", "Aufwand bis zu 30 Minuten"),
            ("mittel", "Aufwand über 30 bis zu 60 Minuten"),
            ("aufwendig", "Aufwand über 60 Minuten"),
        ]
        for name, description in effort_levels:
            effort_level = EffortLevel(name=name, description=description)
            session.add(effort_level)
        session.commit()


def create_recipe_categories():
    with Session(engine) as session:
        if session.exec(select(RecipeCategory)).first():
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
            category = RecipeCategory(name=name)
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


def initialize_database():
    create_effort_levels()
    create_recipe_categories()
    create_seasons()
