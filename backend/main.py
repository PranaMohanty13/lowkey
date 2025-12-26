from typing import List, Literal, Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import GeminiWorking as brain


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request schema (matches AI SDK UIMessage shape at a basic level) ---

class TextPart(BaseModel):
    type: Literal["text"]
    text: str


class UIMessage(BaseModel):
    id: str
    role: Literal["user", "assistant", "system"]
    parts: List[Dict[str, Any]] = Field(default_factory=list)
    # We keep parts as Dict[str, Any] so tool parts won't break validation.
    # We'll only extract type="text" parts in brain.py.


class ChatRequest(BaseModel):
    messages: List[UIMessage]


@app.get("/")
async def read_root():
    return {"status": "Backend is running", "brain": "Gemini"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    # Convert Pydantic models -> plain dicts for brain.py
    messages_as_dicts = [m.model_dump() for m in req.messages]

    return StreamingResponse(
        brain.stream_gemini_from_ui_messages(messages_as_dicts),
        media_type="text/plain; charset=utf-8",
        headers={
            # Helpful for streaming + debugging
            "Cache-Control": "no-cache",
        },
    )
