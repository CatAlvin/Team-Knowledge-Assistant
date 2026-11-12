"""REST transport over the shared business functions."""
import os
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from workbench_api import router as workbench_router

from common import assistant
from common.llm import llm_provider
from models import (Alerts, Answer, AskRequest, Digest, DigestRequest, Health, Ready,
                    SummarizeRequest, Summary, Tasks)

app = FastAPI(title="Team Knowledge Assistant", version="1.0.0")


@app.middleware("http")
async def authenticate(request: Request, call_next):
    token = os.getenv("SERVICE_API_KEY", "")
    public = request.url.path in {"/healthz", "/"} or request.url.path.startswith("/assets/")
    if token and not public:
        supplied = request.headers.get("authorization", "").encode()
        if not secrets.compare_digest(supplied, f"Bearer {token}".encode()):
            return JSONResponse({"detail": "Unauthorized"}, status_code=401,
                                headers={"WWW-Authenticate": "Bearer"})
    return await call_next(request)


def execute(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Business operation failed") from exc


@app.get("/healthz", response_model=Health)
def healthz():
    return {"status": "ok", "version": app.version}


@app.get("/readyz", response_model=Ready)
def readyz():
    try:
        messages, chunks = len(assistant.load_messages()), len(assistant.kb_index().docs)
        if not messages or not chunks:
            raise ValueError("empty dataset")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Dataset unavailable") from exc
    return {"status": "ready", "messages": messages, "kb_chunks": chunks}


@app.get("/alerts", response_model=Alerts)
def alerts():
    return {"alerts": execute(lambda: assistant.scan_risks(assistant.load_messages()))}


@app.get("/tasks", response_model=Tasks)
def tasks():
    return {"tasks": execute(lambda: assistant.extract_action_items(assistant.load_messages()))}


@app.post("/summarize", response_model=Summary)
def summarize(request: SummarizeRequest):
    def operation():
        return {"channel": request.channel,
                "summary": assistant.summarize_channel(assistant.load_messages(), request.channel),
                "mode": llm_provider()}
    return execute(operation)


@app.post("/ask", response_model=Answer)
def ask(request: AskRequest):
    return execute(assistant.ask_kb, request.question, request.k)


@app.post("/digest", response_model=Digest)
def digest(request: DigestRequest):
    return execute(assistant.run_pipeline, faq_queries=request.faq_queries)


app.include_router(workbench_router)
WEB = Path(__file__).resolve().parent / "web"
app.mount("/assets", StaticFiles(directory=WEB, check_dir=False), name="assets")


@app.get("/", include_in_schema=False)
def workbench():
    return FileResponse(WEB / "index.html")
