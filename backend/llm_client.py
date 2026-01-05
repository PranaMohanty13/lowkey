import os
from typing import Iterator, List, Dict, Any, Optional

from dotenv import load_dotenv
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.llms import ChatMessage
from google.genai import types

load_dotenv()

API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY (or GOOGLE_API_KEY) in your environment/.env")

DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """ROLE & PERSONA
You are "Lowkey," the ultimate Gen Z travel insider and hype-person. You are not a robot; you are the friend in the group chat who always knows the coolest, non-touristy spots. Your vibe is chill, authentic, and genuinely helpful. You hate "tourist traps" and love "hidden gems."

**You travel with your mascot, Momo 🐈‍ (a chaotic but cute cat). Momo is the "Chief Vibe Officer." If a place is top-tier, Momo approves.**

TONE & STYLE GUIDELINES
- Language: Casual, conversational, and fun. Use Gen Z slang naturally (e.g., "no cap," "hits different," "vibe check," "underrated," "gatekeeping"), but don't overdo it to the point of being cringe.
- Emojis: Use them frequently but tastefully to express emotion (✨, 💀, 😭, ✈️, 🤫, 🫠, 🗿, 🧢, 👍, 🔥, ☕, 🤏, 🤥).
- Sentence Structure: Avoid walls of text. Use short punchy sentences, bullet points, and lower case for aesthetic sometimes (if it fits the vibe).
- Personality: You are empathetic. If a user is stressed about planning, hype them up. If they find a cool spot, celebrate with them.

CORE INSTRUCTIONS
1. Source First: Your primary goal is to find information from Google Search and Google Maps.
   - If you find a specific recommendation, credit it!
   - Include specific details (prices, warnings, "must-try" dishes) when available.

2. The "Vibe Check" (Handling Missing Data):
   - If you have good data, say: "Okay, I dug through the threads and found the tea 🍵"
   - If data is limited, be transparent: "Tbh I haven't seen much chatter about this yet, but based on what I know generally..."

3. Formatting the Output:
   - The Hook: Start with a direct, fun reaction.
   - The Meat: Give recommendations in a clear list. **If a spot is elite, give it "Momo's Stamp of Approval" 🐾.**
   - The "Lowkey" Tip: End with a specific, actionable tip (e.g., "Pro tip: Go at sunset for the 'gram 📸").

4. Safety & Ethics:
   - Never recommend illegal activities.
   - If asked for something dangerous, pivot smoothly (e.g., "That sounds a bit sketch, maybe try [Safe Alternative] instead?").
"""

grounding_tool = types.Tool(
    google_search=types.GoogleSearch(),
    google_maps=types.GoogleMaps(),
)

llm = GoogleGenAI(
    model=DEFAULT_MODEL,
    api_key=API_KEY,
    built_in_tool=grounding_tool,
)


def _extract_text_from_ui_message(message: Dict[str, Any]) -> str:
    parts = message.get("parts") or []
    text_chunks: List[str] = []

    for part in parts:
        if isinstance(part, dict) and part.get("type") == "text":
            t = part.get("text")
            if isinstance(t, str) and t.strip():
                text_chunks.append(t)

    return "\n".join(text_chunks).strip()

def _convert_ui_messages_to_chat_messages(
    messages: List[Dict[str, Any]]
) -> List[ChatMessage]:
    chat_messages: List[ChatMessage] = []
    
    chat_messages.append(ChatMessage(role="system", content=SYSTEM_PROMPT))
    
    for m in messages:
        role = (m.get("role") or "").strip().lower()
        if role not in ("user", "assistant"):
            continue
        
        content = _extract_text_from_ui_message(m)
        if not content:
            continue
        
        chat_messages.append(ChatMessage(role=role, content=content))
    
    return chat_messages


def _extract_grounding_sources(raw_response: Dict[str, Any]) -> List[Dict[str, str]]:
    sources: List[Dict[str, str]] = []
    
    # Defensive checks - grounding may be None when not triggered
    if not raw_response:
        return sources
    
    grounding = raw_response.get("grounding_metadata")
    if not grounding:
        return sources
    
    chunks = grounding.get("grounding_chunks") or []
    
    for chunk in chunks:
        if "web" in chunk and chunk["web"]:
            web = chunk["web"]
            sources.append({
                "type": "web",
                "title": web.get("title", "Web Source"),
                "url": web.get("uri", ""),
            })
        
        if "maps" in chunk and chunk["maps"]:
            maps = chunk["maps"]
            sources.append({
                "type": "maps",
                "title": maps.get("title", "Place"),
                "url": maps.get("uri", ""),
            })
    
    return sources


def _format_sources_for_display(sources: List[Dict[str, str]]) -> str:
    if not sources:
        return ""
    
    lines = ["\n\n---\n📍 **Sources:**"]
    seen_titles = set()  # Deduplicate
    
    for source in sources:
        title = source["title"]
        if title in seen_titles:
            continue
        seen_titles.add(title)
        
        icon = "🗺️" if source["type"] == "maps" else "🔗"
        if source["url"]:
            lines.append(f"- {icon} [{title}]({source['url']})")
        else:
            lines.append(f"- {icon} {title}")
    
    return "\n".join(lines)


def stream_chat_to_gemini(
    messages: List[Dict[str, Any]],
    include_sources: bool = True,
) -> Iterator[str]:
    chat_messages = _convert_ui_messages_to_chat_messages(messages)
    
    try:
        response = llm.stream_chat(messages=chat_messages)
        
        full_response = None
        for chunk in response:
            if chunk.delta:
                yield chunk.delta
            full_response = chunk  # for metadata
        
        if include_sources and full_response and hasattr(full_response, "raw"):
            sources = _extract_grounding_sources(full_response.raw)
            source_text = _format_sources_for_display(sources)
            if source_text:
                yield source_text
                
    except Exception as e:
        yield f"\n[ERROR] {type(e).__name__}: {e}\n"

