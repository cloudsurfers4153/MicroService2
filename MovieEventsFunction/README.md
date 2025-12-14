# MS2 Movie Events Cloud Function

Pub/Sub-triggered Cloud Function that consumes MS2 movie events and optionally posts to Slack.

## Deploy (example)
```bash
gcloud functions deploy ms2-movie-handler \
  --gen2 --runtime=python310 --region=us-central1 \
  --entry-point=handle_movie_event \
  --trigger-topic=ms2-movie-events \
  --source=. \
  --set-env-vars="SLACK_WEBHOOK_URL=<optional>,SLACK_CHANNEL=<optional>"
```

## Expected message payload
Published by MS2 after create/update (see `MicroService2/main.py`):
```json
{
  "event": "movie.created",
  "movie": {
    "id": 123,
    "title": "Example",
    "genre": "Drama",
    "year": 2024,
    "version": "abcd1234",
    "processing_status": "COMPLETED",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

## Configuration
- `SLACK_WEBHOOK_URL` (optional): if set, posts the event summary to Slack.
- `SLACK_CHANNEL` (optional): override target channel for the webhook.
