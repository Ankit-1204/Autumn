import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis
from settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws/runs/{run_id}")
async def ws_run_updates(websocket: WebSocket, run_id: int):
    """
    WebSocket endpoint to stream run updates.
    Each connected client subscribes to Redis channel `run:{run_id}` and receives JSON messages.
    """
    await websocket.accept()
    redis = aioredis.from_url(settings.REDIS_URL)
    pubsub = redis.pubsub()
    channel = f"run:{run_id}"
    await pubsub.subscribe(channel)
    logger.info("WebSocket connected for run %s", run_id)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = message["data"]
                if isinstance(data, (bytes, bytearray)):
                    text = data.decode()
                else:
                    text = str(data)
                # forward message to websocket client
                try:
                    await websocket.send_text(text)
                except Exception:
                    # client disconnected (send failed)
                    raise WebSocketDisconnect()
            # small sleep to allow event loop to handle client messages/pings
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for run %s", run_id)
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await redis.close()
        except Exception:
            pass