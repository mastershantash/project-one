import json
import logging
import os

import numpy as np
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .model import get_model, predict

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
INFERENCE_REQUESTS_TOPIC = os.getenv("INFERENCE_REQUESTS_TOPIC", "inference-requests")
INFERENCE_RESULTS_TOPIC = os.getenv("INFERENCE_RESULTS_TOPIC", "inference-results")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "ml-serving-capstone")


async def run_worker() -> None:
    logger.info(f"Connecting Kafka worker to {KAFKA_BOOTSTRAP_SERVERS}...")
    consumer = AIOKafkaConsumer(
        INFERENCE_REQUESTS_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
    )
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await consumer.start()
    await producer.start()
    try:
        logger.info(f"Listening for inference requests on '{INFERENCE_REQUESTS_TOPIC}'...")
        async for msg in consumer:
            request = json.loads(msg.value)
            model = get_model()
            X_new = np.array(request["input_data"]).reshape(-1, 1)
            prediction = predict(model, X_new).tolist()
            result = json.dumps({"id": request["id"], "predictions": prediction})
            await producer.send_and_wait(INFERENCE_RESULTS_TOPIC, result.encode())
    finally:
        await consumer.stop()
        await producer.stop()

