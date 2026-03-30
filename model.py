import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures


def train_and_save_model(training_hours, running_times, model_name, degree=3):
    """
    Trains a polynomial regression model and saves it

    Parameters:
        training_hours (array): X values
        running_times (array): y values
        model_name (str): file name
        degree (int): polynomial degree (default 3)

    Returns:
        trained model
    """
    if len(training_hours) != len(running_times):
        raise ValueError("training_hours and running_times must have same length")

    model = Pipeline([
        ("poly", PolynomialFeatures(degree=degree)),
        ("linear", LinearRegression())
    ])

    model.fit(training_hours, running_times)

    joblib.dump(model, model_name)
    print(f"Model saved to {model_name}")

    return model


def predict_from_model(model_name, hours_value):
    """
    Loads model and predicts running time
    """
    model = joblib.load(model_name)
    X_new = np.array([[hours_value]])
    prediction = model.predict(X_new)

    return prediction[0]


if __name__ == "__main__":
    # Your dataset
    training_hours = np.array([2, 3, 5, 7, 9, 12, 16, 20, 25, 30]).reshape(-1, 1)
    running_times = np.array([95, 85, 70, 65, 60, 55, 50, 53, 58, 70])

    # Train + save
    train_and_save_model(training_hours, running_times, "running_model.pkl", degree=3)

    # Predict example
    result = predict_from_model("running_model.pkl", 15)
    print(f"Predicted running time for 15 training hours: {result}")