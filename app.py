"""
FastAPI application entry point for the REST ML project.

This file starts the API, creates the users table, creates the models folder,
registers all routers, and serves the HTML pages.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import dal_users
from router_model import router as model_router
from router_users import router as users_router


app = FastAPI(title="Running Time Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
MODELS_DIR = Path("models")


@app.on_event("startup")
def startup() -> None:
    """
    Prepare the database and models folder when the server starts.
    """
    dal_users.create_table_users()
    MODELS_DIR.mkdir(exist_ok=True)


app.include_router(users_router)
app.include_router(model_router)


@app.get("/")
def home():
    """
    Redirect the home page to the users page.
    """
    return RedirectResponse("/users.html")


@app.get("/health")
def health():
    """
    Return API health status.
    """
    return {"status": "online"}


@app.get("/users-page")
@app.get("/users.html")
def users_page(request: Request):
    """
    Render the user-management page.
    """
    return templates.TemplateResponse("users.html", {"request": request})


@app.get("/model-page")
@app.get("/model")
@app.get("/model.html")
def model_page(request: Request):
    """
    Render the model training and prediction page.
    """
    return templates.TemplateResponse("model.html", {"request": request})