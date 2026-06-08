import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

from ai_decision_engine.api.models import QueryRequest, QueryResponse  # noqa: E402
from ai_decision_engine.pipeline.router import REGISTERED_DOMAINS, detect_domain  # noqa: E402
from ai_decision_engine.state import DecisionState  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    from ai_decision_engine.pipeline.graph import pipeline  # warm import at startup
    app.state.pipeline = pipeline
    yield


app = FastAPI(
    title="AI Decision Engine",
    description="Multi-domain AI pipeline: CardDeals, HireStream, Lead Finder, Travel Planner",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok", "domains": REGISTERED_DOMAINS}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    domain = request.domain

    if domain == "auto":
        domain = detect_domain(request.input)

    if domain not in REGISTERED_DOMAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown domain '{domain}'. Valid: {REGISTERED_DOMAINS}",
        )

    user_input = request.input
    if request.modality == "audio":
        if not request.audio_path:
            raise HTTPException(status_code=400, detail="audio_path required when modality='audio'")
        try:
            from ai_decision_engine.stt import WhisperSTTProvider
            stt = WhisperSTTProvider()
            user_input = stt.transcribe(request.audio_path)
        except ImportError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"STT not available: {exc}. Install with: pip install 'ai-decision-engine[stt]'",
            ) from exc

    initial_state = DecisionState(input=user_input, domain=domain)

    start = time.perf_counter()
    final_state = app.state.pipeline.invoke(initial_state)
    elapsed = time.perf_counter() - start

    return QueryResponse(
        domain=domain,
        intent=final_state["intent"],
        entities=final_state["entities"],
        candidates_count=len(final_state["candidates"]),
        ranked=final_state["ranked"],
        final_response=final_state["final_response"],
        latency_seconds=round(elapsed, 3),
    )
