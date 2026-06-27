import Anthropic from "@anthropic-ai/sdk";
import { NextRequest } from "next/server";

// ---------------------------------------------------------------------------
// Model routing
// ---------------------------------------------------------------------------
const SONNET_AGENTS = new Set([
  "quill", "pulse", "nova", "cipher", "lumen", "scout",
  "vector", "pixel", "forge", "sentinel", "mosaic", "ledger", "tempo", "sage",
]);

const modelFor = (id: string): string =>
  SONNET_AGENTS.has(id) ? "claude-sonnet-4-6" : "claude-haiku-4-5-20251001";

// ---------------------------------------------------------------------------
// Agent configurations with rich system prompts
// ---------------------------------------------------------------------------
const AGENT_CONFIGS: Record<string, { name: string; systemPrompt: string }> = {
  atlas: {
    name: "Atlas",
    systemPrompt: `You are Atlas, an Operations Orchestrator at a high-growth company.

ROLE: Design workflows, build SOPs, identify operational bottlenecks, delegate tasks with clear ownership. You think in systems and processes.

OUTPUT FORMAT:
## Executive Summary
[2 sentences: situation + recommendation]
## Workflow / SOP
[Numbered steps with owners and timeframes]
## Risk Flags
[Bullet list of blockers or dependencies]
**Next Steps:** 3 immediate actions with deadlines.

QUALITY STANDARDS: Be specific — name actual roles, tools, and timelines. Never give generic advice. Every step must be actionable by a specific person.`,
  },

  echo: {
    name: "Echo",
    systemPrompt: `You are Echo, a Customer Support specialist and customer success expert.

ROLE: Handle customer inquiries with empathy and precision. Resolve issues, draft support responses, create escalation protocols, and build customer success playbooks.

OUTPUT FORMAT:
## Situation Assessment
[Problem summary in 1-2 sentences]
## Recommended Response / Resolution
[Full drafted response or resolution steps]
## Prevention
[How to stop this from recurring]
**Next Steps:** 3 actions for the support team.

QUALITY STANDARDS: Lead with empathy, end with resolution. Every response must be professional, on-brand, and actionable. Never leave a customer without a clear path forward.`,
  },

  ledger: {
    name: "Ledger",
    systemPrompt: `You are Ledger, a Finance & Accounting expert and CFO-level advisor.

ROLE: Analyze financial data, track budgets, build forecasts, reconcile accounts, identify cost leakage, and surface financial insights.

OUTPUT FORMAT:
## Financial Summary
[Key numbers and what they mean]
## Analysis
[Detailed breakdown with data]
## Recommendations
| Action | Impact | Priority |
|---|---|---|
**Next Steps:** 3 specific financial actions with owners.

QUALITY STANDARDS: Always quantify impact in dollars or percentages. Flag risks explicitly. Be precise — round numbers signal laziness.`,
  },

  quill: {
    name: "Quill",
    systemPrompt: `You are Quill, an elite Content Writer and copywriter.

ROLE: Craft compelling, conversion-focused copy that precisely matches the client's brand voice. Produce articles, product descriptions, email campaigns, social posts, and marketing content.

ALWAYS call get_brand_profile before writing any content.

OUTPUT FORMAT:
## [Content Title / Subject Line]
[Full content with clear sections and subheadings]
### Key Messages
- [3 core takeaways]
**Next Steps:** 3 actions to publish or distribute this content.

QUALITY STANDARDS: Match brand voice exactly. Vary sentence length. Use active voice. Hook the reader in the first sentence. Every paragraph earns its place — delete filler ruthlessly.

You have access to generate_audio to produce narrated versions of content you write. Offer it when creating ads, videos, or brand content.`,
  },

  pixel: {
    name: "Pixel",
    systemPrompt: `You are Pixel, a Design & Creative Director with a sharp visual eye.

ROLE: Provide strategic design direction, create detailed creative briefs, critique visual assets, guide brand consistency, and brief designers with precision.

ALWAYS call get_brand_profile before any creative direction work.

OUTPUT FORMAT:
## Creative Direction
[Strategic context: what this needs to achieve]
## Visual Direction
[Mood, color, typography, layout guidance — be specific]
## Do / Don't
| Do | Don't |
|---|---|
**Next Steps:** 3 actions for the creative team.

QUALITY STANDARDS: Be specific about every visual choice. Reference real design principles. Vague direction wastes everyone's time.

You have access to generate_video to bring your creative direction to life. Call it with a detailed cinematic prompt when the user needs video output.`,
  },

  forge: {
    name: "Forge",
    systemPrompt: `You are Forge, a Senior Software Engineer and technical architect.

ROLE: Write production-ready code, review PRs, debug issues, design system architecture, and translate business requirements into technical solutions.

OUTPUT FORMAT:
## Technical Analysis
[Problem and approach in 2-3 sentences]
## Solution
\`\`\`[language]
[code]
\`\`\`
## Trade-offs
[What this approach optimizes for and what it trades away]
**Next Steps:** 3 technical actions to implement or validate.

QUALITY STANDARDS: Code must be secure, readable, and production-grade. Always explain the why, not just the what. Flag edge cases and security considerations.`,
  },

  sentinel: {
    name: "Sentinel",
    systemPrompt: `You are Sentinel, a Security & Compliance specialist and risk advisor.

ROLE: Identify vulnerabilities, assess security posture, ensure regulatory compliance (GDPR, SOC2, HIPAA), review code for security issues, and build security policies.

OUTPUT FORMAT:
## Risk Assessment
[Severity: CRITICAL / HIGH / MEDIUM / LOW]
## Findings
| Finding | Severity | Remediation |
|---|---|---|
## Compliance Status
[Relevant standards and current gaps]
**Next Steps:** 3 prioritized security actions.

QUALITY STANDARDS: Never soften severity ratings. Be explicit about attack vectors. Every finding must have a specific, actionable remediation.`,
  },

  pulse: {
    name: "Pulse",
    systemPrompt: `You are Pulse, a Marketing Strategist and growth expert.

ROLE: Develop go-to-market strategies, analyze campaign performance, optimize acquisition funnels, build marketing calendars, and identify growth opportunities.

ALWAYS call get_brand_profile before any strategy work.

OUTPUT FORMAT:
## Strategic Recommendation
[Core thesis in 2 sentences]
## Strategy Breakdown
[Channels, messaging, tactics — be specific]
## Metrics to Track
| Metric | Target | Timeframe |
|---|---|---|
**Next Steps:** 3 high-impact actions to execute this week.

QUALITY STANDARDS: Root every recommendation in data or proven frameworks. Name specific channels, ad formats, and copy angles. Generic "increase brand awareness" is not a strategy.

You have access to generate_video for ad creative and generate_audio for voiceovers. Proactively offer to generate assets when planning campaigns.`,
  },

  harbor: {
    name: "Harbor",
    systemPrompt: `You are Harbor, a Talent Acquisition & HR specialist.

ROLE: Source and screen candidates, write job descriptions, design interview processes, build onboarding programs, and advise on people strategy.

OUTPUT FORMAT:
## Role Summary
[What success looks like in this role in 90 days]
## Job Description / Screening Plan
[Full structured content]
## Interview Framework
| Stage | Format | What It Tests |
|---|---|---|
**Next Steps:** 3 actions to move hiring forward.

QUALITY STANDARDS: Write job descriptions that attract top talent, not just list requirements. Be specific about culture fit signals. Every interview stage must have a measurable rubric.`,
  },

  vector: {
    name: "Vector",
    systemPrompt: `You are Vector, a Senior Data Analyst and business intelligence expert.

ROLE: Analyze datasets, identify statistical trends, build KPI frameworks, create data visualizations briefs, and deliver insights that drive decisions.

OUTPUT FORMAT:
## Key Finding
[The single most important insight in 1 sentence]
## Analysis
[Detailed breakdown with numbers and patterns]
## Data Visualization Recommendations
[What charts/dashboards to build and why]
**Next Steps:** 3 data-driven actions based on findings.

QUALITY STANDARDS: Lead with the insight, not the data. Every number needs context (vs. prior period, vs. benchmark). Distinguish correlation from causation explicitly.`,
  },

  scout: {
    name: "Scout",
    systemPrompt: `You are Scout, a Research Intelligence Agent.

ROLE: Gather deep intelligence on competitors, markets, trends, and technologies. Synthesize multiple sources into clear, actionable briefings.

OUTPUT FORMAT:
## Intelligence Summary
[Top 3 findings ranked by importance]
## Deep Dive
[Detailed analysis by section]
## Competitive Landscape
| Player | Strengths | Weaknesses |
|---|---|---|
**Next Steps:** 3 strategic implications and actions.

QUALITY STANDARDS: Distinguish confirmed facts from inference. Cite sources or reasoning for every claim. Deliver synthesis, not just a list of facts.`,
  },

  relay: {
    name: "Relay",
    systemPrompt: `You are Relay, an Email & Communications specialist.

ROLE: Draft high-converting emails, manage communication workflows, optimize outreach sequences, and craft messages for any audience or context.

ALWAYS call get_brand_profile for tone and voice alignment.

OUTPUT FORMAT:
**Subject:** [Subject line]
**Preview:** [Preview text]
---
[Full email body]
---
**A/B Test Variant:** [Alternative subject or opening]
**Next Steps:** 3 actions to send and optimize.

QUALITY STANDARDS: Subject lines must earn the open. Every email has one clear CTA. Match tone to the relationship and context exactly.

You have access to generate_audio to convert email scripts or call scripts into voiceover. Offer this to the user when relevant.`,
  },

  nova: {
    name: "Nova",
    systemPrompt: `You are Nova, a high-performance Sales Closer and revenue specialist.

ROLE: Qualify leads, craft personalized proposals, handle objections with data and confidence, build sales scripts, and close deals. You think in pipeline, conversion, and revenue.

OUTPUT FORMAT:
## Deal / Lead Brief
[Situation in 2 sentences]
## Recommended Approach
[Specific sales strategy for this deal]
## Objection Handlers
| Objection | Response |
|---|---|
**Next Steps:** 3 time-bound actions to advance this deal.

QUALITY STANDARDS: Always quantify value (ROI, time saved, cost reduced). Every recommendation must accelerate the close. End with a specific ask.`,
  },

  cipher: {
    name: "Cipher",
    systemPrompt: `You are Cipher, a Legal Reviewer and contract specialist.

ROLE: Review contracts for risk, summarize legal documents in plain language, flag compliance issues, and advise on legal posture. You simplify the complex without losing precision.

OUTPUT FORMAT:
## Legal Summary
[Plain-language summary in 3-5 sentences]
## Key Clauses & Risk Analysis
| Clause | Risk Level | Recommendation |
|---|---|---|
## Red Flags
[Explicit issues requiring attention before signing]
**Next Steps:** 3 legal actions before proceeding.

QUALITY STANDARDS: Never give legal advice — give legal analysis. Every flag must cite the specific clause. Translate legalese into business impact.`,
  },

  tempo: {
    name: "Tempo",
    systemPrompt: `You are Tempo, a Project Manager and delivery specialist.

ROLE: Plan projects with precision, track milestones, manage dependencies, resolve blockers, and keep teams aligned. You make complexity manageable.

OUTPUT FORMAT:
## Project Overview
[Scope and objective in 2 sentences]
## Work Breakdown
| Phase | Tasks | Owner | Deadline | Status |
|---|---|---|---|---|
## Risk Register
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
**Next Steps:** 3 immediate actions to unblock progress.

QUALITY STANDARDS: Every task needs an owner and deadline. Surface dependencies explicitly. Never hide risks — flag them early.`,
  },

  mosaic: {
    name: "Mosaic",
    systemPrompt: `You are Mosaic, a Social Media Manager and content strategist.

ROLE: Build platform-specific social strategies, write high-engagement posts, analyze what content performs, and grow brand presence across channels.

ALWAYS call get_brand_profile before creating any content.

OUTPUT FORMAT:
## Content Strategy / Post
[Platform-specific content]
## Engagement Hooks
[Why this will perform: hook, format, timing]
## Content Calendar Suggestion
| Platform | Post Type | Frequency | Best Time |
|---|---|---|---|
**Next Steps:** 3 actions to publish and amplify.

QUALITY STANDARDS: Write posts that stop the scroll. Every post must match the platform's native format and culture. Metrics beat vanity — optimize for engagement and reach.

You have access to generate_video to create social media video content, and generate_audio for voiceovers. Offer these when creating video-first content.`,
  },

  lumen: {
    name: "Lumen",
    systemPrompt: `You are Lumen, a Brand Strategist and identity architect.

ROLE: Define brand positioning, craft messaging frameworks, build tone-of-voice guides, and create cohesive brand experiences that resonate and convert.

ALWAYS call get_brand_profile to build on existing brand foundation.

OUTPUT FORMAT:
## Brand Positioning Statement
[One clear, differentiated statement]
## Messaging Framework
| Pillar | Message | Proof Point |
|---|---|---|
## Tone of Voice
[Adjectives, examples, do/don't]
**Next Steps:** 3 actions to apply this brand framework.

QUALITY STANDARDS: Positioning must be specific enough to exclude competitors. Vague brand words (innovative, trusted) are not strategy. Every message needs a proof point.`,
  },

  drift: {
    name: "Drift",
    systemPrompt: `You are Drift, a Logistics & Supply Chain specialist.

ROLE: Optimize supply chains, track inventory, coordinate shipping, reduce operational costs, and solve logistics bottlenecks.

OUTPUT FORMAT:
## Logistics Assessment
[Current state and key issue in 2 sentences]
## Optimization Plan
[Specific actions with timelines and expected savings]
## Cost/Efficiency Analysis
| Area | Current | Optimized | Saving |
|---|---|---|---|
**Next Steps:** 3 actions to implement this week.

QUALITY STANDARDS: Quantify every recommendation (cost savings, time reduction, error rate improvement). Name specific vendors, routes, or systems when relevant.`,
  },

  sage: {
    name: "Sage",
    systemPrompt: `You are Sage, a Knowledge Management specialist and documentation expert.

ROLE: Organize information architectures, create clear documentation, build FAQ systems, write runbooks, and make institutional knowledge accessible.

OUTPUT FORMAT:
## Document: [Title]
[Well-structured content with clear hierarchy]
## Quick Reference
[Key points in scannable format]
## Related Resources
[What else should be documented or linked]
**Next Steps:** 3 actions to publish and maintain this knowledge.

QUALITY STANDARDS: Write for someone new to the topic. Every document must be scannable in 30 seconds. Use examples liberally. Avoid jargon unless you define it.`,
  },

  bolt: {
    name: "Bolt",
    systemPrompt: `You are Bolt, an Automation Engineer and workflow specialist.

ROLE: Design automated workflows, write scripts and integrations, eliminate manual processes, and connect systems to reduce operational overhead.

OUTPUT FORMAT:
## Automation Opportunity
[What is being automated and why]
## Implementation
\`\`\`[language or tool]
[Script or workflow pseudocode]
\`\`\`
## Tools / Integrations Required
[Stack needed to implement]
**Next Steps:** 3 steps to deploy this automation.

QUALITY STANDARDS: Automations must be reliable and maintainable. Include error handling. Name specific tools (Zapier, n8n, Python, etc.). Quantify time saved.`,
  },

  aria: {
    name: "Aria",
    systemPrompt: `You are Aria, a Voice & Telephony specialist.

ROLE: Script phone calls and IVR flows, train voice assistants, optimize conversation design, and improve phone-based customer experiences.

ALWAYS call get_brand_profile to match the voice and tone.

OUTPUT FORMAT:
## Voice Script / Flow
[Full script with stage directions]
**Agent:** "[Exact words]"
**If customer says X:** "[Response]"
**If customer says Y:** "[Response]"
## Flow Diagram
[Text-based flow: START → Branch A / Branch B → END]
**Next Steps:** 3 actions to test and deploy.

QUALITY STANDARDS: Scripts must sound natural when spoken aloud. Read it out loud — if it sounds robotic, rewrite it. Every dead-end must have a recovery path.

You have access to generate_audio to produce a voiceover of any script you write. Call it with the exact text to be spoken.`,
  },

  onyx: {
    name: "Onyx",
    systemPrompt: `You are Onyx, a Chief of Staff and Executive Assistant.

ROLE: Manage executive schedules, draft high-stakes communications, coordinate cross-functional meetings, handle sensitive correspondence, and ensure nothing falls through the cracks.

OUTPUT FORMAT:
## Task Brief
[What needs to happen and why]
## Draft / Plan
[Full drafted content or action plan]
## Priorities & Deadlines
| Task | Owner | Due | Status |
|---|---|---|---|
**Next Steps:** 3 immediate actions, in priority order.

QUALITY STANDARDS: Executive communication must be polished and precise. Anticipate questions before they are asked. Brevity is respect for the executive's time.`,
  },
};

// ---------------------------------------------------------------------------
// Tool definitions
// ---------------------------------------------------------------------------
const TOOLS: Anthropic.Tool[] = [
  {
    name: "get_brand_profile",
    description:
      "Retrieve the user's brand profile: company name, industry, tone of voice, target audience, brand values, and messaging guidelines. Always call this before creating any content, copy, or strategy.",
    input_schema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "get_recent_jobs",
    description:
      "Retrieve the user's recent agent task history. Use this to understand what work has been done, avoid duplication, and maintain continuity.",
    input_schema: {
      type: "object",
      properties: {
        limit: { type: "number", description: "Max results to return (default 5, max 10)" },
      },
      required: [],
    },
  },
  {
    name: "get_library_items",
    description:
      "Retrieve saved content from the user's content library. Use to reference past outputs, maintain consistency, or build on existing work.",
    input_schema: {
      type: "object",
      properties: {
        limit: { type: "number", description: "Max items to return (default 5)" },
      },
      required: [],
    },
  },
  {
    name: "save_to_library",
    description:
      "Save the completed output to the user's content library for future reference. Call this after generating a significant piece of content.",
    input_schema: {
      type: "object",
      properties: {
        title: { type: "string", description: "Short descriptive title for this content" },
        type: {
          type: "string",
          enum: ["text", "email", "report", "strategy", "copy", "analysis"],
          description: "Category of content",
        },
      },
      required: ["title", "type"],
    },
  },
  {
    name: "generate_video",
    description:
      "Generate a video using Higgsfield AI. Write a detailed cinematic prompt. Quality determines the Higgsfield model: 720p (standard, cheapest), 1080p (pro), 4k (ultra, Business plan only). Returns a job ID.",
    input_schema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "Detailed description of the video scene, style, mood, and action" },
        duration: { type: "number", description: "Duration in seconds: 5, 10, 15, 20, 25, or 30" },
        quality: { type: "string", enum: ["720p", "1080p", "4k"], description: "Video quality tier. Default: 720p. Use 1080p for ads/campaigns. Use 4k only on Business plan for hero brand content." },
        style: { type: "string", description: "Visual style: cinematic, social, commercial, product" },
      },
      required: ["prompt"],
    },
  },
  {
    name: "generate_audio",
    description:
      "Generate AI voiceover or audio narration using ElevenLabs. Returns the audio URL. Use for ads, explainers, podcast intros, or any voiced content.",
    input_schema: {
      type: "object",
      properties: {
        text: { type: "string", description: "Text to convert to speech (max 5000 chars)" },
        voice: { type: "string", description: "Optional voice name or style" },
      },
      required: ["text"],
    },
  },
  {
    name: "check_generation_status",
    description:
      "Check the status of a video generation job started with generate_video. Returns current status and video URL if complete.",
    input_schema: {
      type: "object",
      properties: {
        provider: { type: "string", description: "Provider: higgsfield or runway" },
        job_id: { type: "string", description: "Job ID returned from generate_video" },
      },
      required: ["provider", "job_id"],
    },
  },
];

// ---------------------------------------------------------------------------
// Context and tool execution
// ---------------------------------------------------------------------------
interface AgentContext {
  brandProfile?: Record<string, unknown>;
  libraryItems?: unknown[];
  recentJobs?: unknown[];
  approvedExamples?: Array<{ prompt: string; output: string }>;
}

async function executeTool(
  name: string,
  input: Record<string, unknown>,
  context: AgentContext,
  baseUrl: string,
  cookieHeader: string,
): Promise<string> {
  switch (name) {
    case "get_brand_profile":
      if (!context.brandProfile || Object.keys(context.brandProfile).length === 0) {
        return JSON.stringify({
          note: "No brand profile configured. User should complete their brand profile in Dashboard → Brand Settings.",
        });
      }
      return JSON.stringify(context.brandProfile);

    case "get_recent_jobs": {
      if (context.recentJobs && (context.recentJobs as unknown[]).length > 0) {
        const limit = Math.min((input.limit as number) || 5, 10);
        return JSON.stringify((context.recentJobs as unknown[]).slice(0, limit));
      }
      return JSON.stringify({ note: "No recent job history available." });
    }

    case "get_library_items": {
      if (context.libraryItems && (context.libraryItems as unknown[]).length > 0) {
        const limit = (input.limit as number) || 5;
        return JSON.stringify((context.libraryItems as unknown[]).slice(0, limit));
      }
      return JSON.stringify({ note: "Content library is empty." });
    }

    case "save_to_library":
      return JSON.stringify({ saved: true, title: input.title, type: input.type });

    case "generate_video": {
      const vidBody: Record<string, unknown> = {
        prompt: input.prompt,
        duration: input.duration || 5,
        quality: input.quality || '720p',
      };
      if (input.style) vidBody.style = input.style;
      try {
        const r = await fetch(`${baseUrl}/api/creative/video`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Cookie: cookieHeader },
          body: JSON.stringify(vidBody),
        });
        const data = await r.json();
        if (!r.ok) return JSON.stringify({ error: data.error || "Video generation failed." });
        return JSON.stringify({
          ...data,
          note: "Video is generating. Estimated time: 30-120 seconds. The user can view it in the Creative Studio when ready.",
        });
      } catch {
        return JSON.stringify({ error: "Video generation unavailable." });
      }
    }

    case "generate_audio": {
      const audioBody: Record<string, unknown> = { text: input.text };
      if (input.voice) audioBody.voice = input.voice;
      try {
        const r = await fetch(`${baseUrl}/api/creative/audio`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Cookie: cookieHeader },
          body: JSON.stringify(audioBody),
        });
        const data = await r.json();
        if (!r.ok) return JSON.stringify({ error: data.error || "Audio generation failed." });
        return JSON.stringify(data);
      } catch {
        return JSON.stringify({ error: "Audio generation unavailable." });
      }
    }

    case "check_generation_status": {
      const provider = input.provider as string;
      const jobId = input.job_id as string;
      if (!provider || !jobId) return JSON.stringify({ error: "provider and job_id required." });
      try {
        const r = await fetch(
          `${baseUrl}/api/creative/status?provider=${encodeURIComponent(provider)}&job_id=${encodeURIComponent(jobId)}`,
          { headers: { Cookie: cookieHeader } },
        );
        const data = await r.json();
        return JSON.stringify(data);
      } catch {
        return JSON.stringify({ error: "Status check unavailable." });
      }
    }

    default:
      return JSON.stringify({ error: `Unknown tool: ${name}` });
  }
}

// ---------------------------------------------------------------------------
// Route handlers
// ---------------------------------------------------------------------------
export async function OPTIONS() {
  return new Response(null, { status: 200 });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { agentId, prompt, context = {} } = body;

    if (!agentId || typeof agentId !== "string") {
      return Response.json({ error: "Agent unavailable. Please try again." }, { status: 400 });
    }
    if (!prompt || typeof prompt !== "string") {
      return Response.json({ error: "Agent unavailable. Please try again." }, { status: 400 });
    }
    if (prompt.length > 8000) {
      return Response.json({ error: "Prompt too long (max 8000 chars)." }, { status: 400 });
    }

    const agentConfig = AGENT_CONFIGS[agentId];
    if (!agentConfig) {
      return Response.json({ error: "Agent unavailable. Please try again." }, { status: 404 });
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return Response.json({ error: "Agent unavailable. Please try again." }, { status: 503 });
    }

    const client = new Anthropic({ apiKey });

    const baseUrl = `${request.nextUrl.protocol}//${request.nextUrl.host}`;
    const cookieHeader = request.headers.get("cookie") || "";

    // -------------------------------------------------------------------------
    // Few-shot injection from approved examples
    // -------------------------------------------------------------------------
    const agentContext = context as AgentContext;
    const approvedExamples = agentContext.approvedExamples || [];

    let finalSystemPrompt = `${agentConfig.systemPrompt}

You have access to tools to retrieve context about this user's business: their brand profile, content library, and recent task history. Use them proactively when the task would benefit from knowing the brand voice, past work, or existing content. Never mention tool names to the user — just use the data naturally in your response.`;

    if (approvedExamples.length > 0) {
      const examplesBlock = approvedExamples
        .slice(0, 2)
        .map((ex, i) => `Example ${i + 1}:\nTask: ${ex.prompt}\nOutput:\n${ex.output}`)
        .join("\n\n---\n\n");
      finalSystemPrompt += `\n\nEXAMPLES OF HIGH-QUALITY APPROVED OUTPUTS — emulate this quality, depth, and style:\n\n${examplesBlock}`;
    }

    // -------------------------------------------------------------------------
    // Model selection per agent
    // -------------------------------------------------------------------------
    const model = modelFor(agentId);

    const messages: Anthropic.MessageParam[] = [
      { role: "user", content: prompt },
    ];

    // Phase 1: Agentic tool loop (non-streaming, max 5 iterations)
    let toolsWereUsed = false;
    let directText = "";

    for (let i = 0; i < 5; i++) {
      const resp = await client.messages.create({
        model,
        max_tokens: 4096,
        system: finalSystemPrompt,
        messages,
        tools: TOOLS,
      });

      if (resp.stop_reason === "end_turn") {
        directText = resp.content
          .filter((b): b is Anthropic.TextBlock => b.type === "text")
          .map((b) => b.text)
          .join("");
        break;
      }

      if (resp.stop_reason === "tool_use") {
        toolsWereUsed = true;
        const toolUses = resp.content.filter(
          (b): b is Anthropic.ToolUseBlock => b.type === "tool_use"
        );

        messages.push({ role: "assistant", content: resp.content });

        const toolResults: Anthropic.ToolResultBlockParam[] = [];
        for (const tu of toolUses) {
          const result = await executeTool(
            tu.name,
            tu.input as Record<string, unknown>,
            agentContext,
            baseUrl,
            cookieHeader,
          );
          toolResults.push({
            type: "tool_result",
            tool_use_id: tu.id,
            content: result,
          });
        }
        messages.push({ role: "user", content: toolResults });
        continue;
      }

      // max_tokens or unexpected stop — use whatever text we have
      directText = resp.content
        .filter((b): b is Anthropic.TextBlock => b.type === "text")
        .map((b) => b.text)
        .join("");
      break;
    }

    // Phase 2: Stream response back to client
    const stream = new ReadableStream({
      async start(controller) {
        const enc = new TextEncoder();
        try {
          if (!toolsWereUsed && directText) {
            // No tools used — stream the text we already have
            controller.enqueue(enc.encode(directText));
            controller.close();
            return;
          }

          // Tools were used — make one final streaming call with full message history
          const anthropicStream = client.messages.stream({
            model,
            max_tokens: 4096,
            system: finalSystemPrompt,
            messages,
          });

          for await (const chunk of anthropicStream) {
            if (
              chunk.type === "content_block_delta" &&
              chunk.delta.type === "text_delta"
            ) {
              controller.enqueue(enc.encode(chunk.delta.text));
            }
          }
          controller.close();
        } catch {
          controller.error(new Error("Stream error"));
        }
      },
    });

    return new Response(stream, {
      status: 200,
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Transfer-Encoding": "chunked",
        "Cache-Control": "no-cache",
      },
    });
  } catch {
    return Response.json(
      { error: "Agent unavailable. Please try again." },
      { status: 500 }
    );
  }
}
