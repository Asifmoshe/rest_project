"""
Machine-learning helpers for polynomial regression.

This module trains a polynomial regression model for running-time prediction,
saves the trained model to disk, and loads saved models to make predictions.
The API layer calls these functions from protected endpoints.
"""

import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures


def train_and_save_model(
    training_hours,
    running_times,
    model_name: str,
    degree: int = 3,
) -> Pipeline:
    """
    Train a polynomial regression model and save it to a file.

    Args:
        training_hours: Feature values used for training. The expected shape is
            a two-dimensional structure such as ``[[2], [4], [6]]``.
        running_times: Target values that match the training-hours samples.
        model_name: File path where the trained model should be saved.
        degree: Polynomial degree used by ``PolynomialFeatures``.

    Raises:
        ValueError: If ``training_hours`` and ``running_times`` do not contain
            the same number of samples.

    Returns:
        Pipeline: The trained scikit-learn pipeline.
    """
    if len(training_hours) != len(running_times):
        raise ValueError("training_hours and running_times must have same length")

    model = Pipeline(
        [
            ("poly", PolynomialFeatures(degree=degree)),
            ("linear", LinearRegression()),
        ]
    )

    model.fit(training_hours, running_times)
    joblib.dump(model, model_name)
    return model


def predict_from_model(model_name: str, hours_value: float) -> float:
    """
    Load a saved model and predict the running time for a new input value.

    Args:
        model_name: File path of the saved model file.
        hours_value: Number of training hours used as the prediction input.

    Returns:
        float: Predicted running time.
    """
    model = joblib.load(model_name)
    x_new = np.array([[hours_value]])
    prediction = model.predict(x_new)
    return float(prediction[0])


if __name__ == "__main__":
    training_hours = np.array([2, 3, 5, 7, 9, 12, 16, 20, 25, 30]).reshape(-1, 1)
    running_times = np.array([95, 85, 70, 65, 60, 55, 50, 53, 58, 70])

    train_and_save_model(training_hours, running_times, "running_model.pkl", degree=3)
    result = predict_from_model("running_model.pkl", 15)
    print(f"Predicted running time for 15 training hours: {result}")