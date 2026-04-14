"""
Protected API routes for model training and prediction.

The endpoints in this router require a valid JWT token. The authenticated
username is taken from the token, so the client does not manually choose the
model file name. Each user trains and predicts with a personal model file.
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from auth import get_current_user
from model import predict_from_model, train_and_save_model


router = APIRouter(tags=["Model"])
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)


class TrainRequest(BaseModel):
    """
    Request body for training a polynomial regression model.

    The frontend sends capital X and Y, while Swagger/manual testing may use
    lowercase x and y. This class supports both formats.
    """

    X: list[float] | None = None
    Y: list[float] | None = None
    x: list[float] | None = None
    y: list[float] | None = None
    degree: int = Field(default=3, ge=1, le=10)

    def get_x_values(self) -> list[float]:
        """
        Return X values from either X or x.
        """
        return self.X if self.X is not None else self.x

    def get_y_values(self) -> list[float]:
        """
        Return Y values from either Y or y.
        """
        return self.Y if self.Y is not None else self.y


def train_model_logic(data: TrainRequest, current_user: dict):
    """
    Train and save a personal model for the authenticated user.
    """
    x_values = data.get_x_values()
    y_values = data.get_y_values()

    if x_values is None or y_values is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X/Y values. Send X and Y arrays.",
        )

    if len(x_values) != len(y_values):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X and Y must have the same length",
        )

    user_name = current_user["user_name"]
    model_path = MODELS_DIR / f"{user_name}.pkl"

    training_hours = [[value] for value in x_values]
    running_times = y_values

    try:
        train_and_save_model(
            training_hours=training_hours,
            running_times=running_times,
            model_name=str(model_path),
            degree=data.degree,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {exc}",
        ) from exc

    return {
        "message": "Model trained successfully",
        "user_name": user_name,
        "model_file": model_path.name,
        "degree": data.degree,
        "samples": len(x_values),
    }


def predict_logic(hours: float, current_user: dict):
    """
    Predict running time using the authenticated user's saved model.
    """
    user_name = current_user["user_name"]
    model_path = MODELS_DIR / f"{user_name}.pkl"

    if not model_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model file does not exist. Train the model first.",
        )

    try:
        prediction = predict_from_model(str(model_path), hours)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        ) from exc

    return {
        "message": "Prediction completed successfully",
        "user_name": user_name,
        "hours": hours,
        "prediction": prediction,
        "predicted_running_time": prediction,
    }


@router.post("/train")
def train_model_lowercase(
    data: TrainRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Lowercase train endpoint used by the HTML page.
    """
    return train_model_logic(data, current_user)


@router.post("/TRAIN")
def train_model_uppercase(
    data: TrainRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Uppercase train endpoint required by the assignment.
    """
    return train_model_logic(data, current_user)


@router.get("/predict/{hours}")
def predict_lowercase(
    hours: float,
    current_user: dict = Depends(get_current_user),
):
    """
    Lowercase predict endpoint used by the HTML page.
    """
    return predict_logic(hours, current_user)


@router.get("/PREDICT/{hours}")
def predict_uppercase(
    hours: float,
    current_user: dict = Depends(get_current_user),
):
    """
    Uppercase predict endpoint required by the assignment.
    """
    return predict_logic(hours, current_user)