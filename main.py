import os
from datetime import datetime, timezone
from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint
from transformers import pipeline


app = FastAPI(
    title="FastAPI Assignment App",
    description=(
        "FastAPI application with health, text summarization, and sentiment "
        "analysis endpoints, configured for Render."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Prompt / instruction templates (easy to swap for assignment) ----

SUMMARY_PROMPT_TEMPLATE = (
    "You are a concise assistant. Summarize the following text in no more than "
    "{max_length} tokens, preserving the main ideas and being factual:\n\n{text}"
)

DATA_ANALYST_SUMMARY_TEMPLATE = (
    "Act as a data analyst. Summarize the following text into a small, structured "
    "report. Highlight the main points, trends, and any notable insights. "
    "Keep it concise and under {max_length} tokens:\n\n{text}"
)

SENTIMENT_EXPLANATION_TEMPLATE = (
    "The overall sentiment is **{sentiment}** with confidence {confidence:.2f} "
    "because the text expresses the following cues: {rationale}"
)


# ---- Pydantic models ----

class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Input text to summarize")
    max_length: conint(gt=0, le=256) = Field(
        128, description="Maximum length of the summary (tokens/words approximation)"
    )


class SummarizeResponse(BaseModel):
    summary: str


class SentimentRequest(BaseModel):
    text: str = Field(..., description="Input text to analyze sentiment for")


class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    explanation: str


# ---- Lazy-loaded ML pipelines (works better on Render) ----

@lru_cache(maxsize=1)
def get_summarizer():
    """
    Load a small summarization model suitable for Render's free tier.
    Using sshleifer/distilbart-cnn-12-6 as requested.
    """
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


@lru_cache(maxsize=1)
def get_sentiment_analyzer():
    """
    Load a sentiment analysis model.
    Using distilbert-base-uncased-finetuned-sst-2-english as requested.
    """
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )


# ---- Endpoints ----

@app.get("/")
async def root():
    return {
        "message": "FastAPI assignment app is running",
        "status": "ok",
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.
    Returns a status and the current UTC timestamp in ISO 8601 format.
    """
    now = datetime.now(timezone.utc).isoformat()
    return {"status": "healthy", "timestamp": now}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(payload: SummarizeRequest):
    """
    Summarize the given text using a small transformer model.
    The instruction/prompt template can be swapped by editing SUMMARY_PROMPT_TEMPLATE.
    """
    summarizer = get_summarizer()

    prompt_text = SUMMARY_PROMPT_TEMPLATE.format(
        text=payload.text,
        max_length=payload.max_length,
    )

    # Use a safe default min_length as a fraction of max_length
    max_len = int(payload.max_length)
    min_len = max(10, max_len // 4)

    result = summarizer(
        prompt_text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
    )

    summary_text = result[0]["summary_text"] if result else ""
    return SummarizeResponse(summary=summary_text)


@app.post("/summarize-analyst", response_model=SummarizeResponse)
async def summarize_analyst(payload: SummarizeRequest):
    """
    Data-analyst-style summarization.
    Uses a different instruction template so you can A/B test prompt variations.
    """
    summarizer = get_summarizer()

    prompt_text = DATA_ANALYST_SUMMARY_TEMPLATE.format(
        text=payload.text,
        max_length=payload.max_length,
    )

    max_len = int(payload.max_length)
    min_len = max(10, max_len // 4)

    result = summarizer(
        prompt_text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
    )

    summary_text = result[0]["summary_text"] if result else ""
    return SummarizeResponse(summary=summary_text)


@app.post("/analyze-sentiment", response_model=SentimentResponse)
async def analyze_sentiment(payload: SentimentRequest):
    """
    Analyze sentiment using a DistilBERT model fine-tuned on SST-2.
    Maps scores to positive/negative/neutral and constructs a natural-language explanation
    using SENTIMENT_EXPLANATION_TEMPLATE so prompts can be swapped easily.
    """
    analyzer = get_sentiment_analyzer()
    result = analyzer(payload.text)[0]

    label = result["label"].lower()  # 'positive' or 'negative'
    score = float(result["score"])

    # Derive a neutral band from the binary model via a heuristic threshold.
    if score < 0.6:
        sentiment_label = "neutral"
    elif "positive" in label:
        sentiment_label = "positive"
    else:
        sentiment_label = "negative"

    # Simple rationale placeholder – you can refine this or swap via template.
    if sentiment_label == "positive":
        rationale = "the wording emphasizes benefits, satisfaction, or approval"
    elif sentiment_label == "negative":
        rationale = "the wording highlights problems, dissatisfaction, or criticism"
    else:
        rationale = "the wording is mixed or balanced, without strong polarity"

    explanation = SENTIMENT_EXPLANATION_TEMPLATE.format(
        sentiment=sentiment_label,
        confidence=score,
        rationale=rationale,
    )

    return SentimentResponse(
        sentiment=sentiment_label,
        confidence=score,
        explanation=explanation,
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.environ.get("ENV", "production") != "production",
    )
