from functools import lru_cache

import numpy as np
from sklearn.linear_model import LinearRegression


def predict(model: LinearRegression, X_new: np.ndarray) -> np.ndarray:
    """
    Make predictions using the trained linear regression model.

    Parameters:
    model (LinearRegression): Trained linear regression model.
    X_new (array-like): New input data for prediction.

    Returns:
    np.ndarray: Predicted values for the input data.
    """
    return model.predict(X_new)  # Make predictions


def evaluate_model(
    model: LinearRegression, X_test: np.ndarray, y_test: np.ndarray
) -> float:
    """
    Evaluate the trained linear regression model on test data.

    Parameters:
    model (LinearRegression): Trained linear regression model.
    X_test (array-like): Feature matrix for testing.
    y_test (array-like): Target vector for testing.

    Returns:
    float: R^2 score of the model on the test data.
    """
    return float(model.score(X_test, y_test))


@lru_cache
def get_model() -> LinearRegression:
    X = np.array([[1], [2], [3], [4]])
    y = np.array([2, 4, 6, 8])
    model = LinearRegression()
    model.fit(X, y)  # training happens here, guaranteed, before anyone gets the model
    return model
