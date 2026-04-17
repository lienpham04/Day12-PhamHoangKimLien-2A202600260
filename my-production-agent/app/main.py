import os
import time
import logging
import signal
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit_dependency
from .cost_guard import cost_guard, check_budget_dependency
from utils.mock_llm import ask

# Configure structured JSON logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='{"timestamp":"%(asctime)s", "level":"%(levelname)s", "event":"%(message)s"}'
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info("Agent starting up...")
    # Simulate loading models or connecting to DB/Redis
    time.sleep(0.5) 
    _is_ready = True
    logger.info("Agent is ready!")
    yield
    _is_ready = False
    logger.info("Graceful shutdown initiated (SIGTERM handle)...")
    # Add cleanup logic here
    logger.info("Shutdown complete")

app = FastAPI(title="Production AI Agent", lifespan=lifespan)

@app.get("/health")
def health():
    """Liveness probe"""
    return {
        "status": "ok",
        "uptime": round(time.time() - START_TIME, 2),
        "version": "1.0.0"
    }

@app.get("/ready")
def ready():
    """Readiness probe"""
    if not _is_ready:
        return JSONResponse(status_code=503, content={"status": "not ready"})
    return {"status": "ready", "checks": {"redis": "ok", "llm": "ok"}}

@app.post("/ask")
async def ask_endpoint(
    question: str = Body(..., embed=True),
    user_id: str = Depends(verify_api_key)
):
    """Protected AI Agent endpoint"""
    # Check rate limit and budget
    check_rate_limit_dependency(user_id)
    check_budget_dependency(user_id)
    
    logger.info(f"Processing question from user: {user_id}")
    
    # Call the Mock LLM
    answer = ask(question)
    
    # Record cost (mock value)
    cost_guard.record_cost(user_id, 0.02)
    
    return {
        "user_id": user_id,
        "question": question,
        "answer": answer
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        timeout_graceful_shutdown=30
    )
