from pathlib import Path

p = Path("frontend/src/app/api/run-agent/route.ts")
text = p.read_text(encoding="utf-8")

text = text.replace(
    'import { NextRequest, NextResponse } from "next/server";',
    'import { NextRequest, NextResponse } from "next/server";\nimport { mkdir, readFile, writeFile } from "fs/promises";\nimport path from "path";',
    1,
)

text = text.replace(
    'export const dynamic = "force-dynamic";',
    'export const dynamic = "force-dynamic";\nexport const runtime = "nodejs";',
    1,
)

anchor = '''const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";
'''

insert = '''
const DATA_DIR = path.join(process.cwd(), ".runtime-data");
const DATA_FILE = path.join(DATA_DIR, "client-executions.json");

async function persistClientExecution(bodyText: string) {
  try {
    const data = JSON.parse(bodyText);
    if (!data?.success) return;

    const providerContent =
      data?.output?.provider_execution?.generated_content ||
      data?.output?.content ||
      data?.provider_execution?.generated_content ||
      data?.execution?.adapter_result?.output ||
      data?.execution?.adapter_result?.generated_output ||
      data?.output ||
      "";

    const deliverable = {
      title: "Client deliverable",
      summary: data?.safe_client_message || data?.message || "Governed client execution completed.",
      output: typeof providerContent === "string" ? providerContent : JSON.stringify(providerContent, null, 2),
      generated_output: typeof providerContent === "string" ? providerContent : JSON.stringify(providerContent, null, 2),
      content: typeof providerContent === "string" ? providerContent : JSON.stringify(providerContent, null, 2),
      media_pack: data?.media_pack || data?.execution?.adapter_result?.media_pack || {},
      generation_jobs: data?.generation_jobs || data?.execution?.adapter_result?.generation_jobs || [],
      preview_url: data?.preview_url || data?.execution?.adapter_result?.preview_url || "",
      asset_url: data?.asset_url || data?.execution?.adapter_result?.asset_url || "",
      media_url: data?.media_url || data?.execution?.adapter_result?.media_url || "",
      voiceover_script: data?.voiceover_script || data?.execution?.adapter_result?.voiceover_script || "",
      video_prompt: data?.video_prompt || data?.execution?.adapter_result?.video_prompt || "",
      avatar_prompt: data?.avatar_prompt || data?.execution?.adapter_result?.avatar_prompt || "",
      supports_audio: Boolean(data?.supports_audio || data?.execution?.adapter_result?.supports_audio),
      supports_video: Boolean(data?.supports_video || data?.execution?.adapter_result?.supports_video),
      supports_avatar_video: Boolean(data?.supports_avatar_video || data?.execution?.adapter_result?.supports_avatar_video),
      client_safe_learning_summary: data?.client_safe_learning_summary || data?.learning || {},
      created_at: new Date().toISOString(),
      tags: ["Live execution", "Client safe", "Generated output"],
    };

    await mkdir(DATA_DIR, { recursive: true });

    let existing: any[] = [];
    try {
      existing = JSON.parse(await readFile(DATA_FILE, "utf-8"));
      if (!Array.isArray(existing)) existing = [];
    } catch {
      existing = [];
    }

    existing.unshift({
      created_at: new Date().toISOString(),
      execution: data,
      deliverable,
    });

    await writeFile(DATA_FILE, JSON.stringify(existing.slice(0, 50), null, 2), "utf-8");
  } catch {
    // Never block execution response because local persistence failed.
  }
}

'''

if "persistClientExecution" not in text:
    text = text.replace(anchor, anchor + insert, 1)

text = text.replace(
    '''  const body = await res.text();

  return new NextResponse(body, {''',
    '''  const body = await res.text();

  if (req.method === "POST" && path === "/run-agent") {
    await persistClientExecution(body);
  }

  return new NextResponse(body, {''',
    1,
)

p.write_text(text, encoding="utf-8")
print("RUN_AGENT_CLIENT_DELIVERABLE_PERSISTENCE_PATCHED")