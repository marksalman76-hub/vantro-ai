"""
Standalone chat server for the Vantro site chatbot.
Run with: uvicorn chat_server:app --port 8001 --reload
Install deps: pip install fastapi uvicorn anthropic python-dotenv
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://vantro.ai"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are Vantro's AI assistant on the Vantro.ai website.
Vantro is an AI agent platform that lets businesses deploy autonomous AI agents for ecommerce operations — covering sales, marketing, support, analytics, and more.

Be concise, helpful, and on-brand. Answer questions about:
- What Vantro does and how it works
- Pricing and plans (Starter, Growth, Business, Enterprise)
- The AI agents available (22 specialized agents)
- Integration and setup questions
- Getting started

If asked something outside Vantro's scope, politely redirect to the relevant topic or suggest contacting hello@vantro.ai.
Keep responses short — 2-4 sentences max unless more detail is clearly needed."""


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.post("/chat")
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": m.role, "content": m.content} for m in req.messages],
    )

    return {"content": response.content[0].text}
