import base64
import json
import logging
import os
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")


def _post_slack(message: str) -> None:
    if not SLACK_WEBHOOK_URL:
        return
    payload: Dict[str, Any] = {"text": message}
    if SLACK_CHANNEL:
        payload["channel"] = SLACK_CHANNEL
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        if resp.status_code >= 400:
            logger.error("Slack webhook returned %s: %s", resp.status_code, resp.text)
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to post to Slack: %s", exc)


def handle_movie_event(event, context) -> None:
    """
    Pub/Sub-triggered Cloud Function for MS2 movie events.
    Expects messages like:
    {
      "event": "movie.created" | "movie.updated",
      "movie": { "id": ..., "title": ..., "genre": ..., "year": ... }
    }
    """
    try:
        raw = event.get("data")
        if not raw:
            logger.warning("Received Pub/Sub message without data")
            return

        decoded = base64.b64decode(raw).decode("utf-8")
        payload = json.loads(decoded)
        evt = payload.get("event") or "unknown"
        movie = payload.get("movie") or {}

        msg = (
            f"MS2 movie event: {evt}\n"
            f"- ID: {movie.get('id')}\n"
            f"- Title: {movie.get('title')}\n"
            f"- Genre: {movie.get('genre')}\n"
            f"- Year: {movie.get('year')}\n"
            f"- Version: {movie.get('version')}\n"
            f"- Processing: {movie.get('processing_status')}"
        )
        logger.info(msg)
        _post_slack(msg)
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to process movie event: %s", exc)
