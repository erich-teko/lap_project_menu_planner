from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db_engin import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (if needed)


menu_planner = FastAPI(lifespan=lifespan)
menu_planner.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@menu_planner.get("/", response_class=HTMLResponse, name="home")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
