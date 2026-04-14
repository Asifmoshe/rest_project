from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from auth import get_current_user
from model import train_and_save_model, predict_from_model

router = APIRouter(tags=["Model"])

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

class TrainRequest(BaseModel):
    x: list[float] = Field(..., min_length=1, description="Feature values")
    y: list[float] = Field(..., min_length=1, description="Target values")
    degree: int = Field(default=3, ge=1, le=10)

@router.post("/TRAIN")
def train_model(data: TrainRequest, current_user: dict = Depends(get_current_user)):
    if len(data.x) != len(data.y):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="x and y must have the same length",
        )

    user_name = current_user["user_name"]
    model_path = MODELS_DIR / f"{user_name}.pkl"

    training_hours = [[value] for value in data.x]
    running_times = data.y

    try:
        train_and_save_model(
            training_hours=training_hours,
            running_times=running_times,
            model_name=str(model_path),
            degree=data.degree,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
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
        "samples": len(data.x),
    }

@router.get("/PREDICT/{hours}")
def predict(hours: float, current_user: dict = Depends(get_current_user)):
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
        "user_name": user_name,
        "hours": hours,
        "predicted_running_time": float(prediction),
    }