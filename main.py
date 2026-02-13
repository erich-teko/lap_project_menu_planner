from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from db_engin import (
    create_db_and_tables,
    create_menu,
    get_all_effort_levels,
    get_all_menu_categories,
    get_all_seasons,
    get_menus_with_details,
)
from models.base_data import initialize_database
from models.menu_planner import Menu
from planner.planner_models import DayMenu, EffortLevel, WeekPlanner


class MenuCreate(BaseModel):
    name: str
    description: str | None = None
    category_id: int | None = None
    effort_level_id: int | None = None
    to_take_away: bool = False
    protein: float
    season_ids: list[int]


class DayMenuCreate(BaseModel):
    week_day_number: int
    effort_level: int | None = None
    to_take_away: bool = False
    menu_id: int | None = None


class WeekPlannerCreate(BaseModel):
    year: int
    week_number: int
    protein_goal: float
    daily_menus: list[DayMenuCreate]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    initialize_database()
    yield
    # Shutdown (if needed)


menu_planner = FastAPI(lifespan=lifespan)
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


@menu_planner.post("/api/menus")
async def create_menu_api(menu_data: MenuCreate):
    menu = Menu(
        name=menu_data.name,
        description=menu_data.description,
        category_id=menu_data.category_id,
        effort_level_id=menu_data.effort_level_id,
        to_take_away=menu_data.to_take_away,
        protein=menu_data.protein,
    )
    
    created_menu = create_menu(menu, menu_data.season_ids)
    return {"id": created_menu.id, "name": created_menu.name}


@menu_planner.get("/week-planner", response_class=HTMLResponse, name="week_planner")
async def week_planner_page(request: Request):
    now = datetime.now()
    current_year, current_week, _ = now.isocalendar()
    
    return templates.TemplateResponse(
        "week_planner.html",
        {
            "request": request,
            "default_year": current_year,
            "default_week": current_week + 1,  # Next week
        },
    )


@menu_planner.post("/api/week-planner")
async def create_week_planner_api(planner_data: WeekPlannerCreate):
    # Convert Pydantic models to dataclass instances
    daily_menus = []
    for day in planner_data.daily_menus:
        effort_level_enum: EffortLevel | None = None
        if day.effort_level is not None:
            effort_level_enum = EffortLevel(day.effort_level)
        
        daily_menus.append(
            DayMenu(
                week_day_number=day.week_day_number,
                effort_level=effort_level_enum,
                to_take_away=day.to_take_away,
                menu_id=day.menu_id,
            )
        )
    
    week_planner = WeekPlanner(
        year=planner_data.year,
        week_number=planner_data.week_number,
        protein_goal=planner_data.protein_goal,
        daily_menus=daily_menus,
    )
    
    # Here you would typically save the week planner to a database
    # For now, just return the created planner data
    return {
        "year": week_planner.year,
        "week_number": week_planner.week_number,
        "protein_goal": week_planner.protein_goal,
        "daily_menus_count": len(week_planner.daily_menus),
    }


