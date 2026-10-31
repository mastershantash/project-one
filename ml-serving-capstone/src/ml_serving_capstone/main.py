import json
import logging
import time

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

from .model import get_model, predict
from .redis_cache import MODEL_VERSION, cache_prediction, get_cached_prediction

logger = logging.getLogger("ml_serving")
logging.basicConfig(level=logging.INFO, format="%(message)s")


class PredictRequest(BaseModel):
    """
    Request model for prediction endpoint.
    """

    input_data: list[float]  # List of input features for prediction


class PredictResponse(BaseModel):
    """
    Response model for prediction endpoint.
    """

    predictions: list[float]  # List of predicted values


app = FastAPI(title="ML Serving Capstone API", version="0.1.0")


@app.get("/healthz")
async def healthz():
    """
    Kubernetes Liveness Probe: Checks if the service is running.
    """
    return {"status": "healthy"}


@app.get("/readyz")
async def readyz():
    """
    Kubernetes Readiness Probe: Checks if model is loaded and ready for traffic.
    """
    try:
        model = get_model()
        if model is None:
            return {"status": "not_ready", "reason": "model not loaded"}, 503
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}, 503


@app.post("/predict", response_model=PredictResponse)
async def predict_endpoint(request: PredictRequest):
    """
    Endpoint to make predictions using the trained linear regression model.

    Parameters:
    request (PredictRequest): Request body containing input features.

    Returns:
    PredictResponse: Response containing predicted values.
    """
    start_time = time.perf_counter()
    cached_predictions = await get_cached_prediction(
        request.input_data
    )  # Check for cached predictions
    if cached_predictions is not None:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            json.dumps(
                {
                    "event": "model_inference",
                    "model_version": MODEL_VERSION,
                    "cache_hit": True,
                    "latency_ms": latency_ms,
                    "input_features": request.input_data,
                    "predictions": cached_predictions,
                }
            )
        )
        return PredictResponse(
            predictions=cached_predictions
        )  # Return cached predictions if available

    model = get_model()  # Get the trained model
    X_new = np.array(request.input_data).reshape(
        -1, 1
    )  # Reshape input data for prediction
    predictions = predict(model, X_new)  # Make predictions
    await cache_prediction(
        request.input_data, predictions.tolist()
    )  # Cache the predictions

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "event": "model_inference",
                "model_version": MODEL_VERSION,
                "cache_hit": False,
                "latency_ms": latency_ms,
                "input_features": request.input_data,
                "predictions": predictions.tolist(),
            }
        )
    )
    return PredictResponse(
        predictions=predictions.tolist()
    )  # Return predictions as a list
