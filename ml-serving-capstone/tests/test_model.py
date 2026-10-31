import numpy as np
import pytest

from ml_serving_capstone.model import get_model, predict


def test_get_model_returns_trained_model():
    model = get_model()
    assert model.coef_[0] == pytest.approx(2.0, abs=0.01)


def test_predict_matches_expected_pattern():
    model = get_model()
    X_new = np.array([[5]])
    result = predict(model, X_new)
    assert result[0] == pytest.approx(10.0, abs=0.1)
