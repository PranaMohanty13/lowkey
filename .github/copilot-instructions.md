# Lowkey - AI Coding Instructions

## Architecture Overview

**Lowkey** is a Reddit-powered travel recommendation chat app with a split frontend/backend architecture:

```
frontend/ → Next.js 16 + React 19 + AI SDK (port 3000)
    ↓ HTTP POST /api/chat (streaming)
backend/  → FastAPI + Google Gemini API (port 8000)
```

### Data Flow

1. User sends message via `useChat` hook with `TextStreamChatTransport`
2. Frontend POSTs UIMessage array directly to FastAPI (bypasses Next.js API routes)
3. Backend converts messages to prompt, streams Gemini response
4. Frontend renders streamed text chunks in real-time

## Key Files

| File                                                    | Purpose                                        |
| ------------------------------------------------------- | ---------------------------------------------- |
| [backend/main.py](../backend/main.py)                   | FastAPI app, CORS config, `/api/chat` endpoint |
| [backend/GeminiWorking.py](../backend/GeminiWorking.py) | Gemini client, prompt building, streaming      |
| [frontend/app/page.tsx](../frontend/app/page.tsx)       | Chat UI, `useChat` hook configuration          |

## Developer Workflows

### Running the App

```bash
# Terminal 1: Backend (requires GEMINI_API_KEY in backend/.env)
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Environment Setup

- Backend requires `GEMINI_API_KEY` or `GOOGLE_API_KEY` in `backend/.env`
- CORS is configured for `http://localhost:3000` only

## Project-Specific Patterns

### AI SDK Integration

- Uses `@ai-sdk/react` v3 with `TextStreamChatTransport` (not standard fetch)
- Messages use `UIMessage` shape: `{ id, role, parts: [{type: "text", text: "..."}] }`
- Transport points directly to FastAPI, not a Next.js API route

### Backend Message Handling

- `_extract_text_from_ui_message()` extracts only `type="text"` parts
- Prompt format: `USER: ...\nASSISTANT: ...\nASSISTANT:` (role-prefixed lines)
- Streaming uses `generate_content_stream()` from `google.genai`

### Frontend Conventions

- Tailwind CSS v4 with `@import "tailwindcss"` syntax
- CSS variables for theming (`--background`, `--foreground`)
- Geist font family via Next.js font optimization

## Deployment

- **Frontend**: Deploy to Vercel (Next.js native support)
- **Backend**: Deploy FastAPI separately (Vercel Serverless Functions, Railway, or Render)
- Update CORS origins in `main.py` when deploying to production

## When Extending

- **New message types**: Update `parts` handling in both `GeminiWorking.py` and `page.tsx`
- **New API endpoints**: Add to `main.py`, maintain CORS origins list
- **Model changes**: Update `DEFAULT_MODEL` in `GeminiWorking.py` (currently `gemini-2.5-flash`)
- **Reddit integration**: Planned for future—will add Reddit API calls for travel recommendations
