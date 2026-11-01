import asyncio
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
    consumer = None
    producer = None

    # Resilient retry loop with backoff for cluster cold-starts
    while True:
        try:
            consumer = AIOKafkaConsumer(
                INFERENCE_REQUESTS_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=KAFKA_GROUP_ID,
            )
            producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
            await consumer.start()
            await producer.start()
            logger.info(f"Connected to Kafka! Listening on '{INFERENCE_REQUESTS_TOPIC}'...")
            break
        except Exception as e:
            logger.warning(f"Kafka not ready ({e}). Retrying in 5 seconds...")
            if consumer:
                await consumer.stop()
            if producer:
                await producer.stop()
            await asyncio.sleep(5)

    try:
        async for msg in consumer:
            try:
                request = json.loads(msg.value)
                model = get_model()
                X_new = np.array(request["input_data"]).reshape(-1, 1)
                prediction = predict(model, X_new).tolist()
                result = json.dumps({"id": request.get("id"), "predictions": prediction})
                await producer.send_and_wait(INFERENCE_RESULTS_TOPIC, result.encode())
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    finally:
        logger.info("Stopping Kafka consumer and producer...")
        if consumer:
            await consumer.stop()
        if producer:
            await producer.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    asyncio.run(run_worker())
