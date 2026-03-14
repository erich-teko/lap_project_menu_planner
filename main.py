from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from db_engin import (
    create_db_and_tables,
    create_menu,
    get_all_effort_levels,
    get_all_menu_categories,
    get_all_seasons,
    get_all_week_days,
    get_last_weeks_menus,
    get_menu_collection,
    get_menus_with_details,
    get_planner_result_by_year_and_week,
    import_example_menu_collection,
    save_week_planner_result,
)
from exceptions import WeekPlannerSaveException
from models.api_models import DaySettings, MenuInfo, WeekPlannerResult, WeekPlannerSettings, create_default_week_planner
from models.base_data import initialize_database
from models.db_models import Menu
from planner.week_planner import WeekMenuPlanner


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    initialize_database()
    yield
    # Shutdown (if needed)


menu_planner = FastAPI(lifespan=lifespan)

# Add ProxyHeadersMiddleware to trust X-Forwarded-* headers from nginx
menu_planner.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

menu_planner.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@menu_planner.get("/", response_class=HTMLResponse, name="home")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@menu_planner.get("/menu-collection", response_class=HTMLResponse, name="menu_collection")
async def menu_collection(request: Request):
    menus = get_menus_with_details()
    categories = get_all_menu_categories()
    effort_levels = get_all_effort_levels()
    seasons = get_all_seasons()

    return templates.TemplateResponse(
        "menu_collection.html",
        {
            "request": request,
            "menus": menus,
            "categories": categories,
            "effort_levels": effort_levels,
            "seasons": seasons,
        },
    )


@menu_planner.post("/api/menus", status_code=status.HTTP_201_CREATED)
async def create_menu_api(menu_data: MenuInfo):
    menu = Menu(
        name=menu_data.name,
        description=menu_data.description,
        category_id=menu_data.category_id,
        effort_level_id=menu_data.effort_level_id,
        to_take_away=menu_data.to_take_away,
        protein=menu_data.protein,
    )

    try:
        created_menu = create_menu(menu, menu_data.season_ids)
        return {"id": created_menu.id, "name": created_menu.name}
    except ValueError as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception))


@menu_planner.get("/week-planner", response_class=HTMLResponse, name="week_planner")
async def week_planner_page(request: Request):
    week_planner_default = create_default_week_planner()
    effort_levels = get_all_effort_levels()
    week_days = get_all_week_days()

    # Convert SQLModel objects to dictionaries for JSON serialization
    week_days_dict = [day.model_dump() for day in week_days]

    return templates.TemplateResponse(
        "week_planner.html",
        {
            "request": request,
            "default_year": week_planner_default.year,
            "default_week": week_planner_default.week_number,
            "default_protein_goal": week_planner_default.protein_goal,
            "effort_levels": effort_levels,
            "week_days": week_days_dict,
        },
    )


@menu_planner.post("/api/week-planner/start-planning")
async def create_week_planner_api(planner_settings: WeekPlannerSettings):
    # Convert Pydantic models to dataclass instances
    daily_menus = []
    for day_settings in planner_settings.daily_settings:
        daily_menus.append(
            DaySettings(
                week_day_number=day_settings.week_day_number,
                effort_level_id=day_settings.effort_level_id,
                to_take_away=day_settings.to_take_away,
            )
        )

    week_planner = WeekPlannerSettings(
        year=planner_settings.year,
        week_number=planner_settings.week_number,
        protein_goal=planner_settings.protein_goal,
        daily_settings=daily_menus,
    )

    menus = get_menu_collection()
    used_menu_ids = get_last_weeks_menus(4)
    week_menu_planner = WeekMenuPlanner(menus, week_planner, used_menu_ids)
    week_planner_result = week_menu_planner.plan_week_menus()
    if not week_planner_result:
        message = """\
            Es konnte keine gültige Menüplanung gefunden werden.
            Bitte passen Sie Ihre Einstellungen an und versuchen Sie es erneut.
        """
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return _extend_week_planner_result_for_display(week_planner_result)


@menu_planner.post("/api/menus/import", status_code=status.HTTP_201_CREATED)
async def import_menus():
    try:
        imported_count = import_example_menu_collection("example/menu_collection.json")
        return {"imported_menus": imported_count}
    except (FileNotFoundError, ValueError, ValueError) as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception))


@menu_planner.post("/api/week-planner", status_code=status.HTTP_201_CREATED)
async def save_planned_week(week_planner_result: WeekPlannerResult):
    try:
        save_week_planner_result(week_planner_result)
    except WeekPlannerSaveException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception))


@menu_planner.get("/api/week-planner/{year}/{week_number}")
async def get_planner_result(year: int, week_number: int):
    week_planner_result = get_planner_result_by_year_and_week(year, week_number)
    if not week_planner_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Keine Planung für die angegebene Woche gefunden."
        )
    return _extend_week_planner_result_for_display(week_planner_result)


def _extend_week_planner_result_for_display(week_planner_result: WeekPlannerResult) -> dict[str, Any]:
    week_planner_result_dict = week_planner_result.model_dump()
    effort_levels = get_all_effort_levels()

    for day_menu in week_planner_result_dict["daily_menus"]:
        effort_level = next((level for level in effort_levels if level.id == day_menu["effort_level_id"]), None)
        day_menu["effort_level_name"] = effort_level.name if effort_level else "-"

    return week_planner_result_dict
