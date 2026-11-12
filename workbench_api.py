"""Presentation adapters over the team assistant's business operations."""
import os
from pathlib import Path
from collections import Counter
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

router = APIRouter(prefix="/workspace", tags=["Workbench"])
ROOT = Path(__file__).resolve().parent

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=2000)

    @field_validator("question")
    @classmethod
    def trim(cls, value):
        if len(value.strip()) < 3:
            raise ValueError("Enter at least three characters")
        return value.strip()

class Brief(BaseModel):
    days: int = Field(default=7, ge=1, le=90)

def documents():
    return [{"name": path.name, "title": path.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")}
            for path in sorted((ROOT / "kb").glob("*.md"))]

@router.get("/documents/{name}")
def document(name: str):
    allowed = {item["name"] for item in documents()}
    if name not in allowed:
        raise HTTPException(404, "Document not found")
    return {"name": name, "text": (ROOT / "kb" / name).read_text(encoding="utf-8")}

def projects(kind):
    choices = [{"id": kind, "title": "团队知识助手" if kind == "team" else "Issue 分诊助手", "url": "/"}]
    other = os.getenv("WORKBENCH_OTHER_URL", "")
    if other:
        choices.append({"id": "triage" if kind == "team" else "team",
                        "title": "Issue 分诊助手" if kind == "team" else "团队知识助手", "url": other})
    return choices

import json
from common import assistant, nlp, llm

def message_rows(messages):
    return [{"id": m["id"], "text": m["text"], "title": m["text"].splitlines()[0],
             "author": m["author"], "time": m["sim_ts"], "channel": m["channel"],
             "labels": [], "state": "", "url": ""} for m in messages]

def excerpt_groups(messages):
    output = []
    for channel in ("#incidents", "#product"):
        rows = [m for m in messages if m["channel"] == channel]
        selected = [m for m in rows if any(k in m["text"].lower() for k in nlp.SUMMARY_KEYWORDS)]
        output.append({"title": channel, "count": len(rows),
                       "items": [{"text": m["text"], "id": m["id"]} for m in selected[:8]]})
    return output

@router.get("")
def workspace():
    messages = assistant.load_messages()
    tasks = [t.model_dump(mode="json") for t in nlp.TASKS.validate_json(
        nlp._extract_offline([m for m in messages if m["channel"] in assistant.TASK_CHANNELS]))]
    alerts = assistant.scan_risks(messages)
    return {"kind": "team", "title": "团队知识助手", "records": message_rows(messages),
            "tasks": tasks, "risks": alerts,
            "groups": dict(Counter(m["channel"] for m in messages)),
            "briefs": excerpt_groups(messages), "documents": documents(),
            "period_start": min((m["sim_ts"] for m in messages), default=""),
            "period_end": max((m["sim_ts"] for m in messages), default=""),
            "projects": projects("team")}

@router.post("/brief")
def brief(request: Brief):
    try:
        return assistant.run_pipeline()
    except Exception as exc:
        raise HTTPException(502, "Brief generation failed") from exc

@router.post("/ask")
def ask(request: Ask):
    try:
        result = assistant.ask_kb(request.question)
        if result["mode"] == "mock" and not result["refused"]:
            hits = assistant.kb_index().search(request.question, k=2)
            result["answer"] = hits[0]["text"] if hits else result["answer"]
        return result
    except Exception as exc:
        raise HTTPException(502, "Question processing failed") from exc
