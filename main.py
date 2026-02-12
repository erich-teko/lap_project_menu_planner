from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

menu_planner = FastAPI()
menu_planner.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@menu_planner.get("/", response_class=HTMLResponse, name="home")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
