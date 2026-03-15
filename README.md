# FastAPI assignment app

A FastAPI application with endpoints for health checks, text summarization, and sentiment analysis. Designed for deployment on [Render](https://render.com) for the AI Internship Bootcamp assignment.

## Features / Endpoints

- `GET /health`  
  Returns JSON with:
  - `status`: `"healthy"`
  - `timestamp`: current UTC ISO 8601 timestamp.

- `POST /summarize`  
  Request body:
  ```json
  {
    "text": "Long text to summarize...",
    "max_length": 100
  }
  ```
  Response body:
  ```json
  {
    "summary": "Short summary text..."
  }
  ```
  Uses a small summarization model (`sshleifer/distilbart-cnn-12-6`) suitable for Render’s free tier. The internal instruction/prompt template is defined in code so you can easily swap between different variants for your assignment.

- `POST /analyze-sentiment`  
  Request body:
  ```json
  {
    "text": "Some opinionated text..."
  }
  ```
  Response body:
  ```json
  {
    "sentiment": "positive | negative | neutral",
    "confidence": 0.93,
    "explanation": "Brief natural-language explanation..."
  }
  ```
  Uses `distilbert-base-uncased-finetuned-sst-2-english` under the hood, with an explanation string constructed from a prompt-style template so you can experiment with different instructions.

## Local development

From the project root:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:

- Docs UI: http://127.0.0.1:8000/docs  
- Root: http://127.0.0.1:8000/

## Deploy on Render

You can either configure the service in the Render dashboard or use the included `render.yaml` Blueprint.

1. Push this folder to a Git repo (GitHub, GitLab, etc.).
2. In Render: **New** → **Web Service**, connect the repo, and choose the directory that contains `main.py`, `requirements.txt`, and (optionally) `render.yaml`.
3. Use:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT`
4. Deploy. Render will set the `PORT` environment variable automatically.

After deployment, you can hit the same endpoints:

- `GET /health`
- `POST /summarize`
- `POST /analyze-sentiment`

