import hashlib
import json
import logging
import os

import redis.asyncio as redis

logger = logging.getLogger(__name__)

MODEL_VERSION = "v1"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_timeout=1.0,
    socket_connect_timeout=1.0,
)


def cache_key(input_data: list[float]) -> str:
    input_str = json.dumps(input_data, sort_keys=True)
    hash_input = hashlib.md5(input_str.encode()).hexdigest()
    return f"pred:{MODEL_VERSION}:{hash_input}"


async def cache_prediction(input_data: list[float], predictions: list[float]) -> None:
    try:
        key = cache_key(input_data)
        await redis_client.set(key, json.dumps(predictions), ex=3600)
    except Exception as e:
        logger.warning(f"Redis cache write failed: {e}. Proceeding without caching.")


async def get_cached_prediction(input_data: list[float]) -> list[float] | None:
    try:
        key = cache_key(input_data)
        cached_value = await redis_client.get(key)
        if cached_value is not None:
            return json.loads(cached_value)
    except Exception as e:
        logger.warning(f"Redis cache lookup failed: {e}. Falling back to model inference.")
    return None

