from typing import List, Literal, Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import llm_client


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class TextPart(BaseModel):
    type: Literal["text"]
    text: str


class UIMessage(BaseModel):
    id: str
    role: Literal["user", "assistant", "system"]
    parts: List[Dict[str, Any]] = Field(default_factory=list)


class ChatRequest(BaseModel):
    messages: List[UIMessage]


@app.get("/")
async def read_root():
    return {"status": "Backend is running", "brain": "Gemini"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    messages_as_dicts = [m.model_dump() for m in req.messages]

    return StreamingResponse(
        llm_client.stream_chat_to_gemini(messages_as_dicts),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
        },
    )
