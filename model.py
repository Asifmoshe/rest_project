import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

"""
Machine learning helpers for polynomial regression.

This module trains a polynomial regression model on running data, saves it to a
file, and loads it later for prediction.
"""

import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures


def train_and_save_model(training_hours, running_times, model_name, degree=3):
    """
    Train a polynomial regression model and save it to disk.

    Args:
        training_hours: Feature values (X) used for model training.
        running_times: Target values (Y) used for model training.
        model_name (str): File path for saving the trained model.
        degree (int, optional): Polynomial degree. Defaults to 3.

    Raises:
        ValueError: If X and Y do not have the same number of samples.

    Returns:
        Pipeline: Trained scikit-learn pipeline.
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
    print(f"Model saved to {model_name}")
    return model


def predict_from_model(model_name, hours_value):
    """
    Load a saved model and predict the running time for new training hours.

    Args:
        model_name (str): Path to the saved model file.
        hours_value: Training-hours value for prediction.

    Returns:
        float: Predicted running time.
    """
    model = joblib.load(model_name)
    x_new = np.array([[hours_value]])
    prediction = model.predict(x_new)
    return prediction[0]


if __name__ == "__main__":
    """
    Example local run for training and prediction testing.
    """
    training_hours = np.array([2, 3, 5, 7, 9, 12, 16, 20, 25, 30]).reshape(-1, 1)
    running_times = np.array([95, 85, 70, 65, 60, 55, 50, 53, 58, 70])

    train_and_save_model(training_hours, running_times, "running_model.pkl", degree=3)
    result = predict_from_model("running_model.pkl", 15)
    print(f"Predicted running time for 15 training hours: {result}")