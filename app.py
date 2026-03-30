from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import dal_users
from router_users import router as users_router
from router_model import router as model_router

app = FastAPI(title="running prediction")

templates = Jinja2Templates(directory="templates")
MODELS_DIR = Path("models")


@app.on_event("startup")
def startup():
    dal_users.create_table_users()
    MODELS_DIR.mkdir(exist_ok=True)


app.include_router(users_router)
app.include_router(model_router)


@app.get("/")
def home():
    return RedirectResponse("/users-page")


@app.get("/users-page")
def users_page(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})


@app.get("/model-page")
def model_page(request: Request):
    return templates.TemplateResponse("model.html", {"request": request})