<<<<<<< HEAD
# https-github.com-AEverette01-fastapi-assignment.git-.
A FastAPI application with endpoints for health checks, text summarization, and sentiment analysis. Deployed on Render for [AI Internship Bootcamp]
=======
# FastAPI project for Render

Minimal FastAPI app set up for deployment on [Render](https://render.com).

## Local development

```bash
cd fastapi-project
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs for the API docs.

## Deploy on Render

1. Push this folder to a Git repo (or use Render’s GitHub integration).
2. In Render: **New** → **Web Service**, connect the repo, choose the directory that contains `main.py` and `requirements.txt`.
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT`
5. Deploy. Render sets `PORT` automatically.

Or use the included `render.yaml` as a Blueprint to create the service from the repo.

## Endpoints

- `GET /` – Hello message
- `GET /health` – Health check (for Render/liveness)
>>>>>>> cbe0a38 (Add requirements file)
