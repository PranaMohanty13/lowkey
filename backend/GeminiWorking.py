import os
from typing import Iterator, List, Dict, Any, Optional

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY (or GOOGLE_API_KEY) in your environment/.env")

client = genai.Client(api_key=API_KEY)

DEFAULT_MODEL = "gemini-2.5-flash"


def _extract_text_from_ui_message(message: Dict[str, Any]) -> str:
    """
    AI SDK UIMessage = { id, role, parts: [...] }.
    We only use parts of type 'text' for now.
    """
    parts = message.get("parts") or []
    text_chunks: List[str] = []

    for part in parts:
        if isinstance(part, dict) and part.get("type") == "text":
            t = part.get("text")
            if isinstance(t, str) and t.strip():
                text_chunks.append(t)

    return "\n".join(text_chunks).strip()


def build_prompt_from_ui_messages(messages: List[Dict[str, Any]]) -> str:
    """
    Minimal conversation-to-prompt conversion.
    Good enough for a first working pipeline; you can upgrade to a true chat/history format later.
    """
    lines: List[str] = []
    for m in messages:
        role = (m.get("role") or "").strip().lower()
        if role not in ("user", "assistant", "system"):
            continue

        content = _extract_text_from_ui_message(m)
        if not content:
            continue

        if role == "system":
            lines.append(f"SYSTEM: {content}")
        elif role == "user":
            lines.append(f"USER: {content}")
        else:
            lines.append(f"ASSISTANT: {content}")

    # Nudge the model to continue as assistant
    lines.append("ASSISTANT:")
    return "\n".join(lines)


def stream_gemini_from_ui_messages(
    messages: List[Dict[str, Any]],
    model: str = DEFAULT_MODEL,
) -> Iterator[str]:
    prompt = build_prompt_from_ui_messages(messages)

    try:
        stream = client.models.generate_content_stream(
            model=model,
            contents=prompt,
        )

        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text

    except Exception as e:
        # Make the error visible in the client stream while also being debuggable.
        yield f"\n[ERROR] {type(e).__name__}: {e}\n"
