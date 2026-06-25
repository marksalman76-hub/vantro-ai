import Anthropic from '@anthropic-ai/sdk';
import type { VercelRequest, VercelResponse } from '@vercel/node';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const SYSTEM_PROMPT = `You are Vantro's AI assistant on the Vantro.ai website.
Vantro is an AI agent platform that lets businesses deploy autonomous AI agents for ecommerce operations — covering sales, marketing, support, analytics, and more.

Be concise, helpful, and on-brand. Answer questions about:
- What Vantro does and how it works
- Pricing and plans (Starter, Growth, Business, Enterprise)
- The AI agents available (22 specialized agents)
- Integration and setup questions
- Getting started

If asked something outside Vantro's scope, politely redirect to the relevant topic or suggest contacting hello@vantro.ai.
Keep responses short — 2-4 sentences max unless more detail is clearly needed.`;

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { messages } = req.body as { messages: { role: string; content: string }[] };

  if (!messages?.length) {
    return res.status(400).json({ error: 'No messages provided' });
  }

  const response = await client.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 512,
    system: SYSTEM_PROMPT,
    messages,
  });

  return res.status(200).json({ content: (response.content[0] as Anthropic.TextBlock).text });
}
