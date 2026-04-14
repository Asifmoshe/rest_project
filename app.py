from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import dal_users
from router_users import router as users_router
from router_model import router as model_router

"""
Application entry point for the REST ML project.

This module creates the FastAPI app, initializes required resources on startup,
registers API routers, and serves the HTML pages for the optional website UI.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import dal_users
from router_model import router as model_router
from router_users import router as users_router

app = FastAPI(title="running prediction")

templates = Jinja2Templates(directory="templates")
MODELS_DIR = Path("models")


@app.on_event("startup")
def startup() -> None:
    """
    Initialize project resources when the application starts.

    Creates the users table if it does not already exist and ensures that the
    local directory used for storing trained models is available.
    """
    dal_users.create_table_users()
    MODELS_DIR.mkdir(exist_ok=True)


app.include_router(users_router)
app.include_router(model_router)


@app.get("/")
def home() -> RedirectResponse:
    """
    Redirect the root path to the user management page.

    Returns:
        RedirectResponse: Redirects the browser to the users HTML page.
    """
    return RedirectResponse("/users-page")


@app.get("/users-page")
def users_page(request: Request):
    """
    Render the user management HTML page.

    Args:
        request (Request): The current FastAPI request object.

    Returns:
        TemplateResponse: Rendered users.html page.
    """
    return templates.TemplateResponse("users.html", {"request": request})


@app.get("/model-page")
def model_page(request: Request):
    """
    Render the model training and prediction HTML page.

    Args:
        request (Request): The current FastAPI request object.

    Returns:
        TemplateResponse: Rendered model.html page.
    """
    return templates.TemplateResponse("model.html", {"request": request})